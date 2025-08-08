import os
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import openpyxl

# 从环境变量读取
API_ID = int(os.environ.get("TG_API_ID", "25383117"))  # 替换成你的 api_id
API_HASH = os.environ.get("TG_API_HASH", "c12894dabde9aa99cbe181e7ee8ec5b8")  # 替换成你的 api_hash
PHONE_NUMBER = os.environ.get("TG_PHONE", "+639157681213")  # 你的 Telegram 账号手机号（带国家码）

SESSION_FILE = "session"  # 登录会话文件，Render 会保存它

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

    await client.start(phone=PHONE_NUMBER)
    print("✅ 登录成功！")

    # 输入群链接或用户名
    group_url = os.environ.get("TG_GROUP", "https://t.me/examplegroup")
    entity = await client.get_entity(group_url)

    members = await client.get_participants(entity, aggressive=True)
    print(f"📥 共获取到 {len(members)} 个成员")

    # 保存到 Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["User ID", "Username", "Name", "Phone"])

    for user in members:
        ws.append([
            user.id,
            user.username if user.username else "",
            f"{user.first_name or ''} {user.last_name or ''}".strip(),
            user.phone if user.phone else ""
        ])

    file_name = "members.xlsx"
    wb.save(file_name)
    print(f"💾 成员信息已保存到 {file_name}")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
