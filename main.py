from flask import Flask, request, send_file
import subprocess
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
FFMPEG_PATH = './ffmpeg'  # ffmpeg static داخل نفس المجلد

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return open("index.html", encoding="utf-8").read()

@app.route('/merge', methods=['POST'])
def merge_subtitle():
    video = request.files['video']
    subtitle = request.files['subtitle']

    video_filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + "_" + video.filename)
    subtitle_filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + "_" + subtitle.filename)
    output_filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + "_output.mp4")

    video.save(video_filename)
    subtitle.save(subtitle_filename)

    # إعطاء صلاحيات تنفيذ لـ ffmpeg
    os.chmod(FFMPEG_PATH, 0o755)

    command = [
        FFMPEG_PATH,
        '-i', video_filename,
        '-vf', f"subtitles={subtitle_filename}",
        '-c:a', 'copy',
        output_filename
    ]

    try:
        subprocess.run(command, check=True)
        return send_file(output_filename, as_attachment=True)
    except subprocess.CalledProcessError:
        return "حدث خطأ أثناء الدمج", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
  
