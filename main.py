import os
import csv
from flask import Flask, request, render_template_string, send_file
from telethon import TelegramClient
import asyncio

# ==== 你的 Telegram API 信息 ====
API_ID = 25383117
API_HASH = "c12894dabde9aa99cbe181e7ee8ec5b8"
SESSION_NAME = "session"

# ==== Flask 初始化 ====
app = Flask(__name__)

# ==== Telethon 客户端（全局一个）====
loop = asyncio.get_event_loop()
client = TelegramClient(SESSION_NAME, API_ID, API_HASH, loop=loop)


# ==== 首页（输入手机号）====
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        phone = request.form["phone"]
        loop.run_until_complete(client.connect())
        loop.run_until_complete(client.send_code_request(phone))
        return render_template_string('''
            <h2>验证码已发送到 Telegram</h2>
            <form method="post" action="/verify">
                <input type="hidden" name="phone" value="{{phone}}">
                <label>验证码:</label>
                <input type="text" name="code" required>
                <button type="submit">验证</button>
            </form>
        ''', phone=phone)
    return '''
        <h2>Telegram 登录</h2>
        <form method="post">
            <label>手机号 (包含区号，例如 +85512345678):</label>
            <input type="text" name="phone" required>
            <button type="submit">发送验证码</button>
        </form>
    '''


# ==== 验证验证码 ====
@app.route("/verify", methods=["POST"])
def verify():
    phone = request.form["phone"]
    code = request.form["code"]
    loop.run_until_complete(client.sign_in(phone=phone, code=code))
    return '''
        <h2>✅ 登录成功！</h2>
        <a href="/groups">获取群列表</a>
    '''


# ==== 获取群列表 ====
@app.route("/groups")
def groups():
    loop.run_until_complete(client.connect())
    dialogs = loop.run_until_complete(client.get_dialogs())
    groups = [d for d in dialogs if d.is_group]

    html = "<h2>选择一个群导出成员</h2>"
    for g in groups:
        html += f'<p>{g.name} - <a href="/export/{g.id}">导出</a></p>'
    return html


# ==== 导出群成员 ====
@app.route("/export/<int:group_id>")
def export(group_id):
    loop.run_until_complete(client.connect())
    dialogs = loop.run_until_complete(client.get_dialogs())
    target_group = None
    for d in dialogs:
        if d.id == group_id:
            target_group = d
            break

    if not target_group:
        return "❌ 未找到该群"

    members = loop.run_until_complete(client.get_participants(target_group))
    file_path = "members.csv"
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["User ID", "Username", "First Name", "Last Name"])
        for m in members:
            writer.writerow([
                m.id,
                m.username or "",
                m.first_name or "",
                m.last_name or ""
            ])

    return send_file(file_path, as_attachment=True)


# ==== Render 运行入口 ====
if __name__ == "__main__":
    loop.run_until_complete(client.connect())
    app.run(host="0.0.0.0", port=10000)
