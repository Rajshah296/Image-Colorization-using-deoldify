from flask import Flask, render_template, request, send_from_directory, send_file
import os
import io
from pathlib import Path
from PIL import Image
from deoldify.visualize import get_image_colorizer
import torch
import warnings

# Optimize PyTorch settings
torch.backends.cudnn.benchmark = True
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
        file = request.files.get("image")
        render_factor = int(request.form.get("render_factor", 25))  # Default 25
        watermarked = request.form.get("watermarked") == "yes"

        if file:
            # Process the image in memory
            image = Image.open(io.BytesIO(file.read()))
            filename = file.filename
            result_path = os.path.join(RESULT_FOLDER, filename)

            # Avoid reprocessing if the result already exists
            if not os.path.exists(result_path):
                temp_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(temp_path)  # Temporarily save
                image.close()  # Free memory

                # Perform colorization
                colorizer.plot_transformed_image(
                    path=temp_path, results_dir=Path(RESULT_FOLDER),
                    render_factor=render_factor, watermarked=watermarked
                )

                # Remove temp file to save space
                os.remove(temp_path)

            return render_template(
                "index.html",
                original_image=filename,
                colorized_image=filename,
                render_factor=render_factor,
                watermarked=watermarked,
            )

    return render_template("index.html", render_factor=25)  # Default render factor

@app.route("/results/<filename>")
def result_file(filename):
    return send_from_directory(RESULT_FOLDER, filename)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
