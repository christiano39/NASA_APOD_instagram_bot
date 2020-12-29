from dotenv import load_dotenv
load_dotenv()

from instabot import Bot
import schedule
import time
import requests
import urllib.request
from PIL import Image, ImageOps
import os

bot = Bot()

usr = os.getenv("USER")
pwd = os.getenv("PASSWORD")
api_key = os.getenv("API_KEY")

def post_photo():
    # Delete config that throws errors if exists
    if os.path.exists(f"./config/{usr}_uuid_and_cookie.json"):
        os.remove(f"./config/{usr}_uuid_and_cookie.json")
    
    # Get the data from NASA API
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    photo_data = requests.get(url)
    print(photo_data.json())

    # Skip upload if video
    if dict(photo_data.json())['media_type'] == 'video':
        print('Cannot upload video, skipping...')
        return

    # Download photo from URL
    photo_url = dict(photo_data.json())['url']
    filename = photo_url.split('/')[-1]
    urllib.request.urlretrieve(photo_url, f"./photos/{filename}")

    # Resize image to square
    image = Image.open(f"./photos/{filename}")
    thumb = ImageOps.fit(image, (600, 600), Image.ANTIALIAS)
    thumb.save(f"./photos/{filename}", format='JPEG')

    # Create caption
    author = dict(photo_data.json())['copyright'] if 'copyright' in dict(photo_data.json()) else "Not credited"
    date = dict(photo_data.json())['date']
    description = dict(photo_data.json())['explanation']

    caption = f"""
        Credit: {author}
        {date}
        .
        .
        .
        {description}
    """
    
    # Login and upload photo
    bot.login(username = usr, password = pwd)
    bot.upload_photo(f"./photos/{filename}", caption)
    bot.logout()

# schedule.every().day.at("13:00").do(post_photo)

# while True:
#     schedule.run_pending()
#     time.sleep(1)

post_photo()