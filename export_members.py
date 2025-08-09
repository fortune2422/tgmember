import os
import asyncio
from telethon import TelegramClient
import openpyxl

# 从环境变量读取配置
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE_NUMBER")
target_group = os.getenv("TARGET_GROUP")

client = TelegramClient('scraper_session', api_id, api_hash)

async def export_members():
    print("📞 正在登录 Telegram...")
    await client.start(phone)

    print(f"📂 正在获取群: {target_group}")
    group = await client.get_entity(target_group)

    print("📋 正在获取成员列表...")
    members = await client.get_participants(group)

    print(f"✅ 共获取 {len(members)} 位成员，正在保存到 Excel...")
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Username", "User ID", "Phone Number"])  # 电话可能为空

    for m in members:
        sheet.append([m.username, m.id, getattr(m, 'phone', '')])

    file_name = "members.xlsx"
    workbook.save(file_name)
    print(f"💾 数据已保存到 {file_name}")

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(export_members())
