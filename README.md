# Telethon Invite Bot

批量抓取 Telegram 公开群成员并发送私聊邀请。

## 部署到 Render
1. Fork 这个仓库
2. 在 Render 创建一个新的 Web Service
3. 在 Environment 变量里添加：
   - `API_ID`
   - `API_HASH`
   - `PHONE`（+55 开头）
   - `TARGET_GROUP`（不带 https://t.me/）
   - `INVITE_LINK`
4. 部署后第一次运行会在日志里提示输入验证码
