import os
import csv
from flask import Flask, request, render_template_string, redirect, url_for, send_file
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# ===== 配置信息 =====
API_ID = int(os.getenv("API_ID", "25383117"))
API_HASH = os.getenv("API_HASH", "c12894dabde9aa99cbe181e7ee8ec5b8")
SESSION_NAME = "tg_session"

app = Flask(__name__)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

phone_number = None  # 保存当前手机号

# 登录页面
login_page = """
<h2>Telegram 登录</h2>
<form method="POST">
    <label>手机号（带+区号）：</label><br>
    <input type="text" name="phone" required><br><br>
    <input type="submit" value="获取验证码">
</form>
"""

# 验证码页面
code_page = """
<h2>输入验证码</h2>
<form method="POST" action="/verify">
    <label>验证码：</label><br>
    <input type="text" name="code" required><br><br>
    <input type="submit" value="登录">
</form>
"""

# 导出页面
export_page = """
<h2>导出群成员</h2>
<form method="POST" action="/export">
    <label>群名或群 ID：</label><br>
    <input type="text" name="group" required><br><br>
    <input type="submit" value="导出 CSV">
</form>
"""

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    global phone_number
    if request.method == "POST":
        phone_number = request.form["phone"]
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone_number)
        return render_template_string(code_page)
    return render_template_string(login_page)

@app.route("/verify", methods=["POST"])
def verify():
    global phone_number
    code = request.form["code"]
    client.connect()
    try:
        client.sign_in(phone_number, code)
    except SessionPasswordNeededError:
        return "需要两步验证密码（暂未实现）"
    return render_template_string(export_page)

@app.route("/export", methods=["POST"])
def export_members():
    try:
        group_name = request.form.get("group", "").strip()
        if not group_name:
            return "❌ 缺少 group 参数", 400

        # 确保 Telethon 已连接
        if not client.is_connected():
            client.connect()

        dialogs = client.get_dialogs()

        # 查找群
        target_group = None
        for dialog in dialogs:
            if dialog.is_group and (group_name.lower() in dialog.name.lower() or str(dialog.id) == group_name):
                target_group = dialog
                break

        if not target_group:
            return f"❌ 未找到该群: {group_name}", 404

        # 获取成员（Telethon get_participants 是异步）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        members = loop.run_until_complete(client.get_participants(target_group))

        # 保存到 CSV
        file_path = "members.csv"
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["User ID", "Username", "First Name", "Last Name"])
            for member in members:
                writer.writerow([
                    member.id,
                    member.username or "",
                    member.first_name or "",
                    member.last_name or ""
                ])

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        # 打印错误到 Render Logs
        traceback.print_exc()
        return f"❌ 出错了: {str(e)}", 500
        
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    client.connect()
    app.run(host="0.0.0.0", port=port)
