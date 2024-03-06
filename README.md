# realtime-whisper

## 说明

使用openAI/whisper 作speech to text,并实时解析麦克风传输的数据

### 启动

```bash
python install -r requirements.txt
python mqtt_client.py
python microphone_utils.py
```

### 传输

通过MQTT作流式传输,并实时解析