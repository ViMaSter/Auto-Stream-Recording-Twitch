# Auto Stream Recording Twitch

Docker container for auto recording streams.
Thanks for the source script by [junian](https://gist.github.com/junian/b41dd8e544bf0e3980c971b0d015f5f6) and modifications done by [Effanuel](https://github.com/Effanuel/Auto-Stream-Recording-Twitch)

# Requirements

- [Docker](https://www.docker.com/)

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

# Installing

1. Install Docker
2. Download this repository
3. Run `docker build . -t streamrec`
4. Run and replace the variables surrounded by `[SQUARE_BRAKETS]` inside this command:
5. `docker run -v [ABSOLUTE_TARGET_PATH]:/app/twitch test python3 record.py [CLIENT_ID] [CLIENT_SECRET] [CHANNEL_NAME] [QUALITY]`
   1. `ABSOLUTE TARGET PATH`: Path to where the recordings will be stored
   2. `CLIENT_ID`: The obtained client id from twitch
   3. `CLIENT_SECRET`: The obtained client secret from twitch
   4. `CHANNEL_NAME`: Name of the twitch channel to record
   5. `QUALITY`: Explicit quality setting to use as seen in the twitch player or `best` or `worse`