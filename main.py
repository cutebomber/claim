"""
Telegram Public Channel Creator
Uses Telethon to log in and create a public channel with a given username.

Requirements:
    pip install telethon

Usage:
    python create_telegram_channel.py
"""

import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, UpdateUsernameRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors import (
    UsernameOccupiedError,
    UsernameInvalidError,
    FloodWaitError,
    SessionPasswordNeededError,
)

# ── Credentials ───────────────────────────────────────────────────────────────
API_ID   = 21752358
API_HASH = "fb46a136fed4a4de27ab057c7027fec3"
SESSION  = "my_telegram_session"   # session file saved locally (.session)

# ── Channel settings ──────────────────────────────────────────────────────────
CHANNEL_USERNAME = input("Enter the username to claim (without @): ").strip()
CHANNEL_TITLE    = f"@{CHANNEL_USERNAME}"   # channel display name
CHANNEL_BIO      = "owner : @hankie"


async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start()

    # Handle 2FA if enabled
    if not await client.is_user_authorized():
        print("Not authorized. Please check your session.")
        return

    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name} (@{me.username})")

    # ── Create the channel ────────────────────────────────────────────────────
    print(f"\n⏳ Creating channel '{CHANNEL_TITLE}' ...")
    try:
        result = await client(CreateChannelRequest(
            title=CHANNEL_TITLE,
            about=CHANNEL_BIO,
            megagroup=False,   # False = broadcast channel, True = supergroup
        ))
        channel = result.chats[0]
        print(f"✅ Channel created  →  id: {channel.id}")
    except FloodWaitError as e:
        print(f"⚠️  Flood wait: please retry after {e.seconds} seconds.")
        return
    except Exception as e:
        print(f"❌ Failed to create channel: {e}")
        return

    # ── Set public username ───────────────────────────────────────────────────
    print(f"⏳ Setting username @{CHANNEL_USERNAME} ...")
    try:
        await client(UpdateUsernameRequest(channel, CHANNEL_USERNAME))
        print(f"✅ Username set  →  t.me/{CHANNEL_USERNAME}")
    except UsernameOccupiedError:
        print("❌ Username is already taken. Try a different one.")
    except UsernameInvalidError:
        print("❌ Username is invalid. Use only letters, numbers, and underscores (5–32 chars).")
    except FloodWaitError as e:
        print(f"⚠️  Flood wait: please retry after {e.seconds} seconds.")
    except Exception as e:
        print(f"❌ Failed to set username: {e}")

    print("\n🎉 Done!")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
