import asyncio
import sys
from telethon import TelegramClient
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    UpdateUsernameRequest,
    DeleteChannelRequest,
)
from telethon.errors import (
    UsernameOccupiedError,
    UsernameInvalidError,
    FloodWaitError,
    SessionPasswordNeededError,
)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
API_ID   = 21752358     # Get from https://my.telegram.org/apps
API_HASH = "fb46a136fed4a4de27ab057c7027fec3"    # Get from https://my.telegram.org/apps

CHANNEL_DISPLAY_NAME = "@"
CHANNEL_BIO          = "owner : @hankie"
# ──────────────────────────────────────────────────────────────────────────────


async def login(client):
    """Handles phone, OTP and optional 2FA login interactively."""

    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"✅ Already logged in as {me.first_name} (@{me.username})\n")
        return True

    # ── Step 1: Phone number ────────────────────────────────────────────────
    phone = input("📱 Enter your phone number (with country code, e.g. +1234567890): ").strip()

    await client.send_code_request(phone)
    print("📨 OTP sent to your Telegram app.\n")

    # ── Step 2: OTP ─────────────────────────────────────────────────────────
    while True:
        otp = input("🔑 Enter the OTP you received: ").strip().replace(" ", "")
        try:
            await client.sign_in(phone, otp)
            break
        except SessionPasswordNeededError:
            # ── Step 3: 2FA password (if enabled) ───────────────────────────
            print("\n🔒 2FA is enabled on this account.")
            while True:
                password = input("🔐 Enter your 2FA password: ").strip()
                try:
                    await client.sign_in(password=password)
                    break
                except Exception as e:
                    print(f"    ❌ Wrong 2FA password: {e}. Try again.")
            break
        except Exception as e:
            print(f"    ❌ Invalid OTP: {e}. Try again.")

    me = await client.get_me()
    print(f"\n✅ Logged in successfully as {me.first_name} (@{me.username})\n")
    return True


async def claim_username(client, username):
    print(f"\n[*] Trying to claim @{username} ...")
    channel = None

    try:
        result = await client(CreateChannelRequest(
            title=CHANNEL_DISPLAY_NAME,
            about=CHANNEL_BIO,
            megagroup=False
        ))
        channel = result.chats[0]
        print(f"    ✅ Channel created (ID: {channel.id})")

        await client(UpdateUsernameRequest(channel, username))
        print(f"    🎉 @{username} claimed successfully!")
        return True

    except UsernameOccupiedError:
        print(f"    ❌ @{username} is already taken.")
    except UsernameInvalidError:
        print(f"    ❌ @{username} is invalid.")
    except FloodWaitError as e:
        print(f"    ⚠️  Flood wait! Sleeping {e.seconds}s ...")
        await asyncio.sleep(e.seconds + 5)
    except Exception as e:
        print(f"    ❌ Unexpected error: {e}")

    # Clean up failed/empty channel
    if channel:
        try:
            await client(DeleteChannelRequest(channel))
            print(f"    🗑️  Cleaned up empty channel.")
        except Exception:
            pass

    return False


async def main():
    # Use a generic session name; reused on next run if already logged in
    client = TelegramClient("session_claimer", API_ID, API_HASH)

    # ── Login ────────────────────────────────────────────────────────────────
    await login(client)

    # ── Get usernames ────────────────────────────────────────────────────────
    print("📋 Enter usernames to claim (one per line).")
    print("   When done, type 'done' and press Enter.\n")

    usernames = []
    while True:
        entry = input(f"   Username {len(usernames) + 1}: ").strip().lstrip("@")
        if entry.lower() == "done":
            if not usernames:
                print("   ⚠️  No usernames entered. Please add at least one.")
                continue
            break
        if entry:
            usernames.append(entry)
            print(f"   ✅ Added @{entry}")

    print(f"\n🚀 Starting to claim {len(usernames)} username(s)...\n")

    # ── Claim ────────────────────────────────────────────────────────────────
    claimed, failed = [], []

    for username in usernames:
        success = await claim_username(client, username)
        (claimed if success else failed).append(username)
        await asyncio.sleep(3)

    # ── Results ──────────────────────────────────────────────────────────────
    print("\n" + "═" * 40)
    print("📋 FINAL RESULTS")
    print("═" * 40)
    print(f"  🎉 Claimed ({len(claimed)}): {', '.join(claimed) or 'None'}")
    print(f"  ❌ Failed  ({len(failed)}):  {', '.join(failed)  or 'None'}")
    print("═" * 40)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
