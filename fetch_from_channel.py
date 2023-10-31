from telethon import TelegramClient
from google.oauth2.service_account import Credentials
import googleapiclient.discovery
import asyncio
from dotenv import load_dotenv
import os
import requests

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
sheet_id = os.getenv("GOOGLE_SHEET_ID")
channel_id = 'SOME_CHANNEL_NAME_OR_ID'  # This should be the channel's username or ID
bot_api_token = os.getenv("YOUR_TELEGRAM_BOT_TOKEN")  # Bot token from BotFather
bot_chat_id = os.getenv("YOUR_CHAT_ID")  # Chat ID where the bot will send messages

async def send_to_telegram(message):
    api_url = f'https://api.telegram.org/bot{bot_api_token}/sendMessage'
    try:
        response = requests.post(api_url, json={'chat_id': bot_chat_id, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)

async def insert_into_google_sheet(data):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    service = googleapiclient.discovery.build("sheets", "v4", credentials=creds)

    # Append data to sheet
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="Sheet1!A1",
        body={"values": [data]},
        valueInputOption="RAW"
    ).execute()

async def fetch_telegram_messages():
    async with TelegramClient('anon', api_id, api_hash) as client:
        # Fetch the last 10 messages from the channel
        async for message in client.iter_messages(channel_id, limit=10):
            data_to_insert = [message.id, message.text]
            # Insert the message into Google Sheet
            await insert_into_google_sheet(data_to_insert)
            # Send the message text to the bot chat
            await send_to_telegram(message.text)

async def main():
    while True:
        await fetch_telegram_messages()
        await asyncio.sleep(60)  # Pause for 60 seconds to avoid hitting rate limits

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
