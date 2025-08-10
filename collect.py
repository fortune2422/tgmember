import os
import asyncio
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import ChatAdminRequiredError, ChannelPrivateError

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# 从文件读取群链接
with open("groups.txt", "r", encoding="utf-8") as f:
    GROUPS = [line.strip() for line in f if line.strip()]

# 保存 session 到文件，避免重启后需要重新登录
SESSION_FILE = "collector_session"

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

async def collect_members():
    await client.start()
    print("✅ 已登录 Telegram API")

    for group_link in GROUPS:
        try:
            chat = await client.get_entity(group_link)
            print(f"\n📌 正在采集群: {group_link}")
            members = await client.get_participants(chat)
            print(f"👥 共采集到 {len(members)} 个成员")

            # 保存到 CSV
            filename = f"{chat.title}_members.csv".replace(" ", "_")
            with open(filename, "w", encoding="utf-8") as f:
                f.write("user_id,username,first_name,last_name\n")
                for m in members:
                    f.write(f"{m.id},{m.username or ''},{m.first_name or ''},{m.last_name or ''}\n")
            print(f"💾 已保存到 {filename}")

        except ChatAdminRequiredError:
            print(f"❌ 没有权限查看 {group_link} 成员列表")
        except ChannelPrivateError:
            print(f"❌ 无法访问私有群 {group_link}")
        except Exception as e:
            print(f"⚠️ 采集 {group_link} 出错: {e}")

    await client.disconnect()
    print("\n✅ 所有群采集完成")

if __name__ == "__main__":
    asyncio.run(collect_members())
