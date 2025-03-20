from flask import Flask, render_template, request, send_from_directory
import os
from pathlib import Path
from deoldify.visualize import *

from deoldify.visualize import *
plt.style.use('dark_background')
torch.backends.cudnn.benchmark=True
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*?Your .*? set is empty.*?")

app = Flask(__name__)

# Set up directories for uploads and results
UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Initialize DeOldify Colorizer
colorizer = get_image_colorizer(artistic=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        render_factor = int(request.form["render_factor"])  # Get render factor from form
        watermarked = request.form.get("watermarked") == "yes"  # Get watermark option

        if file:
            # Save uploaded file
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Colorize the image
            result_path = os.path.join(RESULT_FOLDER, file.filename)
            colorizer.plot_transformed_image(
                path=file_path, results_dir=Path(RESULT_FOLDER),
                render_factor=render_factor, watermarked=watermarked
            )

            # Show images in the UI
            return render_template(
                "index.html",
                original_image=file.filename,
                colorized_image=file.filename,
                render_factor=render_factor,
                watermarked=watermarked,
            )

    return render_template("index.html", render_factor=25)  # Default render factor is 25

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/results/<filename>")
def result_file(filename):
    return send_from_directory(RESULT_FOLDER, filename)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)