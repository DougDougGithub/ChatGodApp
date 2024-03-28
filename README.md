# ChatGodApp

Written by DougDoug, with help from Banana!
You are welcome to adapt/use this code for whatever you'd like. Credit is appreciated but not necessary.

## SETUP
1) This was written in Python 3.9.2. Install page here: https://www.python.org/downloads/release/python-392/

2) Run "pip install -r requirements.txt" to install all modules.

3) This uses the twitchio module to connect to your Twitch channel.
First you must generate a Access Token for your account. You can do this at: https://twitchtokengenerator.com/ , just make sure the Access Token has chat:read and chat:edit enabled.
Once you've generated an Access Token, set it as a windows environment variable named TWITCH_ACCESS_TOKEN.
Then update the TWITCH_CHANNEL_NAME variable in chat_god_app.py to the name of the twitch channel you are connecting to.

4) This uses Microsoft Azure's TTS service for the text-to-speech voices. 
First you must make an account and sign up for Microsoft Azure's services.
Then use their site to generate an access key and region for the text-to-speech service.
Then, set these as windows environment variables named AZURE_TTS_KEY and AZURE_TTS_REGION.

5) Optionally, you can use OBS Websockets and an OBS plugin to make images move while talking.
First open up OBS. Make sure you're running version 28.X or later.
Click Tools, then WebSocket Server Settings.
Make sure "Enable WebSocket server" is checked. Make sure Server Port is '4455', and set the Server Password to 'TwitchChat9'.
Next install the Move OBS plugin: https://obsproject.com/forum/resources/move.913/
Now you can use the plugin to add a filter to an audio source that will change an image's transform based on the audio waveform.
For example, I have a filter that will move each of the player images whenever text-to-speech audio is playing.
Lastly, in the voices_manager.py code, update the OBS section so that it will turn the corresponding filters on and off when text-to-speech audio is being played.
Note that OBS must be open when you're running this code, otherwise OBS WebSockets won't be able to connect.
If you don't need the images to move while talking, you can just delete the OBS portions of the code.

## BASIC APP USAGE

1) Run chat_god_app.py and then open up http://127.0.0.1:5000 on a browser or as a browser source in OBS

2) You can enter a user's name in the "Choose User" field and hit enter to manually assign them as that player.
Alternatively, viewers can join the pool of potential players by typing !player1, !player2, or !player3.
Then, when you hit Pick Random, it will pick one of the viewers randomly from that player pool.

3) Once a user is picked, their twitch messages will be automatically read out loud via Azure TTS.
You can change the voice and the voice style using the drop down menus on the web app.
If a user starts their message with (angry), (cheerful), (excited), (hopeful), (sad), (shouting), (shout), (terrified), (unfriendly), (whispering), (whisper), or (random), it will automatically use that voice style.
