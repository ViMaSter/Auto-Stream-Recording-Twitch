# Auto Stream Recording Twitch v1.7.0 https://github.com/EnterGin/Auto-Stream-Recording-Twitch

# Please install latest release build of streamlink for proper work of the script
# https://github.com/streamlink/streamlink/releases

import requests
import os
import time
import json
import sys
import platform
import subprocess
import datetime
import getopt
import pytz
import traceback


class TwitchRecorder:
    def __init__(self):
        if not os.path.exists("config.json"):
            raise Exception("Config file doesn't exist")
        config_file = open('config.json')
        config = json.load(config_file)

        self.validate_config(config)
        
        self.client_id          = config["client_id"]                              # If you don't have client id then register new app: https://dev.twitch.tv/console/apps
        self.client_secret      = config["client_secret"]                               # Manage application -> new secret
        self.ffmpeg_path        = config["ffmpeg_path"]                    # Path to ffmpeg.exe. Leave blank if Linux or ffmpeg in env PATH
        self.refresh            = config["refresh"] if config["refresh"] else 5                            # Time between checking (5.0 is recommended)
        self.root_path          = config["output_path"] if config["output_path"] else "twitch"                    # path to recorded and processed streams
        self.username           = config["username"] 
        self.quality            = config["quality"]
        self.timezoneName       = 'Europe/Moscow'                  # name of timezone (list of timezones: https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones)
        self.oauth_tok_private  = ""                               # You can provide your private oauth token and record streams without ads or record sub-only streams (or leave blank if don't need), how to get oauth: https://imgur.com/a/j1Bg6JM
        self.chatdownload       = 1                                # 0 - disable chat downloading, 1 - enable chat downloading
        self.cmdstate           = 2                                # Windows: 0 - not minimazed cmd close after processing, 1 - minimazed cmd close after processing, 2 - minimazed cmd don't close after processing, 3 - no terminal, do in background
                                                                   # Linux:   0 - not minimazed terminal close after processing, 1 - not minimazed terminal don't close after processing, 2 - no terminal, do in background
        self.downloadVOD        = 0                                # 0 - disable VOD downloading after stream's ending, 1 - enable VOD downloading after stream's ending
        self.dont_ask_to_delete = 1                                # 0 - always ask to delete previous processed streams from recorded folder, 1 - don't ask, don't delete, 2 - don't ask, delete
        self.make_stream_folder = 1                                # 0 - don't make folders for each processed stream, 1 - make folders for each processed stream
        self.short_folder       = 0                                # 0 - date, title, game and username in processed VOD folder, 1 - only date in processed VOD folder
        self.hls_segments       = 3                                # 1-10 for live stream, it's possible to use multiple threads to potentially increase the throughput. 2-3 is enough
        self.hls_segmentsVOD    = 10                               # 1-10 for downloading vod, it's possible to use multiple threads to potentially increase the throughput
        self.streamlink_debug   = 0                                # 0 - don't show streamlink debug, 1 - show streamlink debug
        self.warning_windows    = 1                                # 0 - don't show warning windows (warnings will only be printed in terminal), 1 - show warning windows


    def validate_config(self, config):
        if len(config["client_id"]) != 30 or len(config["client_secret"]) != 30:
            raise Exception("No client id and secret provided or wrong format, length of 30 is require")
        if config["refresh"] is None:
            print('Defaulting to 5 refresh')
        if config["output_path"] is None:
            print('Defaulting to ./twitch/ directory')
        if len(config["username"]) == "":
            raise Exception("Add valid twitch channel username")
        qualities = config['quality'].split(',')
        for quality in qualities:
            if quality not in ['best', '720p', '720p60', '1080p', '1080p60', '480p']:
                raise Exception("Valid qualities are 720p, 720p60, 1080p, 1080p60, 480p. You can add multiple by separating with a comma (ex, '720p,720p60,best')")


    def run(self):
        # detect os
        if sys.platform.startswith('win32'):
            self.osCheck = 0
        elif True: # so that this works on Mac
            self.osCheck = 1
            if self.cmdstate == 3:
                self.cmdstate = 2
        else:
            print('Your OS might not be supported.\n')
            return

        # cmdstatecommand
        if self.osCheck == 0:
            if self.cmdstate == 2:
                self.cmdstatecommand = "/min cmd.exe /k".split()
            elif self.cmdstate == 1:
                self.cmdstatecommand = "/min".split()
            else:
                self.cmdstatecommand = "".split()
            self.main_cmd_window = "cmd.exe /c start".split()
        else:
            if self.cmdstate == 1:
                self.linuxstatecomma = "; exec bash'"
            elif self.cmdstate == 0:
                self.linuxstatecomma = "'"
            self.main_cmd_window = "gnome-terminal --".split()

        # self.timezoneName to number
        self.timezone = pytz.timezone(self.timezoneName).localize(datetime.datetime.now()).tzinfo._utcoffset.seconds/60/60

        # -v check
        if str(self.downloadVOD).isdigit() == False:
            print('-v can be only 0 or 1. Set to 0.\n')
            self.downloadVOD = 0
        else:
            self.downloadVOD = int(self.downloadVOD)

        # deleting previous processed streams from recorded folder
        if self.dont_ask_to_delete == 0:
            print('Do you want to delete previous processed streams from recorded folder? y/n')
            delete_recorded_ans = str(input())
        elif self.dont_ask_to_delete == 2:
            delete_recorded_ans = 'y'
        else:
            delete_recorded_ans = 'n'

        if delete_recorded_ans == 'y' or delete_recorded_ans == 'Y':
            self.cleanrecorded = 1
        else:
            self.cleanrecorded = 0

        # streamlink debug
        if self.streamlink_debug == 1:
            self.debug_cmd = "--loglevel trace".split()
        else:
            self.debug_cmd = "".split()

        if self.client_id == "" or self.client_secret == "":
            print("If you don't have client-id then register new app on following page:")
            print("https://dev.twitch.tv/console/apps")
            print("You have to set both client-id and client-secret.")
            return

        # start text
        print('Auto Stream Recording Twitch v1.7.0')
        print('Configuration:')
        print('OS: ' + "Windows " + platform.release() if self.osCheck == 0 else 'OS: ' + "Linux " + platform.release())
        print('Root path: ' + self.root_path)
        print('Ffmpeg path: ' + self.ffmpeg_path)
        print('Timezone: ' + self.timezoneName + ' ' + '(' + str(self.timezone) + ')')
        if self.chatdownload == 1:
            print('Chat downloading Enabled')
        else:
            print('Chat downloading Disabled')
        if self.downloadVOD == 1:
            print('VOD downloading Enabled')
        else:
            print('VOD downloading Disabled')

        # get oauth token
        self.oauth_token = self.get_oauth_token()

        # get user id
        self.get_channel_id()

        # path to recorded stream
        self.recorded_path = os.path.join(self.root_path, "recorded", self.username)

        # path to finished video, errors removed
        self.processed_path = os.path.join(self.root_path, "processed", self.username)

        # create directory for recordedPath and processedPath if not exist
        if(os.path.isdir(self.recorded_path) is False):
            os.makedirs(self.recorded_path)

        # make sure the interval to check user availability is not less than 1 second
        if(self.refresh < 1):
            print("Check interval should not be lower than 1 second.")
            self.refresh = 1
            print("System set check interval to 1 second.")

        print("Checking for", self.username, "every", self.refresh, "seconds. Record with", self.quality, "quality.")
        self.loopcheck()
    
    def get_oauth_token(self):
        try:
            return requests.post(f"https://id.twitch.tv/oauth2/token"
                                f"?client_id={self.client_id}"
                                f"&client_secret={self.client_secret}"
                                f"&grant_type=client_credentials").json()['access_token']
        except:
            return None

    def get_channel_id(self):
        self.getting_channel_id_error = 0
        self.user_not_found           = 0
        if self.oauth_token == None:
            self.getting_channel_id_error = 1
            return

        url = 'https://api.twitch.tv/helix/users?login=' + self.username
        try:
            r = requests.get(url, headers = {"Authorization" : "Bearer " + self.oauth_token, "Client-ID": self.client_id}, timeout = 15)
            r.raise_for_status()
            info = r.json()
            if info["data"] != []:
                self.channel_id = info["data"][0]["id"]
            else:
                self.user_not_found = 1
        except requests.exceptions.RequestException as e:
            self.getting_channel_id_error = 1
            print(f'\n{e}\n')

    def check_user(self):
        # 0: online,
        # 1: not found,
        # 2: error,
        # 3: channel id error

        info = None
        if self.user_not_found != 1 and self.getting_channel_id_error != 1:
            url    = 'https://api.twitch.tv/helix/channels?broadcaster_id=' + str(self.channel_id)
            status = 2
            try:
                r = requests.get(url, headers = {"Authorization" : "Bearer " + self.oauth_token, "Client-ID": self.client_id}, timeout = 15)
                r.raise_for_status()

                info   = r.json()
                status = 0
            except requests.exceptions.RequestException as e:
                if e.response != None:
                    if e.response.status_code == 401:
                        print(
                            '\nRequest to Twitch returned an error %s, trying to get new oauth_token...'
                            % (e.response.status_code)
                        )
                        self.getting_channel_id_error = 1
                    else:
                        print(
                            '\nRequest to Twitch returned an error %s, the response is:\n%s\n'
                            % (e.response.status_code, e.response)
                        )
                else:
                    print(f'\n{e}\n')
        elif self.user_not_found == 1:
            status = 1
        else:
            self.oauth_token = self.get_oauth_token()
            self.get_channel_id()
            status = 3

        return status, info

    def loopcheck(self):
        while True:
            uncrop = 0
            status, info = self.check_user()
            if status == 1:
                print("Username not found. Invalid username or typo.")
                time.sleep(self.refresh)
            elif status == 2:
                print(datetime.datetime.now().strftime("%Hh%Mm%Ss")," ","Unexpected error. Try to check internet connection or client-id. Will try again in", self.refresh, "seconds.")
                time.sleep(self.refresh)
            elif status == 3:
                print(datetime.datetime.now().strftime("%Hh%Mm%Ss")," ","Error with channel id or oauth token. Try to check internet connection or client-id and client-secret. Will try again in", self.refresh, "seconds.")
                time.sleep(self.refresh)
            elif status == 0:
                stream_title = str(info["data"][0]['title'])
                stream_title = "".join(x for x in stream_title if x.isalnum() or not x in ["/","\\",":","?","*",'"',">","<","|"]).replace('\n', '')

                present_date     = datetime.datetime.now().strftime("%Y%m%d")
                present_datetime = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")

                filename = present_datetime + "_" + stream_title + '_' + str(info["data"][0]['game_name']) + "_" + self.username + ".mp4"

                # clean filename from unecessary characters
                filename = "".join(x for x in filename if x.isalnum() or not x in ["/","\\",":","?","*",'"',">","<","|"]).replace('\n', '')

                recorded_filename = os.path.join(self.recorded_path, filename)

                # length check
                if len(recorded_filename) >= 260:
                    difference = len(stream_title) - len(recorded_filename) + 250
                    if difference < 0:
                        uncrop = 1
                    else:
                        stream_title      = stream_title[:difference]
                        filename          = present_datetime + "_" + stream_title + '_' + str(info["data"][0]['game_name']) + "_" + self.username + ".mp4"
                        filename          = "".join(x for x in filename if x.isalnum() or not x in ["/","\\",":","?","*",'"',">","<","|"]).replace('\n', '')
                        recorded_filename = os.path.join(self.recorded_path, filename)

                # start streamlink process
                subprocess.call(["streamlink", '--http-header', 'Authorization=OAuth ' + self.oauth_tok_private, "--hls-segment-threads", str(self.hls_segments), "--hls-live-restart", "--twitch-disable-hosting", "twitch.tv/" + self.username, self.quality, "--retry-streams", str(self.refresh)] + self.debug_cmd + ["-o", recorded_filename])

                print("Fixing is done. Going back to checking..")
                time.sleep(self.refresh)

def main(argv):
    twitch_recorder = TwitchRecorder()
    usage_message = 'Auto_Recording_Twitch.py -u <username> -q <quality> -v <download VOD 1/0>'
    try:
        opts, args = getopt.getopt(argv,"hu:q:v:",["username=","quality=", "vod="])
    except getopt.GetoptError:
        print (usage_message)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(usage_message)
            sys.exit()
        elif opt in ("-u", "--username"):
            twitch_recorder.username = arg
        elif opt in ("-q", "--quality"):
            twitch_recorder.quality = arg
        elif opt in ("-v", "--vod"):
            twitch_recorder.downloadVOD = arg

    twitch_recorder.run()

if __name__ == "__main__":
    main(sys.argv[1:])
