import os
import csv
from flask import Flask, send_file, request
from telethon import TelegramClient

# 从环境变量读取配置
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 创建 Telethon 客户端（使用 Bot Token，无需交互）
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Telegram 群成员导出机器人已运行"

@app.route('/export', methods=['GET'])
async def export_members():
    chat_id = request.args.get('chat_id')
    if not chat_id:
        return "❌ 请在 URL 中加上 chat_id 参数", 400

    try:
        members = []
        async for member in client.iter_participants(chat_id):
            members.append([member.id, member.username or "", member.first_name or "", member.last_name or ""])

        # 保存为 CSV
        file_path = "/tmp/members.csv"
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["User ID", "Username", "First Name", "Last Name"])
            writer.writerows(members)

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"❌ 错误: {str(e)}", 500

if __name__ == '__main__':
    import threading

    # 在后台线程运行 Telegram bot
    def run_bot():
        client.run_until_disconnected()

    threading.Thread(target=run_bot).start()

    # 启动 Flask
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
