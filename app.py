from flask import Flask, render_template, request, jsonify
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from langdetect import detect
from datetime import datetime as dt
import re
from dotenv import load_dotenv
import asyncio
import os
from telethon.errors import FloodWaitError

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Set up TelegramClient using environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')

# Function to remove emojis and non-alphabetic characters
def clean_text(text):
    # Remove characters that are not Unicode letters or whitespace
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
    return text

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
            'recent_posts': [],
            'languages': []
        }
        
        # Fetch recent posts
        async for message in client.iter_messages(channel, limit=10):
            post_info = {
                'text': message.message,
                'views': message.views,
                'date': message.date,
                'language': 'unknown'  # Default language value
            }
            
            # Language detection for each post
            if message.message:
                try:
                    text = message.message
                    # Clean text (remove emojis and non-alphabetic characters)
                    cleaned_text = clean_text(text)
                    # Language detection
                    if cleaned_text.strip():  # Check if text is not empty after cleaning
                        language = detect(cleaned_text)
                    else:
                        language = 'unknown'
                except Exception as e:
                    print(f"Language detection error: {e}")
                    language = 'unknown'
                
                post_info['language'] = language
                channel_info['languages'].append(language)  # Store the language in the languages list
            
            channel_info['recent_posts'].append(post_info)
        
        return channel_info
    
    except FloodWaitError as e:
        print(f"Rate limit hit: Waiting for {e.seconds} seconds.")
        await asyncio.sleep(e.seconds)
        return await get_channel_stats(client, channel_username)
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
                if hasattr(chat, 'username') and chat.username:
                    chat_url = f"https://t.me/{chat.username}"
                    channel_stats = await get_channel_stats(client, chat.username)  # Get channel stats

                    # Calculate average views
                    if 'recent_posts' in channel_stats:
                        views = [post['views'] for post in channel_stats['recent_posts'] if post['views'] is not None]
                        if views:
                            total_views = sum(views)
                            average_views = total_views / len(views)
                            rounded_views = round(average_views)
                        else:
                            rounded_views = 'N/A'
                    else:
                        rounded_views = 'N/A'
                    
                    datetime = channel_stats['recent_posts'][0]['date'] if 'recent_posts' in channel_stats and channel_stats['recent_posts'] else 'N/A'

                    if datetime != 'N/A':
                        datetime_str = str(datetime)
                        datetime_obj = dt.fromisoformat(datetime_str)
                        date_str = datetime_obj.date().isoformat()
                    else:
                        date_str = 'N/A'

                    groups.append({
                        'id': chat.id,
                        'title': chat.title,
                        'url': chat_url,
                        'members': chat.participants_count,
                        'views': rounded_views,
                        'last_message_date': date_str,
                        'languages': channel_stats.get('languages', [])
                    })
                    print(rounded_views)
                    print(channel_stats)
                    print(date_str)
                else:
                    groups.append({
                        'id': chat.id,
                        'title': chat.title,
                        'url': None,
                        'members': chat.participants_count,
                        'views': 'N/A',
                        'last_message_date': 'N/A',
                        'languages': []
                    })
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
