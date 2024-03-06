import numpy as np
import torch
import whisper

audio_model = whisper.load_model("base.en")


def whisper_queue(queue):
    try:
        # audio_data = b''.join(queue)
        audio_np = np.frombuffer(queue, dtype=np.int16).astype(np.float32) / 32768.0
        # Read the transcription.
        result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
        text = result['text'].strip()
        return text
    except Exception as err:
        print("whisper error:", err)
        return "sorry,riva is busy now"
