# 🎁 GramApi – Telegram Gift & Star Parser Library
GramApi is a lightweight and efficient Python library designed for parsing gifts and stars from Telegram Business chats using both official API and optional userbot integration.

Perfect for analytics, automation, dashboards, and backend services.

## 📦 Installation
```bash
pip install gramapi
```
## 🚀 Quick Start
```python
from gramapi import GiftParser

parser = GiftParser(bot_token="1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
gifts = parser.fetch_recent_gifts(chat_id="@your_channel")

for gift in gifts:
    print(f"🎁 Gift ID: {gift.id}, Sender: {gift.sender.username}, Type: {gift.type}, Amount: {gift.amount}")
```
## 🔧 Features
- 🧾 Parse all available Telegram gifts and stars
- 📊 Extract metadata: gift ID, sender info, type, value, timestamp
- 🛡️ Rate-limit safe
- 🔌 Supports both Bot API and UserBot (Telethon)

## 📚 API Reference
### GiftParser
```python
GiftParser(bot_token: str, use_userbot: bool = False)
```
**Methods:**
- `fetch_recent_gifts(chat_id: str, limit: int = 100) -> List[Gift]`  
  Fetch recent gift transactions from a chat/channel.

- `get_gift_by_id(gift_id: str) -> Gift`  
  Fetch a single gift object by ID.

- `listen(callback: Callable[[Gift], None])`  
  Start real-time monitoring (UserBot required).

### 🎁 Gift Object Structure
```python
class Gift:
    id: str
    sender: User
    type: str  # "star", "nft", "custom"
    amount: int
    timestamp: datetime
```
## 🧪 Async Usage Example
```python
import asyncio
from gramapi import GiftParser

async def main():
    parser = GiftParser(bot_token="123:ABC", use_userbot=True)

    async for gift in parser.stream("@gift_channel"):
        print(f"New gift from {gift.sender.username}: {gift.type} x{gift.amount}")

asyncio.run(main())
```
## 📄 License
MIT License

## 📬 Support
Telegram support bot: @gramapi_support_bot 