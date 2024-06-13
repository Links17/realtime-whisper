from flask import Flask, request, jsonify
import numpy as np
import torch
import whisper

audio_model = whisper.load_model("base.en")

app = Flask(__name__)


# 假设 audio_model 是您已经加载的模型，能够调用 transcribe 方法
# audio_model = ...

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    try:
        # 读取流式上传的音频数据
        audio_data = request.data
        # 转换为NumPy数组并进行转录
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
        text = result['text'].strip()
        return jsonify({'transcription': text})
    except Exception as err:
        print("whisper error:", err)
        return jsonify({'error': 'An error occurred during transcription.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
