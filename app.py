from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timezone,timedelta
from sqlalchemy import extract
from flask import render_template, redirect, url_for
from flask import session
from sqlalchemy import or_
#密碼加密
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for

app = Flask(__name__)
app.secret_key = "yuqi972"
# 資料庫設定
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# Models
# =========================
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # income / expense
    date = db.Column(db.DateTime, default=datetime.utcnow)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

    couple_id = db.Column(db.Integer)


class Couple(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user1_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    user2_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


class Expense(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    couple_id = db.Column(db.Integer)

    user_id = db.Column(db.Integer)

    amount = db.Column(db.Float)

    category = db.Column(db.String(100))

    description = db.Column(db.String(200))
    record_type = db.Column(db.String(20))
    expense_type = db.Column(db.String(50))
    split_ratio = db.Column(db.Float, default=0.5)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
class Income(db.Model):
    __tablename__ = "incomes"

    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)

    note = db.Column(db.String(200))

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone(timedelta(hours=8)))
    )
# =========================
# Home
# =========================

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if not user:
        return redirect(url_for('login'))

    now = datetime.now()

    # =========================
    # 月統計（支出）
    # =========================
    monthly = {
        "year": now.year,
        "month": now.month,
        "total": 0,
        "per_user": {}
    }

    expenses = []
    incomes = []

    if user.couple_id:

        #支出（本月）
        expenses = Expense.query.filter(
            Expense.couple_id == user.couple_id,
            extract('year', Expense.created_at) == now.year,
            extract('month', Expense.created_at) == now.month
        ).all()

        for e in expenses:
            monthly["total"] += e.amount
            monthly["per_user"][e.user_id] = monthly["per_user"].get(e.user_id, 0) + e.amount

        #收入（全部）
        incomes = Income.query.filter_by(
            couple_id=user.couple_id
        ).all()

    # =========================
    # 情侶結算
    # =========================
    summary = None

    if user.couple_id:
        couple = Couple.query.get(user.couple_id)

        if couple:
            balances = {couple.user1_id: 0, couple.user2_id: 0}

            shared_expenses = Expense.query.filter_by(
                couple_id=user.couple_id,
                expense_type="shared"
            ).all()

            for e in shared_expenses:
                payer = e.user_id
                amount = e.amount
                ratio = e.split_ratio or 0.5

                payer_should = amount * ratio
                other_should = amount * (1 - ratio)

                if payer == couple.user1_id:
                    other = couple.user2_id
                else:
                    other = couple.user1_id

                balances[payer] += amount - payer_should
                balances[other] -= other_should

            u1, u2 = couple.user1_id, couple.user2_id

            if balances[u1] > 0:
                summary = f"User {u2} 欠 User {u1} {abs(balances[u1])} 元"
            elif balances[u1] < 0:
                summary = f"User {u1} 欠 User {u2} {abs(balances[u1])} 元"
            else:
                summary = "雙方已平衡"

    # =========================
    # 收入統計（給 balance 用）
    # =========================
    total_income = sum(i.amount for i in incomes) if incomes else 0
    balance = total_income - monthly["total"]

    # =========================
    # 回傳給前端
    # =========================
    return render_template(
        "index.html",
        username=user.name,
        user_id=user.id,
        couple_id=user.couple_id,
        monthly=monthly,
        summary=summary,
        expenses=expenses,
        incomes=incomes,
        total_income=total_income,
        balance=balance
    )
def home():
    
    income = Record.query.filter_by(type="income").all()
    total_income = sum(item.amount for item in income)

    expense = Record.query.filter_by(type="expense").all()
    total_expense = sum(item.amount for item in expense)

    balance = total_income - total_expense

    return render_template(
        'index.html',
        total_income=total_income,
        total_expense=total_expense,
        balance=balance
    )

