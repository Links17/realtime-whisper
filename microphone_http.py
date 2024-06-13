import argparse
import os
import numpy as np
import speech_recognition as sr

from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform
import requests
import time
def stream_audio_data(data):
    """
    Generator function to yield audio data chunks.
    """
    yield data

def publish_http_stream(url, audio_data):
    """
    Function to send audio data as a stream to the given URL.
    """
    headers = {'Content-Type': 'application/octet-stream'}
    response = requests.post(url, data=stream_audio_data(audio_data), headers=headers, stream=True)
    if response.status_code == 200:
        print("Successfully sent audio data.")
    else:
        print(f"Failed to send audio data. Status code: {response.status_code}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the english model.")
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=2,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                 "Run this with 'list' to view available Microphones.", type=str)
    args = parser.parse_args()

    # The last time a recording was retrieved from the queue.
    phrase_time = None
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False

    # Important for linux users.
    # Prevents permanent application hang and crash by using the wrong Microphone
    if 'linux' in platform:
        mic_name = args.default_microphone
        if not mic_name or mic_name == 'list':
            print("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"Microphone with name \"{name}\" found")
            return
        else:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    source = sr.Microphone(sample_rate=16000, device_index=index)
                    break
    else:
        source = sr.Microphone(sample_rate=16000)

    record_timeout = args.record_timeout

    def record_callback(_, audio: sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        publish_http_stream("127.0.0.1:5000", data)

    with source:
        while True:
            recorder.adjust_for_ambient_noise(source)
            audio = recorder.listen(source, phrase_time_limit=record_timeout)
            record_callback(None, audio)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
    # recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)
    # recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)


if __name__ == "__main__":
    main()
