import os
import asyncio
from flask import Flask, request, render_template_string, redirect, url_for
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# ===== 配置信息 =====
API_ID = int(os.getenv("API_ID", "25383117"))
API_HASH = os.getenv("API_HASH", "c12894dabde9aa99cbe181e7ee8ec5b8")
SESSION_NAME = "tg_session"

app = Flask(__name__)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# 全局变量保存当前手机号
phone_number = None

# 登录页面模板
login_page = """
<h2>Telegram 登录</h2>
<form method="POST">
    <label>手机号（带+区号）：</label><br>
    <input type="text" name="phone" required><br><br>
    <input type="submit" value="获取验证码">
</form>
"""

# 验证码页面模板
code_page = """
<h2>输入验证码</h2>
<form method="POST">
    <label>验证码：</label><br>
    <input type="text" name="code" required><br><br>
    <input type="submit" value="登录">
</form>
"""

@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
async def login():
    global phone_number
    if request.method == "POST":
        phone_number = request.form["phone"]
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
        return render_template_string(code_page)
    return render_template_string(login_page)

@app.route("/verify", methods=["POST"])
async def verify():
    code = request.form["code"]
    await client.connect()
    try:
        await client.sign_in(phone_number, code)
    except SessionPasswordNeededError:
        return "需要两步验证密码（暂未实现）"
    return "✅ 登录成功！你现在可以获取群成员信息了。"

if __name__ == "__main__":
    # Render 需要监听 0.0.0.0:10000 端口
    port = int(os.environ.get("PORT", 10000))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.connect())
    app.run(host="0.0.0.0", port=port)
