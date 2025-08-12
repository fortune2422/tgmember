import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, time
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.channels import InviteToChannelRequest

# 固定信息
api_id = int(os.getenv("API_ID", "25383117"))
api_hash = os.getenv("API_HASH", "c12894dabde9aa99cbe181e7ee8ec5b8")
phone = os.getenv("PHONE", "+639157681213")

target_group = "aposta10grupo"   # 目标群
my_group = "jili707group"        # 你自己的群
pulled_users_file = "pulled_users.txt"

client = TelegramClient('session', api_id, api_hash)

# ================= HTTP 保活服务器 =================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Service is running.")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("", port), SimpleHandler)
    server.serve_forever()

# 在单独线程运行 HTTP 服务
threading.Thread(target=run_server, daemon=True).start()

# ================= 辅助函数 =================
def load_pulled_users():
    if os.path.exists(pulled_users_file):
        with open(pulled_users_file, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_pulled_users(users):
    with open(pulled_users_file, "a") as f:
        for u in users:
            f.write(u + "\n")

# ================= 拉人逻辑 =================
async def pull_members():
    pulled_users = load_pulled_users()
    print(f"[{datetime.now()}] 开始拉人任务...")

    try:
        group = await client.get_entity(target_group)
        my_group_entity = await client.get_entity(my_group)
        members = await client.get_participants(group)

        new_users = []
        for user in members:
            if user.bot or not user.username:
                continue
            if user.username in pulled_users:
                continue
            new_users.append(user)

        print(f"[{datetime.now()}] 找到 {len(new_users)} 个新用户")

        if not new_users:
            return

        # 加到通讯录
        contacts = []
        for u in new_users:
            if u.phone:
                contacts.append(InputPhoneContact(client_id=0, phone=u.phone, first_name=u.first_name or "User", last_name=u.last_name or ""))
        if contacts:
            await client(ImportContactsRequest(contacts))
            print(f"[{datetime.now()}] 已添加 {len(contacts)} 人到通讯录")

        # 拉进群
        batch_size = 5
        invited_usernames = []
        for i in range(0, len(new_users), batch_size):
            batch = new_users[i:i+batch_size]
            try:
                await client(InviteToChannelRequest(my_group_entity, batch))
                for u in batch:
                    invited_usernames.append(u.username)
                print(f"[{datetime.now()}] 成功拉 {len(batch)} 人")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"拉人出错: {e}")
                await asyncio.sleep(10)

        # 保存已拉过的
        save_pulled_users(invited_usernames)

    except Exception as e:
        print(f"任务执行出错: {e}")

# ================= 调度器 =================
async def scheduler():
    while True:
        now = datetime.now().time()
        target_time = time(1, 0)  # 每天凌晨 1 点
        if now.hour == target_time.hour and now.minute == target_time.minute:
            await pull_members()
            await asyncio.sleep(60)  # 防止重复执行
        await asyncio.sleep(10)
        print(f"[{datetime.now()}] 心跳中...")

# ================= 主入口 =================
async def main():
    await client.start(phone=phone)
    print("已登录 Telegram")
    await scheduler()

if __name__ == "__main__":
    asyncio.run(main())
