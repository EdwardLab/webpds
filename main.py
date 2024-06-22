import hashlib
from flask import Flask, request, send_file, render_template
from datetime import datetime, timedelta
import os

app = Flask(__name__)
DPFilesPWD = "testpwd123@"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    generate_time = datetime.now().strftime("%Y%m%d%H%M%S")
    token = generate_token(filename, generate_time)
    if get_file_size(filename) == False:
        return f'Sorry, the file: {filename} was not found'
    expiration_time = calculate_expiration_time(get_file_size(filename))

    return render_template('download.html', filename=filename, token=token,
                           generate_time=generate_time, expiration_time=expiration_time)


@app.route('/<path:filename>')
def download_file(filename):
    token = request.args.get('token')
    generate_time = request.args.get('generate_time')

    if token != generate_token(filename, generate_time):
        return "Invalid token", 403

    file_path = os.path.join("root", filename).replace("\\", "/")

    file_size = get_file_size(filename)
    if file_size == 0:
        return "File not found", 404

    expiration_time = calculate_expiration_time(file_size)

    current_time = datetime.now()
    generate_time = datetime.strptime(generate_time, "%Y%m%d%H%M%S")
    expiration_datetime = generate_time + timedelta(seconds=expiration_time)

    if current_time > expiration_datetime:
        return "The link has expired, please regenerate", 403

    return send_file(file_path, as_attachment=True)


def generate_token(filename, generate_time):
    token_string = f"{generate_time}{filename}{DPFilesPWD}@"
    md5 = hashlib.md5(token_string.encode()).hexdigest()
    return md5


def get_file_size(filename):
    file_path = os.path.join("root", filename).replace("\\", "/")
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    else:
        return False


def calculate_expiration_time(file_size):
    if file_size < 100 * 1024:  # Less than 100KB
        return 30
    elif 100 * 1024 <= file_size < 1 * 1024 * 1024:  # 100KB - 1MB
        return 50
    elif 1 * 1024 * 1024 <= file_size < 500 * 1024 * 1024:  # 1MB - 500MB
        return 30 * 60
    elif 500 * 1024 * 1024 <= file_size < 1 * 1024 * 1024 * 1024:  # 500MB - 1GB
        return 50 * 60
    elif 1 * 1024 * 1024 * 1024 <= file_size < 5 * 1024 * 1024 * 1024:  # 1GB - 5GB
        return 5 * 60 * 60
    elif 5 * 1024 * 1024 * 1024 <= file_size < 10 * 1024 * 1024 * 1024:  # 5GB - 10GB
        return 10 * 60 * 60
    else:  # Greater than 10GB
        return 24 * 60 * 60


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9000', debug=True)

