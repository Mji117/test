from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
import subprocess
import os
import uuid

app = Flask(__name__)
socketio = SocketIO(app)

UPLOAD_FOLDER = 'uploads'
FFMPEG_PATH = './ffmpeg'  # تأكد من أنك وضعت ffmpeg في نفس المجلد

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge_subtitle():
    video = request.files['video']
    subtitle = request.files['subtitle']

    video_filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + "_" + video.filename)
    subtitle_filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + "_" + subtitle.filename)
    output_filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + "_output.mp4")

    video.save(video_filename)
    subtitle.save(subtitle_filename)

    # بدء المعالجة عبر WebSocket
    socketio.emit('processing_start', {'message': 'عملية الدمج بدأت'})

    command = [
        FFMPEG_PATH,
        '-i', video_filename,
        '-vf', f"subtitles={subtitle_filename}",
        '-c:a', 'copy',
        output_filename
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # مراقبة تقدم المعالجة
    for line in process.stderr:
        line = line.decode('utf-8')
        if "time=" in line:
            # استخراج الوقت المتقدم في المعالجة
            time_position = line.split("time=")[1].split(" ")[0]
            socketio.emit('progress_update', {'progress': time_position})

    process.wait()  # الانتظار حتى انتهاء المعالجة
    socketio.emit('processing_complete', {'message': 'تم الدمج بنجاح! يمكنك تحميل الفيديو الآن.'})

    return send_file(output_filename, as_attachment=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
