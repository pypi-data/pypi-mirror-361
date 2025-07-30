🎁 puregram – Telegram Gift & Star Parser Library
puregram is a fast, modular Python library for parsing Telegram gifts and stars from business chats.
Compatible with official Bot API and optional userbot integration.

Ideal for automation, dashboards, internal analytics, or gamified reward systems.

📦 Installation
```bash
pip install puregram
```
🚀 Quick Start
```python
from puregram import GiftParser

parser = GiftParser(bot_token="1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
gifts = parser.fetch_recent_gifts(chat_id="@your_channel")

for gift in gifts:
    print(f"🎁 Gift ID: {gift.id}, Sender: {gift.sender.username}, Type: {gift.type}, Amount: {gift.amount}")
```
🔧 Features
- 🎁 Parse all incoming gifts and stars from Telegram
- 📎 Access full metadata: ID, sender, type, amount, timestamp
- 📉 Rate-limit aware logic
- 🔄 Works with Bot API and optional UserBot (Telethon-based)

📚 API Reference
GiftParser
```python
GiftParser(bot_token: str, use_userbot: bool = False)
```
Methods:
- `fetch_recent_gifts(chat_id: str, limit: int = 100) -> List[Gift]`  
  Fetch the most recent gift transactions from the specified chat.

- `get_gift_by_id(gift_id: str) -> Gift`  
  Retrieve a gift object using its ID.

- `listen(callback: Callable[[Gift], None])`  
  Start live event listener for real-time gift parsing (requires userbot mode).

🎁 Gift Object
```python
class Gift:
    id: str
    sender: User
    type: str  # "star", "nft", or "custom"
    amount: int
    timestamp: datetime
```
🧪 Async Usage Example
```python
import asyncio
from puregram import GiftParser

async def main():
    parser = GiftParser(bot_token="123:ABC", use_userbot=True)

    async for gift in parser.stream("@gift_channel"):
        print(f"New gift from {gift.sender.username}: {gift.type} x{gift.amount}")

asyncio.run(main())
```
📄 License
MIT License

📬 Contact
For inquiries, bug reports, or collaboration:
📧 Email: support@puregram.dev 