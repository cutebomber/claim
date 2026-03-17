import os
import asyncio
import sys
from telethon import TelegramClient, errors
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.functions.channels import UpdateUsernameRequest as ChannelUpdateUsername
from telethon.tl.functions.account import CheckUsernameRequest
from telethon.tl.types import Channel
import random

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    ORANGE = '\033[38;5;214m'
    PURPLE = '\033[38;5;141m'
    PINK = '\033[38;5;213m'
    GRAY = '\033[90m'
    WHITE = '\033[97m'

# Your API credentials
API_ID = 21752358
API_HASH = 'fb46a136fed4a4de27ab057c7027fec3'
SESSION_NAME = 'my_account'

def print_banner():
    """Print a cool banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}╔════════════════════════════════════════════════════════════════╗
║{Colors.YELLOW}  ████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗{Colors.CYAN} ║
║{Colors.YELLOW}  ╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║{Colors.CYAN} ║
║{Colors.YELLOW}     ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██╔████╔██║{Colors.CYAN} ║
║{Colors.YELLOW}     ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║{Colors.CYAN} ║
║{Colors.YELLOW}     ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║{Colors.CYAN} ║
║{Colors.YELLOW}     ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝{Colors.CYAN} ║
║{Colors.GREEN}                  USERNAME MANAGER v3.0{Colors.CYAN}                              ║
║{Colors.PINK}              Created with ❤️  by @hankie{Colors.CYAN}                              ║
╚════════════════════════════════════════════════════════════════╝{Colors.END}
"""
    print(banner)

def print_step(message, emoji="➤"):
    """Print a step message"""
    print(f"{Colors.CYAN}{emoji} {Colors.BOLD}{message}{Colors.END}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {Colors.BOLD}{message}{Colors.END}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {Colors.BOLD}{message}{Colors.END}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {Colors.BOLD}{message}{Colors.END}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {Colors.BOLD}{message}{Colors.END}")

async def logout_session():
    """Logout and delete session file"""
    print_step("Logging out session...", "🔐")
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    
    if await client.is_user_authorized():
        await client.log_out()
        print_success("Logged out from Telegram servers")
    else:
        print_warning("Not logged in")
    
    await client.disconnect()
    
    # Delete session files
    session_file = f"{SESSION_NAME}.session"
    if os.path.exists(session_file):
        os.remove(session_file)
        print_success(f"Deleted local session file: {session_file}")
    
    journal_file = f"{SESSION_NAME}.session-journal"
    if os.path.exists(journal_file):
        os.remove(journal_file)
        print_success(f"Deleted journal file: {journal_file}")

