from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from werkzeug.utils import secure_filename
import zipfile
from datetime import datetime
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "static/downloads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

# ✅ Ensure folder exists before clearing
def clear_folder(path):
    os.makedirs(path, exist_ok=True)
    for file in os.listdir(path):
        os.remove(os.path.join(path, file))

@app.route("/", methods=["GET", "POST"])
def index():
    clips = []
    if request.method == "POST":
        # ✅ Check if video file is actually uploaded
        if "video" not in request.files or request.files["video"].filename == "":
            return "No video file uploaded", 400

        clear_folder(UPLOAD_FOLDER)
        clear_folder(OUTPUT_FOLDER)

        video = request.files["video"]
        filename = secure_filename(video.filename)
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        video.save(video_path)

        starts = request.form.getlist("start")
        ends = request.form.getlist("end")

        for i, (start, end) in enumerate(zip(starts, ends)):
            try:
                h1, m1, s1 = map(int, start.strip().split(":"))
                h2, m2, s2 = map(int, end.strip().split(":"))
                start_sec = h1 * 3600 + m1 * 60 + s1
                end_sec = h2 * 3600 + m2 * 60 + s2
            except:
                continue

            out_name = f"clip_{i+1}.mp4"
            out_path = os.path.join(OUTPUT_FOLDER, out_name)

            cmd = [
                "ffmpeg",
                "-ss", str(start_sec),
                "-to", str(end_sec),
                "-i", video_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                out_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

            clips.append(out_name)

        # Create ZIP
        zip_path = os.path.join(OUTPUT_FOLDER, "all_clips.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for clip in clips:
                clip_path = os.path.join(OUTPUT_FOLDER, clip)
                zipf.write(clip_path, arcname=clip)

        return render_template("index.html", clips=clips, zip_file="all_clips.zip")

    return render_template("index.html", clips=[], zip_file=None)

@app.route("/download/<filename>")
def download_clip(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(debug=True)
if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    port = int(os.environ.get("PORT", 5000))  # Use Render's port
    app.run(host="0.0.0.0", port=port)