@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/delete/<int:expense_id>')
def delete(expense_id):
    expense = Expense.query.get(expense_id)

    if not expense:
        return jsonify({
            "message": "找不到這筆帳單"
        }), 404

    db.session.delete(expense)
    db.session.commit()

    return redirect(url_for('index'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None    

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['couple_id'] = user.couple_id
            return redirect(url_for('index'))

        error = "帳號或密碼錯誤"
    
    return render_template('login.html', error=error)

@app.route('/register-page', methods=['GET', 'POST'])
def register_page():
    error = None

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()

        


        if existing_user:
            error = "Email 已存在"
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(
                    name=name,
                    email=email,
                    password=hashed_password
            )

            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route("/couple-link-page")
def couple_link_page():
    return render_template("couple_link.html")


@app.route("/logout")
def logout():
    session.clear()  #清掉 user_id / couple_id / user_name
    return redirect(url_for("login"))

# =========================
# Register
# =========================

@app.route("/register", methods=["POST"])
def register():

    data = request.json

    if not data:
        return jsonify({
            "message": "請提供資料"
        }), 400

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({
            "message": "name 和 email 必填"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "message": "Email 已存在"
        }), 400

    new_user = User(
        name=name,
        email=email
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "註冊成功",
        "user_id": new_user.id
    })


# =========================
# Get Users
# =========================

@app.route("/users", methods=["GET"])
def get_users():

    users = User.query.all()

    result = []

    for user in users:

        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "couple_id": user.couple_id
        })

    return jsonify(result)


# =========================
# Delete User
# =========================

@app.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "找不到使用者"
        }), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": "刪除成功"
    })


# =========================
# Update User
# =========================

@app.route("/user/<int:user_id>", methods=["PUT"])
def update_user(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "找不到使用者"
        }), 404

    data = request.json

    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)

    db.session.commit()

    return jsonify({
        "message": "更新成功",
        "id": user.id,
        "name": user.name,
        "email": user.email
    })


# =========================
# Create Couple
# =========================

@app.route("/couple/create", methods=["POST"])
def create_couple():

    data = request.json

    user1_id = data.get("user1_id")
    user2_id = data.get("user2_id")

    user1 = User.query.get(user1_id)
    user2 = User.query.get(user2_id)

    if not user1 or not user2:
        return jsonify({
            "message": "user 不存在"
        }), 404
    if user1.couple_id or user2.couple_id:
        return jsonify({
            "message": "其中一位使用者已經配對過"
        }), 400
    couple = Couple(
        user1_id=user1_id,
        user2_id=user2_id
    )

    db.session.add(couple)
    db.session.commit()
    
    user1.couple_id = couple.id
    user2.couple_id = couple.id
    
    db.session.commit()
    session['couple_id'] = couple.id
    return jsonify({
        "message": "配對成功",
        "couple_id": couple.id
    })






# =========================
# Create Expense
# =========================

@app.route("/expenses", methods=["POST"])
def create_expense():

    data = request.form

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"message": "尚未登入"}), 401

    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "找不到 user"}), 404

    if not user.couple_id:
        return jsonify({"message": "尚未綁定情侶"}), 400

    new_expense = Expense(
        couple_id=user.couple_id,
        user_id=user.id,
        amount=data.get("amount"),
        category=data.get("category"),
        description=data.get("description"),
        expense_type=data.get("expense_type"),
        split_ratio=float(data.get("split_ratio", 0.5)) 
 )

    db.session.add(new_expense)
    db.session.commit()

    return jsonify({"message": "新增支出成功"})

# =========================
# Get Expenses
# =========================

@app.route("/expenses", methods=["GET"])
def get_expenses():

    user_id = session.get("user_id")
    
    if not user_id:
        user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"message": "缺 user_id"}), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify([])

    if not user.couple_id:
        expenses = Expense.query.filter_by(user_id=user_id).all()
    else:
        expenses = Expense.query.filter(
            or_(
                Expense.user_id == user_id,
                Expense.couple_id == user.couple_id
            )
        ).all()

    return jsonify([
        {
            "id": e.id,
            "amount": e.amount,
            "category": e.category,
            "expense_type": e.expense_type,
            "couple_id": e.couple_id
        }
        for e in expenses
    ])
