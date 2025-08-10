import os
import asyncio
from telethon import TelegramClient
from datetime import datetime

# 从环境变量读取（Render 安全存储）
api_id = int(os.getenv("API_ID", "25383117"))
api_hash = os.getenv("API_HASH", "c12894dabde9aa99cbe181e7ee8ec5b8")
phone = os.getenv("PHONE", "+639157681213")  # 你的手机号（带区号）
target_group = os.getenv("TARGET_GROUP", "aposta10grupo")  # 群用户名
invite_link = os.getenv("INVITE_LINK", "https://t.me/jili707group")  # 你的群链接

client = TelegramClient('session', api_id, api_hash)

async def main():
    await client.start(phone=phone)
    group = await client.get_entity(target_group)

    print(f"[{datetime.now()}] 获取 {group.title} 成员列表...")
    members = await client.get_participants(group)
    print(f"[{datetime.now()}] 共找到 {len(members)} 个成员")

    count = 0
    for user in members:
        if user.bot or not user.username:
            continue

        try:
            await client.send_message(user.username, f"Olá! 😊 Venha participar do nosso grupo: {invite_link}")
            count += 1
            print(f"[{datetime.now()}] 已发送给 {user.username} (第 {count} 个)")
            await asyncio.sleep(5)  # 每次间隔 5 秒
            if count >= 30:  # 每次运行最多发 30 个
                print("已达今日上限，停止发送。")
                break
        except Exception as e:
            print(f"无法发送给 {user.username}: {e}")

asyncio.run(main())
