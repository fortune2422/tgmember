from flask import Flask, request, jsonify, send_file
from telethon import TelegramClient
import os
import csv
import asyncio
import traceback

api_id = 25383117
api_hash = "c12894dabde9aa99cbe181e7ee8ec5b8"
phone = "+639999005166"
group_link = "https://t.me/oficial9fbetbr"

app = Flask(__name__)
client = TelegramClient("session_name", api_id, api_hash)

@app.errorhandler(Exception)
def handle_exception(e):
    error_details = traceback.format_exc()
    print("❌ 发生错误：\n", error_details)
    return f"<h3>服务器错误：</h3><pre>{error_details}</pre>", 500

@app.route("/")
def home():
    return "✅ Telegram Exporter Running"

@app.route("/login")
def login():
    async def do_login():
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            return "验证码已发送到 Telegram"
        return "已登录，无需再次获取验证码"

    return asyncio.run(do_login())

@app.route("/verify")
def verify():
    code = request.args.get("code")
    if not code:
        return "请在 URL 中加上验证码参数，例如 /verify?code=12345"

    async def do_verify():
        await client.connect()
        try:
            await client.sign_in(phone, code)
            return "✅ 登录成功！现在可以访问 /export 导出成员"
        except Exception as e:
            return f"❌ 登录失败: {e}"

    return asyncio.run(do_verify())

@app.route("/export")
def export():
    async def do_export():
        await client.connect()
        if not await client.is_user_authorized():
            return "❌ 请先 /login 并 /verify 完成登录"

        group = await client.get_entity(group_link)
        members = await client.get_participants(group)

        file_path = "/tmp/members.csv"
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["用户名", "ID", "电话"])
            for m in members:
                username = m.username or ""
                user_id = m.id
                phone_number = getattr(m, "phone", "")
                writer.writerow([username, user_id, phone_number])

        return jsonify({
            "status": "✅ 成功导出",
            "count": len(members),
            "download": "/download"
        })

    return asyncio.run(do_export())

@app.route("/download")
def download():
    file_path = "/tmp/members.csv"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "没有找到导出文件"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
