import pygame
import time
import soundfile as sf
import os
from mutagen.mp3 import MP3

class AudioManager:

    def __init__(self):
        pygame.mixer.init()

    def play_audio(self, file_path, sleep_during_playback=True, delete_file=False, play_using_music=True):
        """
        Parameters:
        file_path (str): path to the audio file
        sleep_during_playback (bool): means program will wait for length of audio file before returning
        delete_file (bool): means file is deleted after playback (note that this shouldn't be used for multithreaded function calls)
        play_using_music (bool): means it will use Pygame Music, if false then uses pygame Sound instead
        """
        print(f"Playing file with pygame: {file_path}")
        pygame.mixer.init()
        if play_using_music:
            # Pygame Mixer only plays one file at a time, but audio doesn't glitch
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
        else:
            # Pygame Sound lets you play multiple sounds simultaneously, but the audio glitches for longer files
            pygame_sound = pygame.mixer.Sound(file_path) 
            pygame_sound.play()

        if sleep_during_playback:
            # Calculate length of the file, based on the file format
            _, ext = os.path.splitext(file_path) # Get the extension of this file
            if ext.lower() == '.wav':
                wav_file = sf.SoundFile(file_path)
                file_length = wav_file.frames / wav_file.samplerate
                wav_file.close()
            elif ext.lower() == '.mp3':
                mp3_file = MP3(file_path)
                file_length = mp3_file.info.length
            else:
                print("Cannot play audio, unknown file type")
                return

            # Sleep until file is done playing
            time.sleep(file_length)

            # Delete the file
            if delete_file:
                # Stop pygame so file can be deleted
                # Note, this can cause issues if this function is being run on multiple threads, since it quit the mixer for the other threads too
                pygame.mixer.music.stop()
                pygame.mixer.quit()

                try:  
                    os.remove(file_path)
                    print(f"Deleted the audio file.")
                except PermissionError:
                    print(f"Couldn't remove {file_path} because it is being used by another process.")