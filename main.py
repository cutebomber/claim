import os
import asyncio
import sys
from telethon import TelegramClient, errors
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.functions.channels import UpdateUsernameRequest as ChannelUpdateUsername
from telethon.tl.functions.account import CheckUsernameRequest

# Your API credentials
API_ID = 21752358
API_HASH = 'fb46a136fed4a4de27ab057c7027fec3'
SESSION_NAME = 'my_account'

async def logout_session():
    """Logout and delete session file"""
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    
    if await client.is_user_authorized():
        # This terminates the session on Telegram's side
        await client.log_out()
        print("✅ Logged out from Telegram servers")
    else:
        print("⚠️ Not logged in")
    
    await client.disconnect()
    
    # Delete the session file locally
    session_file = f"{SESSION_NAME}.session"
    if os.path.exists(session_file):
        os.remove(session_file)
        print(f"✅ Deleted local session file: {session_file}")
    
    # Also delete .journal file if it exists
    journal_file = f"{SESSION_NAME}.session-journal"
    if os.path.exists(journal_file):
        os.remove(journal_file)
        print(f"✅ Deleted journal file: {journal_file}")

async def main():
    # Check if logout argument is provided
    if len(sys.argv) > 1 and sys.argv[1] == "--logout":
        await logout_session()
        return
    
    # Rest of your main script here...
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print("✅ Logged in successfully!")

    # ... (rest of your username claiming code)

if __name__ == '__main__':
    asyncio.run(main())
