import os
from flask import Flask, request, render_template_string, send_file
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import csv
import asyncio

API_ID = 25383117
API_HASH = "c12894dabde9aa99cbe181e7ee8ec5b8"

# 存储会话
SESSION_FILE = "anon"
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

app = Flask(__name__)

# 简单的 HTML 模板
login_page = """
<h2>Telegram 登录</h2>
<form method="post" action="/send_code">
  手机号（带国家码，如 +85512345678）:<br>
  <input type="text" name="phone"><br><br>
  <button type="submit">发送验证码</button>
</form>
"""

verify_page = """
<h2>输入验证码</h2>
<form method="post" action="/verify">
  验证码（Telegram 发来的 5 位数字）:<br>
  <input type="text" name="code"><br><br>
  如果开启了两步验证，请输入密码（否则留空）:<br>
  <input type="password" name="password"><br><br>
  <button type="submit">验证登录</button>
</form>
"""

group_page = """
<h2>获取群成员</h2>
<form method="post" action="/export">
  群链接或群 ID:<br>
  <input type="text" name="group"><br><br>
  <button type="submit">导出成员</button>
</form>
"""

@app.route("/", methods=["GET"])
def index():
    return login_page

@app.route("/send_code", methods=["POST"])
def send_code():
    phone = request.form["phone"]

    async def _send():
        await client.connect()
        await client.send_code_request(phone)
        client.storage.set("phone", phone)
    asyncio.run(_send())

    return verify_page

@app.route("/verify", methods=["POST"])
def verify():
    code = request.form["code"]
    password = request.form.get("password", "")
    phone = client.storage.get("phone")

    async def _verify():
        await client.connect()
        try:
            await client.sign_in(phone=phone, code=code)
        except SessionPasswordNeededError:
            if not password:
                return False, "需要两步验证密码，但你没输入"
            await client.sign_in(password=password)
        return True, None

    success, err = asyncio.run(_verify())
    if not success:
        return f"<p>登录失败：{err}</p>" + verify_page

    return "<p>✅ 登录成功！</p>" + group_page

@app.route("/export", methods=["POST"])
def export():
    group_input = request.form["group"]

    async def _export():
        await client.connect()
        entity = await client.get_entity(group_input)
        members = await client.get_participants(entity)

        file_path = "members.csv"
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "username", "first_name", "last_name"])
            for m in members:
                writer.writerow([m.id, m.username, m.first_name, m.last_name])
        return file_path

    file_path = asyncio.run(_export())
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    client.start()
    app.run(host="0.0.0.0", port=5000)
