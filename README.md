# 💕 Couple Finance Tracker

一個專為情侶、家人、朋友設計的共同記帳系統，可以管理共同支出、個人收入、分帳比例與每月統計。

---

## ✨ 功能介紹

### 👤 使用者功能
- 註冊 / 登入
- 建立情侶關係
- 綁定另一半帳號

### 💸 支出管理
- 新增共同支出
- 記錄付款人
- 自動分帳
- 支援分類（餐飲、交通、娛樂...）

### 💰 收入管理
- 新增個人收入
- 查看收入紀錄

### 📊 統計功能
- 本月總支出
- 每人支出統計
- 每月花費分析

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
├── database.db            # SQLite 資料庫
├── templates/             # HTML 頁面
│   ├── login.html
│   ├── register.html
│   └── bind.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── README.md