async def list_public_usernames():
    """List all public channels/groups with usernames owned by the account"""
    print_step("Logging in to list usernames...", "🔑")
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print_success("Logged in successfully!")
    
    print_step("Fetching your dialogs (chats/channels)...", "🔍")
    
    public_items = []
    total_dialogs = 0
    
    # Get all dialogs
    async for dialog in client.iter_dialogs():
        total_dialogs += 1
        entity = dialog.entity
        
        # Check if it's a channel/group with a username
        if hasattr(entity, 'username') and entity.username:
            username = f"@{entity.username}"
            title = dialog.name or "No title"
            
            # Determine type with emojis
            if hasattr(entity, 'megagroup') and entity.megagroup:
                type_str = "📢 Supergroup"
                type_color = Colors.PURPLE
            elif hasattr(entity, 'gigagroup') and entity.gigagroup:
                type_str = "🌟 Gigagroup"
                type_color = Colors.ORANGE
            elif isinstance(entity, Channel):
                if entity.broadcast:
                    type_str = "📺 Channel"
                    type_color = Colors.CYAN
                else:
                    type_str = "👥 Group"
                    type_color = Colors.GREEN
            else:
                type_str = "💬 Chat"
                type_color = Colors.BLUE
            
            # Check if you're the owner/creator
            is_creator = False
            try:
                full_entity = await client.get_entity(entity.id)
                if hasattr(full_entity, 'creator') and full_entity.creator:
                    is_creator = True
            except:
                pass
            
            public_items.append({
                'username': username,
                'title': title,
                'type': type_str,
                'type_color': type_color,
                'id': entity.id,
                'is_creator': is_creator
            })
    
    # Print results in a beautiful table
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}                        📋 YOUR PUBLIC USERNAMES 📋{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════════════════════{Colors.END}")
    
    if public_items:
        print(f"{Colors.GRAY}┌─────────────────────┬─────────────────┬────────────┬─────────────────┐{Colors.END}")
        print(f"{Colors.GRAY}│{Colors.END} {Colors.BOLD}{Colors.WHITE}Username            {Colors.GRAY}│{Colors.END} {Colors.BOLD}{Colors.WHITE}Type            {Colors.GRAY}│{Colors.END} {Colors.BOLD}{Colors.WHITE}Creator   {Colors.GRAY}│{Colors.END} {Colors.BOLD}{Colors.WHITE}ID              {Colors.GRAY}│{Colors.END}")
        print(f"{Colors.GRAY}├─────────────────────┼─────────────────┼────────────┼─────────────────┤{Colors.END}")
        
        public_items.sort(key=lambda x: x['username'])
        for item in public_items:
            creator_mark = f"{Colors.GREEN}👑 Yes{Colors.END}" if item['is_creator'] else f"{Colors.GRAY}❌ No{Colors.END}"
            username_display = f"{Colors.YELLOW}{item['username']}{Colors.END}"
            type_display = f"{item['type_color']}{item['type']}{Colors.END}"
            id_display = f"{Colors.GRAY}{item['id']}{Colors.END}"
            
            # Truncate long titles for display
            title_display = item['title'][:18] + "..." if len(item['title']) > 20 else item['title']
            print(f"{Colors.GRAY}│{Colors.END} {username_display:<20} {Colors.GRAY}│{Colors.END} {type_display:<15} {Colors.GRAY}│{Colors.END} {creator_mark:<11} {Colors.GRAY}│{Colors.END} {id_display:<15} {Colors.GRAY}│{Colors.END}")
        
        print(f"{Colors.GRAY}└─────────────────────┴─────────────────┴────────────┴─────────────────┘{Colors.END}")
        print(f"\n{Colors.GREEN}✅ Found {Colors.BOLD}{len(public_items)}{Colors.END}{Colors.GREEN} public items with usernames!{Colors.END}")
        print(f"{Colors.GRAY}📊 Total dialogs scanned: {total_dialogs}{Colors.END}")
    else:
        print(f"{Colors.YELLOW}╔════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.YELLOW}║{Colors.END}  {Colors.RED}❌ No public usernames found in your account.{Colors.YELLOW}           ║{Colors.END}")
        print(f"{Colors.YELLOW}║{Colors.END}  {Colors.GRAY}Note: Only shows dialogs you have access to.{Colors.YELLOW}          ║{Colors.END}")
        print(f"{Colors.YELLOW}╚════════════════════════════════════════════════════════════╝{Colors.END}")
    
    await client.disconnect()

async def claim_usernames():
    """Main function to claim usernames"""
    print_step("Initializing Telegram client...", "⚡")
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print_success("Logged in successfully!")
    print(f"{Colors.GRAY}Session: {SESSION_NAME}.session{Colors.END}\n")

    # Read usernames
    print(f"{Colors.MAGENTA}{Colors.BOLD}📝 Enter usernames to check and claim (one per line){Colors.END}")
    print(f"{Colors.GRAY}Press Enter on an empty line to start processing{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    
    usernames = []
    while True:
        line = (await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)).strip()
        if not line:
            break
        cleaned = line.lstrip('@')
        usernames.append(cleaned)
        print(f"{Colors.GREEN}  ✓ Added: @{cleaned}{Colors.END}")

    if not usernames:
        print_error("No usernames provided. Exiting.")
        await client.disconnect()
        return

    print(f"\n{Colors.CYAN}{'='*50}{Colors.END}")
    print(f"{Colors.YELLOW}{Colors.BOLD}🎯 Processing {len(usernames)} username(s)...{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}\n")

    successful = 0
    failed = 0
    skipped = 0

    for idx, username in enumerate(usernames, 1):
        # Progress indicator
        print(f"{Colors.MAGENTA}[{idx}/{len(usernames)}]{Colors.END} Checking @{username}... ", end="", flush=True)
        
        # 1. Check availability
        try:
            result = await client(CheckUsernameRequest(username))
            available = result
        except errors.UsernameInvalidError:
            print(f"{Colors.RED}❌ Invalid format{Colors.END}")
            skipped += 1
            continue
        except errors.RPCError as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
            failed += 1
            continue

        if not available:
            print(f"{Colors.YELLOW}⚠️ Already taken{Colors.END}")
            skipped += 1
            continue

        print(f"{Colors.GREEN}✅ Available! Creating channel...{Colors.END}")

        # 2. Create channel
        try:
            result = await client(CreateChannelRequest(
                title="@",
                about="owner : @hankie",
                megagroup=False
            ))
            
            if hasattr(result, 'chats') and result.chats:
                channel = result.chats[0]
            else:
                channel = result[0].chats[0] if isinstance(result, list) else None
            
            if not channel:
                print(f"   {Colors.RED}❌ Failed to get channel object{Colors.END}")
                failed += 1
                continue
                
            # 3. Set username
            try:
                await client(ChannelUpdateUsername(channel=channel, username=username))
                print(f"   {Colors.GREEN}{Colors.BOLD}✅ SUCCESSFULLY CLAIMED @{username}! 🎉{Colors.END}")
                successful += 1
                
                # Show channel info
                print(f"   {Colors.GRAY}├─ Channel ID: {channel.id}{Colors.END}")
                print(f"   {Colors.GRAY}├─ Title: @{Colors.END}")
                print(f"   {Colors.GRAY}└─ Bio: owner : @hankie{Colors.END}\n")
                
            except errors.UsernameOccupiedError:
                print(f"   {Colors.RED}❌ Taken right before setting{Colors.END}")
                failed += 1
            except errors.UsernameInvalidError:
                print(f"   {Colors.RED}❌ Invalid username{Colors.END}")
                failed += 1
            except Exception as e:
                print(f"   {Colors.RED}❌ Failed: {e}{Colors.END}")
                failed += 1

        except errors.RPCError as e:
            print(f"   {Colors.RED}❌ Channel creation failed: {e}{Colors.END}")
            failed += 1
        except Exception as e:
            print(f"   {Colors.RED}❌ Unexpected error: {e}{Colors.END}")
            failed += 1

        # Delay to avoid rate limits
        if idx < len(usernames):
            await asyncio.sleep(2)

    # Final summary
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}📊 FINAL SUMMARY{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}✅ Successfully claimed: {successful}{Colors.END}")
    print(f"{Colors.RED}❌ Failed: {failed}{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  Skipped (taken/invalid): {skipped}{Colors.END}")
    print(f"{Colors.BLUE}📝 Total processed: {len(usernames)}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    
    # Success animation if any claimed
    if successful > 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 CONGRATULATIONS! 🎉{Colors.END}")
        for _ in range(3):
            print(f"{random.choice([Colors.RED, Colors.GREEN, Colors.YELLOW, Colors.BLUE, Colors.MAGENTA, Colors.CYAN])}✦{Colors.END}", end="", flush=True)
            await asyncio.sleep(0.1)
        print(f"\n{Colors.PINK}You've successfully claimed {successful} username(s)!{Colors.END}")
    
    await client.disconnect()

def show_help():
    """Show help menu"""
    print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}  {Colors.BOLD}{Colors.YELLOW}🚀 TELEGRAM USERNAME MANAGER - HELP{Colors.CYAN}                         ║{Colors.END}")
    print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════════╣{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}Usage:{Colors.END} python telegram_username_manager.py [OPTION]              {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}                                                                  {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}  {Colors.YELLOW}Options:{Colors.END}                                                         {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}    {Colors.CYAN}--list{Colors.END}     List all public usernames in your account             {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}    {Colors.CYAN}--logout{Colors.END}   Logout and delete session file                        {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}    {Colors.CYAN}--claim{Colors.END}    Run username claiming process (default)                {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}    {Colors.CYAN}--help{Colors.END}     Show this help message                                {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}                                                                  {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}Examples:{Colors.END}                                                       {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}    python telegram_username_manager.py --list                     {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}    python telegram_username_manager.py --logout                   {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}    python telegram_username_manager.py                            {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END}    (no args starts claim mode)                                    {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════╝{Colors.END}")

async def main():
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Print banner
    print_banner()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "--logout" or arg == "-l":
            await logout_session()
        elif arg == "--list" or arg == "-ls":
            await list_public_usernames()
        elif arg == "--help" or arg == "-h":
            show_help()
        elif arg == "--claim" or arg == "-c":
            await claim_usernames()
        else:
            print_error(f"Unknown option: {sys.argv[1]}")
            show_help()
    else:
        # No arguments - run claim mode
        await claim_usernames()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Script interrupted by user{Colors.END}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
