from audio_player import AudioManager
from obs_websockets import OBSWebsocketsManager
from azure_text_to_speech import AzureTTSManager

class TTSManager:
    azuretts_manager = AzureTTSManager()
    audio_manager = AudioManager()
    obswebsockets_manager = OBSWebsocketsManager()

    user1_voice_name = "en-US-DavisNeural"
    user1_voice_style = "random"
    user2_voice_name = "en-US-TonyNeural"
    user2_voice_style = "random"
    user3_voice_name = "en-US-JaneNeural"
    user3_voice_style = "random"

    def __init__(self):
        file_path = self.azuretts_manager.text_to_audio("Chat God App is now running!") # Say some shit when the app starts
        self.audio_manager.play_audio(file_path, True, True, True)

    def update_voice_name(self, user_number, voice_name):
        if user_number == "1":
            self.user1_voice_name = voice_name
        elif user_number == "2":
            self.user2_voice_name = voice_name
        elif user_number == "3":
            self.user3_voice_name = voice_name
        
    def update_voice_style(self, user_number, voice_style):
        if user_number == "1":
            self.user1_voice_style = voice_style
        elif user_number == "2":
            self.user2_voice_style = voice_style
        elif user_number == "3":
            self.user3_voice_style = voice_style

    def text_to_audio(self, text, user_number):
        if user_number == "1":
            voice_name = self.user1_voice_name
            voice_style = self.user1_voice_style
        elif user_number == "2":
            voice_name = self.user2_voice_name
            voice_style = self.user2_voice_style
        elif user_number == "3":
            voice_name = self.user3_voice_name
            voice_style = self.user3_voice_style

        tts_file = self.azuretts_manager.text_to_audio(text, voice_name, voice_style)

        # OPTIONAL: Use OBS Websockets to enable the Move plugin filter
        if user_number == "1":
            self.obswebsockets_manager.set_filter_visibility("Line In", "Audio Move - DnD Player 1", True)
        elif user_number == "2":
            self.obswebsockets_manager.set_filter_visibility("Line In", "Audio Move - DnD Player 2", True)
        elif user_number == "3":
            self.obswebsockets_manager.set_filter_visibility("Line In", "Audio Move - DnD Player 3", True)

        self.audio_manager.play_audio(tts_file, True, True, True)

        if user_number == "1":
            self.obswebsockets_manager.set_filter_visibility("Line In", "Audio Move - DnD Player 1", False)
        elif user_number == "2":
            self.obswebsockets_manager.set_filter_visibility("Line In", "Audio Move - DnD Player 2", False)
        elif user_number == "3":
            self.obswebsockets_manager.set_filter_visibility("Line In", "Audio Move - DnD Player 3", False)
