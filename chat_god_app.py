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
