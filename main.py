import os
from flask import Flask, request
from telethon import TelegramClient
import asyncio
import csv

API_ID = 25383117
API_HASH = "c12894dabde9aa99cbe181e7ee8ec5b8"
SESSION_NAME = "bot"

app = Flask(__name__)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

loop = asyncio.get_event_loop()

@app.before_first_request
def startup():
    loop.run_until_complete(client.connect())

@app.route("/")
def home():
    return """
    <h3>Telegram 群成员导出</h3>
    <p>第一次使用请先 <a href='/login'>登录</a></p>
    <p>导出群成员: /export?link=群链接</p>
    """

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone")
        loop.run_until_complete(client.connect())
        loop.run_until_complete(client.send_code_request(phone))
        return f"""
        <form method='post' action='/verify'>
            <input type='hidden' name='phone' value='{phone}'>
            验证码: <input name='code'>
            <input type='submit' value='验证'>
        </form>
        """
    return """
    <form method='post'>
        手机号（+区号+号码）: <input name='phone'>
        <input type='submit' value='发送验证码'>
    </form>
    """

@app.route("/verify", methods=["POST"])
def verify():
    phone = request.form.get("phone")
    code = request.form.get("code")
    loop.run_until_complete(client.connect())
    loop.run_until_complete(client.sign_in(phone, code))
    return "✅ 登录成功，session 已保存，可以开始导出群成员"

@app.route("/export")
def export():
    group_link = request.args.get("link")
    if not group_link:
        return "❌ 请提供群链接，如 /export?link=https://t.me/xxx"

    loop.run_until_complete(client.connect())
    if not loop.run_until_complete(client.is_user_authorized()):
        return "❌ 请先访问 /login 登录 Telegram"

    try:
        entity = loop.run_until_complete(client.get_entity(group_link))
        members = loop.run_until_complete(client.get_participants(entity))

        file_path = "/tmp/members.csv"
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Username", "Name"])
            for m in members:
                writer.writerow([
                    m.id,
                    m.username if m.username else "",
                    (m.first_name or "") + " " + (m.last_name or "")
                ])

        return open(file_path, "rb").read(), 200, {
            "Content-Disposition": "attachment; filename=members.csv",
            "Content-Type": "text/csv"
        }
    except Exception as e:
        return f"❌ 出错: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
