from telethon import TelegramClient, events
import pandas as pd
import os

# 你的 Telegram API 信息（在 https://my.telegram.org 获取）
api_id = 25383117     # 替换成你的 API ID
api_hash = 'c12894dabde9aa99cbe181e7ee8ec5b8'  # 替换成你的 API Hash
session_name = 'collector_session'

# 数据文件
DATA_FILE = 'users.csv'
GROUPS_FILE = 'groups.txt'

# 加载已有数据
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=['user_id', 'username', 'group_id', 'last_seen'])

# 保存数据
def save_data():
    df.to_csv(DATA_FILE, index=False)
    print(f"[保存] 当前已采集 {len(df)} 位用户")

# 创建客户端
client = TelegramClient(session_name, api_id, api_hash)

# 监听消息
@client.on(events.NewMessage)
async def handler(event):
    global df
    sender = await event.get_sender()
    if sender and sender.id:
        user_id = sender.id
        username = sender.username or ''
        group_id = event.chat_id
        last_seen = pd.Timestamp.now()

        # 更新或新增
        if user_id in df['user_id'].values:
            df.loc[df['user_id'] == user_id, ['username', 'group_id', 'last_seen']] = [username, group_id, last_seen]
        else:
            df = pd.concat([df, pd.DataFrame([[user_id, username, group_id, last_seen]],
                                             columns=df.columns)], ignore_index=True)
        save_data()

async def main():
    # 读取群链接
    with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
        groups = [line.strip() for line in f if line.strip()]

    print(f"[启动] 共 {len(groups)} 个群等待加入并监听...")

    for group in groups:
        try:
            await client(JoinChannelRequest(group))
            print(f"[加入] {group}")
        except Exception as e:
            print(f"[错误] 无法加入 {group}: {e}")

    print("[运行中] 正在监听群消息...")

# 启动
with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
