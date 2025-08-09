# main.py
import os
import asyncio
from datetime import datetime
from fastapi import FastAPI, Response
from telethon import TelegramClient
import csv

# config from env
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE = os.getenv("PHONE_NUMBER", "")            # e.g. +639999005166
TARGET_GROUP = os.getenv("TARGET_GROUP", "")     # e.g. https://t.me/oficial9fbetbr
SESSION_DIR = os.getenv("SESSION_DIR", "/data")
SESSION_NAME = os.path.join(SESSION_DIR, "telethon_session")
EXPORT_DIR = os.getenv("EXPORT_DIR", "/data")
EXPORT_PREFIX = os.getenv("EXPORT_PREFIX", "members")

if not os.path.isdir(SESSION_DIR):
    os.makedirs(SESSION_DIR, exist_ok=True)
if not os.path.isdir(EXPORT_DIR):
    os.makedirs(EXPORT_DIR, exist_ok=True)

app = FastAPI(title="Telegram Exporter")

def make_client():
    return TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def do_export():
    client = make_client()
    await client.start(phone=PHONE)  # if session present, this won't ask code
    entity = await client.get_entity(TARGET_GROUP)
    members = await client.get_participants(entity, aggressive=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{EXPORT_PREFIX}_{timestamp}.csv"
    path = os.path.join(EXPORT_DIR, filename)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "user_id", "phone"])
        for m in members:
            username = m.username or ""
            uid = m.id
            phone = getattr(m, "phone", "") or ""
            writer.writerow([username, uid, phone])

    await client.disconnect()
    return path, len(members)

@app.on_event("startup")
async def startup_event():
    # automatic export on startup if session exists
    session_exists = os.path.exists(SESSION_NAME + ".session") or os.path.exists(SESSION_NAME + ".session-journal")
    if session_exists:
        try:
            path, count = await do_export()
            print(f"[startup] Exported {count} members -> {path}")
            # write latest pointer
            with open(os.path.join(EXPORT_DIR, "latest.txt"), "w") as t:
                t.write(path)
        except Exception as e:
            print("[startup] export failed:", e)
    else:
        print("[startup] No session file found. Please run interactive init locally or via Render Shell to login.")

@app.get("/")
def index():
    return {"status": "ok", "note": "Use /export to export, /download to fetch latest file."}

@app.post("/export")
async def export_endpoint():
    try:
        path, count = await do_export()
        with open(os.path.join(EXPORT_DIR, "latest.txt"), "w") as t:
            t.write(path)
        return {"status": "ok", "exported": count, "path": path}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/download")
def download_latest():
    latest_file = os.path.join(EXPORT_DIR, "latest.txt")
    if not os.path.exists(latest_file):
        return Response("No export yet", status_code=404)
    with open(latest_file, "r") as f:
        path = f.read().strip()
    if not os.path.exists(path):
        return Response("File missing", status_code=404)
    with open(path, "rb") as f:
        data = f.read()
    filename = os.path.basename(path)
    return Response(content=data, media_type="text/csv", headers={
        "Content-Disposition": f'attachment; filename="{filename}"'
    })

if __name__ == "__main__":
    import uvicorn, argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="Run interactive login locally to create session")
    args = parser.parse_args()

    if args.init:
        # Interactive one-off to create session locally (use this on your laptop)
        async def init_session():
            client = make_client()
            print("Starting interactive login. You will receive a code in your Telegram app.")
            await client.start(phone=PHONE)
            print("✅ session created at", SESSION_NAME + ".session")
            await client.disconnect()
        asyncio.run(init_session())
    else:
        port = int(os.environ.get("PORT", 10000))
        uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
