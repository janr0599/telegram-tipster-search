from flask import Flask, render_template, request, jsonify
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from dotenv import load_dotenv
import asyncio
import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Set up TelegramClient using environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')

async def get_channel_stats(client, channel_username):
    try:
        # Get the channel entity
        channel = await client.get_entity(channel_username)
        
        # Get full channel info
        full_channel = await client(GetFullChannelRequest(channel))
        
        # Basic channel info
        channel_info = {
            'title': full_channel.chats[0].title,
            'username': full_channel.chats[0].username,
            'subscribers': full_channel.full_chat.participants_count,
            'recent_posts': []
        }
        
        # Fetch recent posts
        async for message in client.iter_messages(channel, limit=10):
            channel_info['recent_posts'].append({
                'id': message.id,
                'text': message.message,
                'views': message.views,
                "date": message.date
                # 'forwards': message.forwards,
                # 'reactions': message.reactions.results if message.reactions else []
            })
        
        return channel_info
    
    except Exception as e:
        print(f"An error occurred while fetching channel stats: {e}")
        return {}

async def search_groups(keywords):
    async with TelegramClient('session_name', api_id, api_hash) as client:
        try:
            result = []
            for keyword in keywords:
                search_result = await client(SearchRequest(q=keyword, limit=10))
                result += search_result.chats

            groups = []
            for chat in result:
                average_views = None  # Initialize average_views
                
                if hasattr(chat, 'username') and chat.username:
                    chat_url = f"https://t.me/{chat.username}"
                    channel_stats = await get_channel_stats(client, chat.username)  # Get channel stats

                    # Ensure channel_stats contains 'recent_posts'
                    if 'recent_posts' in channel_stats:
                        views = [post['views'] for post in channel_stats['recent_posts'] if post['views'] is not None]
                        if views:  # Check if the list is not empty
                            total_views = sum(views)
                            average_views = total_views / len(views)
                            rounded_views = round(average_views)
                        else:
                            average_views = 0
                    else:
                        average_views = 0
                else:
                    chat_url = None
                    channel_stats = {} 

                groups.append({
                    'id': chat.id,
                    'title': chat.title,
                    'url': chat_url,
                    'members': chat.participants_count,
                    'views': rounded_views if rounded_views is not None else 'N/A',
                    'last_message_date': channel_stats['recent_posts'][0]['date'] if 'recent_posts' in channel_stats and channel_stats['recent_posts'] else 'N/A'  # Handle the case where there are no views
                })

                print(rounded_views if rounded_views is not None else 'N/A')
                print(channel_stats)

            return groups

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