# =========================
# Create Income
# =========================    
@app.route("/income", methods=["POST"])
def add_income():

    data = request.form

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"message": "尚未登入"}), 401

    user = User.query.get(user_id)

    new_income = Income(
        couple_id=user.couple_id,
        user_id=user.id,
        amount=data.get("amount"),
        category=data.get("category"),
        note=data.get("note", "")
    )

    db.session.add(new_income)
    db.session.commit()

    return jsonify({
        "message": "收入新增成功",
        "income_id": new_income.id
    })
# =========================
# Get Income
# =========================

@app.route("/income/<int:couple_id>", methods=["GET"])
def get_income(couple_id):

    incomes = Income.query.filter_by(couple_id=couple_id).all()

    result = []

    for income in incomes:
        result.append({
            "id": income.id,
            "user_id": income.user_id,
            "amount": income.amount,
            "category": income.category,
            "note": income.note,
            "created_at": income.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(result), 200
# =========================
# Expense Summary
# =========================

@app.route("/expenses/summary/<int:couple_id>", methods=["GET"])
def expense_summary(couple_id):

    couple = Couple.query.get(couple_id)

    if not couple:
        return jsonify({"message": "找不到 couple"}), 404

    expenses = Expense.query.filter_by(
        couple_id=couple_id,
        expense_type="shared"
    ).all()

    balances = {
        couple.user1_id: 0,
        couple.user2_id: 0
    }

    for expense in expenses:
    
        payer = int(expense.user_id)
        amount = expense.amount
        ratio = expense.split_ratio or 0.5

        payer_should_pay = amount * ratio
        other_should_pay = amount * (1 - ratio)

        if payer == couple.user1_id:
            other_user = couple.user2_id
        else:
            other_user = couple.user1_id

    #淨額計算
        balances[payer] += amount - payer_should_pay
        balances[other_user] -= other_should_pay

    u1 = couple.user1_id
    u2 = couple.user2_id


    if balances[u1] > 0:
        summary = f"User {u2} 欠 User {u1} {-balances[u2]} 元"
    elif balances[u1] < 0:
        summary = f"User {u1} 欠 User {u2} {-balances[u1]} 元"
    else:
        summary = "雙方已平衡"
        
    return jsonify({
        "balances": balances,
        "summary": summary
    })
@app.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):

    expense = Expense.query.get(expense_id)

    if not expense:
        return jsonify({
            "message": "找不到這筆帳單"
        }), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({
        "message": "刪除成功",
        "deleted_id": expense_id
    })
@app.route("/income/<int:income_id>", methods=["DELETE"])
def delete_income(income_id):

    income = Income.query.get(income_id)

    if not income:
        return jsonify({"message": "找不到這筆收入"}), 404

    db.session.delete(income)
    db.session.commit()

    return jsonify({
        "message": "收入刪除成功",
        "deleted_id": income_id
    })
# =========================
#更新帳單（PUT）
# =========================
@app.route("/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):

    expense = Expense.query.get(expense_id)

    if not expense:
        return jsonify({
            "message": "找不到這筆帳單"
        }), 404

    data = request.json

    #更新欄位（有傳才改，沒傳就維持原本）
    expense.amount = data.get("amount", expense.amount)
    expense.category = data.get("category", expense.category)
    expense.description = data.get("description", expense.description)
    expense.expense_type = data.get("expense_type", expense.expense_type)

    db.session.commit()

    return jsonify({
        "message": "更新成功",
        "id": expense.id,
        "amount": expense.amount,
        "category": expense.category,
        "description": expense.description,
        "expense_type": expense.expense_type
    })
#月度統計
@app.route("/expenses/monthly/<int:couple_id>", methods=["GET"])
def monthly_summary(couple_id):


    now = datetime.now()

    expenses = Expense.query.filter(
        Expense.couple_id == couple_id,
        extract('year', Expense.created_at) == now.year,
        extract('month', Expense.created_at) == now.month
    ).all()
    total = 0
    per_user = {}

    for e in expenses:
        total += e.amount

        per_user[e.user_id] = per_user.get(e.user_id, 0) + e.amount

    return jsonify({
        "year": now.year,
        "month": now.month,
        "total": total,
        "per_user": per_user
    })
#收入的post
#==========================
# Main
# =========================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=10000)
