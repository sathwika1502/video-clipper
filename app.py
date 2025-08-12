import os
import subprocess
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CLIPS_FOLDER = "clips"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLIPS_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video = request.files["video"]
        start_time = request.form.get("start")
        end_time = request.form.get("end")

        if not video or not start_time or not end_time:
            return "Missing required inputs", 400

        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        video.save(video_path)

        start_sec = time_to_seconds(start_time)
        end_sec = time_to_seconds(end_time)
        out_filename = f"clip_{video.filename}"
        out_path = os.path.join(CLIPS_FOLDER, out_filename)

        # Build ffmpeg command
        cmd = [
            "ffmpeg",
            "-ss", str(start_sec),                # fast seek
            "-i", video_path,                     # input file
            "-to", str(end_sec - start_sec),      # clip duration
            "-c", "copy",                         # avoid re-encoding
            "-y",                                 # overwrite without asking
            out_path
        ]

        print("\n=== Running ffmpeg command ===")
        print(" ".join(cmd))

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            print("\n=== FFMPEG STDOUT ===")
            print(result.stdout)
            print("\n=== FFMPEG STDERR ===")
            print(result.stderr)

            if result.returncode != 0:
                print(f"FFmpeg failed with code {result.returncode}")
                return f"Error: FFmpeg failed. See logs.", 500

        except Exception as e:
            print(f"Exception running ffmpeg: {e}")
            return f"Error running ffmpeg: {e}", 500

        return send_file(out_path, as_attachment=True)

    return render_template("index.html")

def time_to_seconds(t):
    parts = list(map(int, t.split(":")))
    return parts[0] * 3600 + parts[1] * 60 + parts[2]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
