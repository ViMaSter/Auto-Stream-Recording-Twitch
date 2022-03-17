# Auto Stream Recording Twitch

Python script for auto recording streams.
Thanks for source script to [junian](https://gist.github.com/junian/b41dd8e544bf0e3980c971b0d015f5f6)

# Requirements

- [Python 3](https://www.python.org/downloads/)
- [Twitch Chat Downloader](https://github.com/PetterKraabol/Twitch-Chat-Downloader) (optional)
- [Streamlink](https://github.com/streamlink/streamlink)
- [FFmpeg](http://ffmpeg.org/download.html)

# How to get client_id and client_secret:

1. Go to https://dev.twitch.tv/console/apps
2. Login
3. Press "+ Register Your Application"
4. Name: Enter any name you like
5. OAuth Redirect URLs: http://localhost
6. Category: Website Integration
7. Press "Create"
8. Find the registered application in the list and press "Manage"
9. You will see `Client ID`, which is `client_id`
10. Press on "New Secret", this will generate `client_secret`
11. You are done

# Installing

1. Install Python 3
2. Streamlink
3. Download ffmpeg
4. Download script
5. Change config options:

- client_id - Get this from previous section guide
- client_secret - Get this from previous section guide
- ffmpeg_path - directory of ffmpeg if on Windows and ffmpeg.exe is not in path
- output_path - where to output recorded streams
- refresh - how often to check if stream is online in seconds
- username - name of twitch channel (ex. forsen)
- quality - single quality or separated by comma (ex. "720p,720p60,best")

Example config file content:
{
"client_id": "h9wqpoxrb3cxaxmxas0ee4olvzuo0p",
"client_secret": "8rc0xfpgerer0set41ffxzd9799cpa",
"ffmpeg_path": "",
"output_path": "twitch",
"refresh": 5,
"username": "forsen",
"quality": "720p,720p60,best"
}

6. Do: `pip install -r requirements.txt`
7. Do: `python Auto_Recording_Twitch.py`
