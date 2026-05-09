from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timezone,timedelta
from sqlalchemy import extract
app = Flask(__name__)

# 資料庫設定
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# Models
# =========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)

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

    expense_type = db.Column(db.String(50))
    split_ratio = db.Column(db.Float, default=0.5)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

# =========================
# Home
# =========================

@app.route("/")
def home():
    return "Hello Couple Finance Tracker!"


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

    couple = Couple(
        user1_id=user1_id,
        user2_id=user2_id
    )

    db.session.add(couple)
    db.session.commit()

    return jsonify({
        "message": "配對成功",
        "couple_id": couple.id
    })


# =========================
# Link Couple
# =========================

@app.route("/couple/link", methods=["POST"])
def link_couple():

    data = request.json

    couple_id = data.get("couple_id")

    user1_id = data.get("user1_id")
    user2_id = data.get("user2_id")

    couple = Couple.query.get(couple_id)

    if not couple:
        return jsonify({
            "message": "找不到 couple"
        }), 404

    user1 = User.query.get(user1_id)
    user2 = User.query.get(user2_id)

    if not user1 or not user2:
        return jsonify({
            "message": "user 不存在"
        }), 404

    user1.couple_id = couple_id
    user2.couple_id = couple_id

    db.session.commit()

    return jsonify({
        "message": "綁定成功"
    })


# =========================
# Create Expense
# =========================

@app.route("/expenses", methods=["POST"])
def create_expense():

    data = request.json

    couple_id = data.get("couple_id")
    user_id = data.get("user_id")

    couple = Couple.query.get(couple_id)

    if not couple:
        return jsonify({
            "message": "找不到 couple"
        }), 404

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "找不到 user"
        }), 404

    new_expense = Expense(
        couple_id=couple_id,
        user_id=user_id,
        amount=data.get("amount"),
        category=data.get("category"),
        description=data.get("description"),
        expense_type=data.get("expense_type"),
        split_ratio=data.get("split_ratio", 0.5)
    )

    db.session.add(new_expense)
    db.session.commit()

    return jsonify({
        "message": "新增支出成功"
    })


# =========================
# Get Expenses
# =========================

@app.route("/expenses", methods=["GET"])
def get_expenses():

    expenses = Expense.query.all()
    
    result = []

    for expense in expenses:
        if expense.created_at:
            tw_time = expense.created_at.astimezone(
            timezone(timedelta(hours=8))
            )
            time_str = tw_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = None

        result.append({
            "id": expense.id,
            "couple_id": expense.couple_id,
            "user_id": expense.user_id,
            "amount": expense.amount,
            "category": expense.category,
            "description": expense.description,
            "expense_type": expense.expense_type,
            "created_at": time_str
        })

    return jsonify(result)


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

    # 💡 淨額計算（關鍵）
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

    # ✏️ 更新欄位（有傳才改，沒傳就維持原本）
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
# =========================
# Main
# =========================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )