'''
# Written by DougDoug, with help from Banana
# You are welcome to adapt/use this code for whatever you'd like. Credit is appreciated but not necessary.

SETUP:
1) This was written in Python 3.9.2. Run "pip install -r requirements.txt" to install all modules.
2) This uses the twitchio module to connect to your Twitch channel.
First you must generate a Access Token for your account. You can do this at: https://twitchtokengenerator.com/
Then set the Acccess Token as a windows environment variable named TWITCH_ACCESS_TOKEN
You can see where this is accessed in the __init__ function of the Bot class below.
3) This uses Microsoft Azure's TTS service for the text-to-speech voices. 
First you must make an account and sign up for Microsoft Azure's services.
Then use their site to generate an access key and region for the text-to-speech service.
Then, set these as windows environment variables named AZURE_TTS_KEY and AZURE_TTS_REGION.
You can see where this is accessed in the __init__ function of the AzureTTSManager class in azure_text_to_speech.py.
4) Optionally, you can use OBS Websockets and an OBS plugin to make images move while talking.
First open up OBS. Make sure you're running version 28.X or later.
Click Tools, then WebSocket Server Settings.
Make sure "Enable WebSocket server" is checked. Make sure Server Port is '4455', and set the Server Password to 'TwitchChat9'.
Next install the Move OBS plugin: https://obsproject.com/forum/resources/move.913/
Now you can use the plugin to add a filter to an audio source that will change an image's transform based on the audio waveform.
For example, I have a filter that will move each of the player images whenever text-to-speech audio is playing.
Lastly, in the voices_manager.py code, update the OBS section so that it will turn the corresponding filters on and off when text-to-speech audio is being played.
Note that OBS must be open when you're running this code, otherwise OBS WebSockets won't be able to connect.
If you don't need the images to move while talking, you can just delete the OBS portions of the code.

BASIC APP USAGE:
1) Run chat_god_app.py and then open up http://127.0.0.1:5000 on a browser or as a browser source in OBS
2) You can enter a user's name in the "Choose User" field and hit enter to manually assign them as that player.
Alternatively, viewers can join the pool of potential players by typing !player1, !player2, or !player3.
Then, when you hit Pick Random, it will pick one of the viewers randomly from that player pool.
3) Once a user is picked, their message will be read out loud via Azure TTS.
You can select the voice and the voice style using the drop down menus.
If a user starts their message with (angry), (cheerful), (excited), (hopeful), (sad), (shouting), (shout), (terrified), (unfriendly), (whispering), (whisper), or (random), it will automatically use that voice style
'''

from twitchio.ext import commands
from twitchio import *
from datetime import datetime, timedelta
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
import asyncio
import threading
import pytz
import random 
import os
from voices_manager import TTSManager

socketio = SocketIO
app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")
print(socketio.async_mode)
 
@app.route("/")
def home():
    return render_template('index.html') #redirects to index.html in templates folder

@socketio.event
def connect(): #when socket connects, send data confirming connection
    socketio.emit('message_send', {'message': "Connected successfully!", 'current_user': "Temp User", 'user_number': "1"})

@socketio.on("tts")
def toggletts(value):
    print("TTS: Received the value " + str(value['checked']))
    if value['user_number'] == "1":
        bot.tts_enabled_1 = value['checked']
    elif value['user_number'] == "2":
        bot.tts_enabled_2 = value['checked']
    elif value['user_number'] == "3":
        bot.tts_enabled_3 = value['checked']

@socketio.on("pickrandom")
def pickrandom(value):
    bot.randomUser(value['user_number'])
    print("Getting new random user for user " + value['user_number'])

@socketio.on("choose")
def chooseuser(value):
    if value['user_number'] == "1":
        bot.current_user_1 = value['chosen_user'].lower()
        socketio.emit('message_send',
            {'message': f"{bot.current_user_1} was picked!",
            'current_user': f"{bot.current_user_1}",
            'user_number': value['user_number']})
    elif value['user_number'] == "2":
        bot.current_user_2 = value['chosen_user'].lower()
        socketio.emit('message_send',
            {'message': f"{bot.current_user_2} was picked!",
            'current_user': f"{bot.current_user_2}",
            'user_number': value['user_number']})
    elif value['user_number'] == "3":
        bot.current_user_3 = value['chosen_user'].lower()
        socketio.emit('message_send',
            {'message': f"{bot.current_user_3} was picked!",
            'current_user': f"{bot.current_user_3}",
            'user_number': value['user_number']})

@socketio.on("voicename")
def choose_voice_name(value):
    if (value['voice_name']) != None:
        bot.update_voice_name(value['user_number'], value['voice_name'])
        print("Updating voice name to: " + value['voice_name'])

@socketio.on("voicestyle")
def choose_voice_style(value):
    if (value['voice_style']) != None:
        bot.update_voice_style(value['user_number'], value['voice_style'])
        print("Updating voice style to: " + value['voice_style'])


class Bot(commands.Bot):
    current_user_1 = None
    current_user_2 = None
    current_user_3 = None
    tts_enabled_1 = True
    tts_enabled_2 = True
    tts_enabled_3 = True
    keypassphrase_1 = "!player1"
    keypassphrase_2 = "!player2"
    keypassphrase_3 = "!player3"
    user_pool_1 = {} #dict of username and time last chatted
    user_pool_2 = {} #dict of username and time last chatted
    user_pool_3 = {} #dict of username and time last chatted
    seconds_active = 450 # of seconds until a chatter is booted from the list
    max_users = 2000 # of users who can be in user pool
    tts_manager = None

    def __init__(self):
        self.tts_manager = TTSManager()

        #connects to twitch channel
        super().__init__(token=os.getenv('TWITCH_ACCESS_TOKEN'), prefix='?', initial_channels=['dougdoug'])
    
    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        await bot.process_message(message)

    async def process_message(self, message: Message):
        # print("We got a message from this person: " + message.author.name)
        # print("Their message was " + message.content)

        # If this is our current_user, read out their message
        if message.author.name == bot.current_user_1:
            socketio.emit('message_send',
                {'message': f"{message.content}",
                'current_user': f"{bot.current_user_1}",
                'user_number': "1"})
            if bot.tts_enabled_1:
                bot.tts_manager.text_to_audio(message.content, "1")
        elif message.author.name == bot.current_user_2:
            socketio.emit('message_send',
                {'message': f"{message.content}",
                'current_user': f"{bot.current_user_2}",
                'user_number': "2"})
            if bot.tts_enabled_2:
                bot.tts_manager.text_to_audio(message.content, "2")
        elif message.author.name == bot.current_user_3:
            socketio.emit('message_send',
                {'message': f"{message.content}",
                'current_user': f"{bot.current_user_3}",
                'user_number': "3"})
            if bot.tts_enabled_3:
                bot.tts_manager.text_to_audio(message.content, "3")

        # Add this chatter to the user_pool
        if message.content == bot.keypassphrase_1:
            if message.author.name.lower() in bot.user_pool_1: # Remove this chatter from pool if they're already there
                bot.user_pool_1.pop(message.author.name.lower())
            bot.user_pool_1[message.author.name.lower()] = message.timestamp # Add user to end of pool with new msg time
            # Now we remove the oldest viewer if they're past the activity threshold, or if we're past the max # of users
            activity_threshold = datetime.now(pytz.utc) - timedelta(seconds=bot.seconds_active) # calculate the cutoff time
            oldest_user = list(bot.user_pool_1.keys())[0] # The first user in the dict is the user who chatted longest ago
            if bot.user_pool_1[oldest_user].replace(tzinfo=pytz.utc) < activity_threshold or len(bot.user_pool_1) > bot.max_users:
                bot.user_pool_1.pop(oldest_user) # remove them from the list
                if len(bot.user_pool_1) == bot.max_users:
                    print(f"{oldest_user} was popped due to hitting max users")
                else:
                    print(f"{oldest_user} was popped due to not talking for {bot.seconds_active} seconds")
        elif message.content == bot.keypassphrase_2:
            if message.author.name.lower() in bot.user_pool_2: # Remove this chatter from pool if they're already there
                bot.user_pool_2.pop(message.author.name.lower())
            bot.user_pool_2[message.author.name.lower()] = message.timestamp # Add user to end of pool with new msg time
            # Now we remove the oldest viewer if they're past the activity threshold, or if we're past the max # of users
            activity_threshold = datetime.now(pytz.utc) - timedelta(seconds=bot.seconds_active) # calculate the cutoff time
            oldest_user = list(bot.user_pool_2.keys())[0] # The first user in the dict is the user who chatted longest ago
            if bot.user_pool_2[oldest_user].replace(tzinfo=pytz.utc) < activity_threshold or len(bot.user_pool_2) > bot.max_users:
                bot.user_pool_2.pop(oldest_user) # remove them from the list
                if len(bot.user_pool_2) == bot.max_users:
                    print(f"{oldest_user} was popped due to hitting max users")
                else:
                    print(f"{oldest_user} was popped due to not talking for {bot.seconds_active} seconds")
        elif message.content == bot.keypassphrase_3:
            if message.author.name.lower() in bot.user_pool_3: # Remove this chatter from pool if they're already there
                bot.user_pool_3.pop(message.author.name.lower())
            bot.user_pool_3[message.author.name.lower()] = message.timestamp # Add user to end of pool with new msg time
            # Now we remove the oldest viewer if they're past the activity threshold, or if we're past the max # of users
            activity_threshold = datetime.now(pytz.utc) - timedelta(seconds=bot.seconds_active) # calculate the cutoff time
            oldest_user = list(bot.user_pool_3.keys())[0] # The first user in the dict is the user who chatted longest ago
            if bot.user_pool_3[oldest_user].replace(tzinfo=pytz.utc) < activity_threshold or len(bot.user_pool_3) > bot.max_users:
                bot.user_pool_3.pop(oldest_user) # remove them from the list
                if len(bot.user_pool_3) == bot.max_users:
                    print(f"{oldest_user} was popped due to hitting max users")
                else:
                    print(f"{oldest_user} was popped due to not talking for {bot.seconds_active} seconds")
                
                
    #picks a random user from the queue
    def randomUser(this, user_number):
        try:
            if user_number == "1":
                bot.current_user_1 = random.choice(list(bot.user_pool_1.keys()))
                socketio.emit('message_send',
                    {'message': f"{bot.current_user_1} was picked!",
                    'current_user': f"{bot.current_user_1}",
                    'user_number': user_number})
                print("Random User is: " + bot.current_user_1)
            elif user_number == "2":
                bot.current_user_2 = random.choice(list(bot.user_pool_2.keys()))
                socketio.emit('message_send',
                    {'message': f"{bot.current_user_2} was picked!",
                    'current_user': f"{bot.current_user_2}",
                    'user_number': user_number})
                print("Random User is: " + bot.current_user_2)
            elif user_number == "3":
                bot.current_user_3 = random.choice(list(bot.user_pool_3.keys()))
                socketio.emit('message_send',
                    {'message': f"{bot.current_user_3} was picked!",
                    'current_user': f"{bot.current_user_3}",
                    'user_number': user_number})
                print("Random User is: " + bot.current_user_3)
        except Exception:
            return

    def update_voice_name(this, user_number, voice_name):
        bot.tts_manager.update_voice_name(user_number, voice_name)

    def update_voice_style(this, user_number, voice_style):
        bot.tts_manager.update_voice_style(user_number, voice_style)


def startBot():
    global bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = Bot()
    bot.run()

if __name__=='__main__':
    
    global bot_thread
    bot_thread = threading.Thread(target=startBot)
    bot_thread.start()
    
    socketio.run(app)
