import os
import csv
from telethon import TelegramClient
from flask import Flask, send_file

# 读取环境变量
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
PHONE = os.environ.get("PHONE")  # 你的手机号，用于 Telethon 登录
TARGET_GROUP = os.environ.get("TARGET_GROUP")

# Telethon 客户端
client = TelegramClient("session_name", API_ID, API_HASH)

app = Flask(__name__)

async def export_members():
    """导出群成员"""
    await client.start(PHONE)

    entity = await client.get_entity(TARGET_GROUP)
    members = await client.get_participants(entity, aggressive=True)

    csv_file = "members.csv"
    txt_file = "members.txt"

    with open(csv_file, "w", newline="", encoding="utf-8") as f_csv, \
         open(txt_file, "w", encoding="utf-8") as f_txt:
        writer = csv.writer(f_csv)
        writer.writerow(["Username", "User ID", "Phone"])

        for member in members:
            username = member.username or ""
            user_id = member.id
            phone = member.phone or ""

            writer.writerow([username, user_id, phone])
            f_txt.write(f"{username} | {user_id} | {phone}\n")

    # 保存额外号码
    with open("extra_number.txt", "w", encoding="utf-8") as f_extra:
        f_extra.write("+639999005166\n")

@app.route("/")
def home():
    return """
    <h1>Telegram 群成员导出工具</h1>
    <a href='/run'>立即抓取群成员</a>
    """

@app.route("/run")
def run_export():
    with client:
        client.loop.run_until_complete(export_members())
    return """
    <h3>抓取完成</h3>
    <p><a href='/download/csv'>下载 CSV 文件</a></p>
    <p><a href='/download/txt'>下载 TXT 文件</a></p>
    <p><a href='/download/extra'>下载额外号码</a></p>
    """

@app.route("/download/csv")
def download_csv():
    return send_file("members.csv", as_attachment=True)

@app.route("/download/txt")
def download_txt():
    return send_file("members.txt", as_attachment=True)

@app.route("/download/extra")
def download_extra():
    return send_file("extra_number.txt", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
