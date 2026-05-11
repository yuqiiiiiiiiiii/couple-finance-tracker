# 💕 Couple Finance Tracker

一個專為情侶、家人、朋友設計的共同記帳系統，可以管理共同支出、個人收入、分帳比例與每月統計。

---

## ✨ 功能介紹

### 👤 使用者功能
- 註冊
<img width="443" height="398" alt="image" src="https://github.com/user-attachments/assets/827ea56f-f195-41da-b33a-f3e2863b19f0" />

- 登入
<img width="436" height="384" alt="image" src="https://github.com/user-attachments/assets/4f6d96cd-bcef-4304-8b2f-b2266cb5176b" />

- 綁定另一個使用者帳號
<img width="439" height="333" alt="image" src="https://github.com/user-attachments/assets/7022967f-7c08-4be6-99a0-dfff7dd15bb3" />


### 💸 支出管理
- 新增共同/或個人支出
- 記錄付款人
- 自動分帳
- 支援分類（餐飲、交通、娛樂...）
<img width="428" height="627" alt="image" src="https://github.com/user-attachments/assets/bd5d567e-0c1e-4f64-8c6d-257d4635a83e" />
- 查看支出紀錄
<img width="720" height="263" alt="image" src="https://github.com/user-attachments/assets/4f0c0e60-e8da-46b6-8f5e-e1e00ae3931f" />

### 💰 收入管理
- 新增個人收入
<img width="437" height="475" alt="image" src="https://github.com/user-attachments/assets/580006a0-d1b6-4e70-bbe8-9587b1ca6028" />

- 查看收入紀錄
<img width="720" height="303" alt="image" src="https://github.com/user-attachments/assets/826cf02e-8389-4be8-acc3-4f6d04f530a9" />


### 📊 統計功能
- 本月總支出
- 每人支出統計
- 每月花費分析
<img width="267" height="238" alt="image" src="https://github.com/user-attachments/assets/eb266374-3980-4087-924f-75e715ee3c93" />



---

## 🛠 使用技術

### Backend
- Python
- Flask
- SQLAlchemy
- SQLite

### Frontend
- HTML
- CSS
- JavaScript

---

## 📁 專案結構

```bash
project/
│
├── app.py                 # Flask 主程式
├── intance/
    ├── database.db        # SQLite 資料庫
├── templates/             # HTML 頁面
│   ├── login.html
│   ├── register.html
│   └── add.html
│   └── couple_link.html
│   └── index.html
├── requirements.txt
├── .gitignore

