from config import ALLOWED_EXTENSIONS
from flask import flash, request, redirect
from werkzeug.utils import secure_filename


def allowed_file(filename):
    """Check if the given file has an allowed extension."""
    
    if '.' not in filename:
        return False

    extension = filename.rsplit('.', 1)[1].lower()

    if extension in ALLOWED_EXTENSIONS:
        return True

    return False


def upload_file():
    """Upload file from request.files"""
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(f"static/img/{filename}")
        img_path = f"img/{filename}"
        return img_path
