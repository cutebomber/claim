import asyncio
import sys
from telethon import TelegramClient, errors
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.functions.account import UpdateUsernameRequest, CheckUsernameRequest

# Your API credentials
API_ID = 21752358
API_HASH = 'fb46a136fed4a4de27ab057c7027fec3'

SESSION_NAME = 'my_account'

async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print("✅ Logged in successfully!")

    # Read usernames from user input (one per line, empty line to finish)
    print("Enter usernames to check and claim (one per line). Press Enter on an empty line to start processing:")
    usernames = []
    while True:
        line = (await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)).strip()
        if not line:
            break
        # Remove '@' if accidentally included
        cleaned = line.lstrip('@')
        usernames.append(cleaned)

    if not usernames:
        print("No usernames provided. Exiting.")
        await client.disconnect()
        return

    print(f"\nProcessing {len(usernames)} username(s)...\n")

    for idx, username in enumerate(usernames, 1):
        print(f"[{idx}/{len(usernames)}] Checking @{username}...")

        # 1. Check availability
        try:
            available = await client(CheckUsernameRequest(username))
        except errors.UsernameInvalidError:
            print(f"   ❌ Username @{username} is invalid (bad format).")
            continue
        except errors.RPCError as e:
            print(f"   ❌ Error checking @{username}: {e}")
            continue

        if not available:
            print(f"   ❌ Username @{username} is already taken.")
            continue

        print(f"   ✅ Username @{username} is available. Creating channel...")

        # 2. Create channel with title "@" and bio "owner : @hankie"
        try:
            result = await client(CreateChannelRequest(
                title="@",
                about="owner : @hankie",
                megagroup=False  # normal channel
            ))
            channel = result.chats[0]  # the new channel
            print(f"   ✅ Channel created (ID: {channel.id}). Setting username...")

            # 3. Set the username
            try:
                await client(UpdateUsernameRequest(channel, username))
                print(f"   ✅ Successfully claimed @{username}!\n")
            except errors.UsernameOccupiedError:
                # Rare race condition – someone else took it just now
                print(f"   ❌ Failed: @{username} was taken right before setting.")
            except errors.UsernameInvalidError:
                print(f"   ❌ Failed: @{username} is invalid.")
            except Exception as e:
                print(f"   ❌ Failed to set username: {e}")

        except errors.RPCError as e:
            print(f"   ❌ Failed to create channel: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")

        # Delay to avoid hitting rate limits
        if idx < len(usernames):  # no need to wait after the last one
            await asyncio.sleep(2)

    print("\nAll done!")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
