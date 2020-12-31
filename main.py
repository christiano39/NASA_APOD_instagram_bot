from dotenv import load_dotenv
load_dotenv()

from instabot import Bot
import schedule
import time
import requests
import urllib.request
from PIL import Image, ImageOps
import os
import pytube

bot = Bot()

usr = os.getenv("USER")
pwd = os.getenv("PASSWORD")
api_key = os.getenv("API_KEY")

def post_video(photo_data):
    video_url = dict(photo_data.json())['url']
    date = dict(photo_data.json())['date']
    description = dict(photo_data.json())['explanation']
    title = dict(photo_data.json())['title']
    
    youtube = pytube.YouTube(video_url)
    video = youtube.streams.get_highest_resolution()
    print("downloading...")
    video.download('./photos', filename = "video")
    print("download complete")

    caption = f"""
        {date}
        {title}
        .
        .
        .
        {description}
    """

    bot.login(username = usr, password = pwd)
    bot.upload_video(f"./photos/video.mp4", caption)
    bot.logout()

    if os.path.exists("./photos/video.mp4.REMOVE_ME"):
        os.remove("./photos/video.mp4.REMOVE_ME")

def post_photo():
    # Delete config that throws errors if exists
    if os.path.exists(f"./config/{usr}_uuid_and_cookie.json"):
        os.remove(f"./config/{usr}_uuid_and_cookie.json")
    
    # Get the data from NASA API
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    photo_data = requests.get(url)
    print(photo_data.json())

    # Video upload
    if dict(photo_data.json())['media_type'] == 'video':
        post_video(photo_data)
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

post_photo()