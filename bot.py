import aiohttp
import asyncio
import json
import os
import random
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize Console for Rich Formatting
console = Console()

def display_logo():
    console.print(Panel.fit(
        "[bold cyan] ██████████                               ███████████ █████   █████ ████   ████████ [/]\n"
        "[bold cyan]░░███░░░░███                             ░█░░░███░░░█░░███   ░░███ ░░███  ███░░░░███[/]\n"
        "[bold cyan] ░███   ░░███  ██████   ██████  ████████ ░   ░███  ░  ░███    ░███  ░███ ░░░    ░███[/]\n"
        "[bold cyan] ░███    ░███ ███░░███ ███░░███░░███░░███    ░███     ░███    ░███  ░███    ███████[/]\n"
        "[bold cyan] ░███    ░███░███████ ░███████  ░███ ░███    ░███     ░░███   ███   ░███   ███░░░░[/]\n"
        "[bold cyan] ░███    ███ ░███░░░  ░███░░░   ░███ ░███    ░███      ░░░█████░    ░███  ███      █[/]\n"
        "[bold cyan] ██████████  ░░██████ ░░██████  ░███████     █████       ░░███      █████░██████████[/]\n"
        "[bold cyan]░░░░░░░░░░    ░░░░░░   ░░░░░░   ░███░░░     ░░░░░         ░░░      ░░░░░ ░░░░░░░░░░[/]\n"
        "\n[bold yellow]© DeepTV | Telegram: [blue]https://t.me/DeepTV12[/][/]"
    ))

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def watermark(text, status="INFO", color="white"):
    timestamp = get_time()
    return f"[{timestamp}] [{status}] [bold {color}]{text}[/] [dim]— DeepTV12[/]"

async def read_tokens():
    file_path = "data.txt"
    if not os.path.exists(file_path):
        console.print(watermark("data.txt file not found!", "ERROR", "red"))
        return []
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            tokens = [line.strip() for line in file.readlines() if line.strip()]
            if not tokens:
                console.print(watermark("data.txt is empty!", "WARNING", "yellow"))
                return []
            return tokens
    except Exception as e:
        console.print(watermark(f"Failed to read tokens: {e}", "ERROR", "red"))
        return []

def get_user_agent():
    return "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36 Telegram-Android/11.2.2 (Xiaomi M1908C3JGG; Android 12; SDK 31; AVERAGE)"

async def fetch_user_data(session, token, account_number):
    url = "https://api.monkeyrush.fun/api/v1/user"
    headers = {
        'User-Agent': get_user_agent(),
        'Accept': "application/json, text/plain, */*",
        'Authorization': f"Bearer {token}",
        'Origin': "https://clicker.monkeyrush.fun",
        'Referer': "https://clicker.monkeyrush.fun/"
    }

    try:
        async with session.get(url, headers=headers) as response:
            data = await response.text()
            json_data = json.loads(data)
            username = json_data.get("username", "No Name")
            console.print(watermark(f"Account {account_number}: Username - {username}", "SUCCESS", "green"))
    except json.JSONDecodeError:
        console.print(watermark(f"Account {account_number}: Failed to parse JSON!", "ERROR", "red"))
    except Exception as e:
        console.print(watermark(f"Account {account_number}: Request failed - {e}", "ERROR", "red"))

async def take_reward(session, token, account_number):
    url = "https://api.monkeyrush.fun/api/v1/game/take-reward"
    payload = {"type": "daily"}
    headers = {
        'User-Agent': get_user_agent(),
        'Accept': "application/json, text/plain, */*",
        'Content-Type': "application/json",
        'Authorization': f"Bearer {token}",
        'Origin': "https://clicker.monkeyrush.fun",
        'Referer': "https://clicker.monkeyrush.fun/"
    }

    try:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                console.print(watermark(f"Account {account_number}: Reward claimed successfully!", "SUCCESS", "green"))
            else:
                console.print(watermark(f"Account {account_number}: Daily reward already claimed.", "INFO", "yellow"))
    except Exception as e:
        console.print(watermark(f"Account {account_number}: Failed to claim reward - {e}", "ERROR", "red"))

async def send_request(session, token, account_number, clk):
    url = "https://api.monkeyrush.fun/api/v1/game/tap"
    payload = {"score": clk}
    headers = {
        'User-Agent': get_user_agent(),
        'Accept': "application/json, text/plain, */*",
        'Content-Type': "application/json",
        'Authorization': f"Bearer {token}",
        'Origin': "https://clicker.monkeyrush.fun",
        'Referer': "https://clicker.monkeyrush.fun/"
    }

    try:
        async with session.post(url, json=payload, headers=headers) as response:
            result = await response.text()
            data = json.loads(result)
            score = data.get("score", "N/A")
            energy = data.get("energy", "N/A")

            console.print(watermark(f"Acc {account_number}: Score {score} | Energy {energy}", "INFO", "cyan"))

            if energy <= clk:
                console.print(watermark(f"Acc {account_number}: Low energy, waiting 5 minutes.", "WARNING", "red"))
                await asyncio.sleep(300)
    except json.JSONDecodeError:
        console.print(watermark(f"Account {account_number}: Failed to parse JSON response!", "ERROR", "red"))
    except Exception as e:
        console.print(watermark(f"Account {account_number}: Request failed - {e}", "ERROR", "red"))

async def handle_account(token, account_number):
    clk = random.randint(100, 500)  # Random tap value each run
    async with aiohttp.ClientSession() as session:
        await fetch_user_data(session, token, account_number)
        await take_reward(session, token, account_number)

        while True:
            await send_request(session, token, account_number, clk)
            await asyncio.sleep(10)

async def main():
    display_logo()
    
    tokens = await read_tokens()
    if not tokens:
        return  

    tasks = [handle_account(token, i + 1) for i, token in enumerate(tokens)]
    await asyncio.gather(*tasks)

# ✅ Fix for Windows while keeping compatibility with other systems
if __name__ == "__main__":
    if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
