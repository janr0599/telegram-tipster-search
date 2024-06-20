from flask import Flask, render_template, request, jsonify
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
import asyncio
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Set up TelegramClient using environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')

async def search_groups(keywords):
    async with TelegramClient('session_name', api_id, api_hash) as client:
        try:
            result = []
            for keyword in keywords:
                search_result = await client(SearchRequest(q=keyword, limit=10))
                result += search_result.chats

            return [{'id': chat.id, 'title': chat.title} for chat in result]

        except Exception as e:
            print(f"Error searching for groups: {e}")
            return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_groups', methods=['POST'])
def search_groups_handler():
    try:
        data = request.get_json()
        if not data or 'keywords' not in data:
            return jsonify({'error': 'Keywords not provided in JSON format'}), 400

        keywords = data['keywords']
        groups = asyncio.run(search_groups(keywords))
        return jsonify({'status': 'success', 'data': groups}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)