import argparse
from typing import List
import cv2
import matplotlib.pyplot as plt
from path import Path
from word_detector import detect_words, prepare_img

# -------------------------------------------------------------- #
import os
import shutil      # For File Manipulations like get paths, rename
from flask import Flask, flash, request, redirect, render_template, jsonify
from werkzeug.utils import secure_filename
import uuid
from PIL import Image
import io
from base64 import encodebytes


app = Flask(__name__)
app.secret_key = "secretkey"  # for encrypting the session
# It will allow below 16MB contents only, you can change it
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
path_current = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path_current, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def hello():
    return {"Hello": "World"}

# http://127.0.0.1:5000/upload


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')

            defaultPath = Path(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))

            # img = prepare_img(cv2.imread(defaultPath), 50) theta=7,
            img = prepare_img(cv2.imread(defaultPath), 1000)
            # python main.py --data ../data/page --img_height 1000 --theta 5
            res = detect_words(img,
                               kernel_size=25,
                               sigma=11,
                               theta=5,
                               min_area=100)

            for idx, det in enumerate(res):
                imagePath222 = uuid.uuid4().hex + '__' + str(idx+1) + ".png"
                im = Image.fromarray(det.img)
                im.save(Path(os.path.join(
                    app.config['UPLOAD_FOLDER'], imagePath222)))

            for file_img in get_img_files(UPLOAD_FOLDER):
                print(f' file {file_img}')

            encoded_imges = []
            for image_path in get_img_files(UPLOAD_FOLDER):
                encoded_imges.append(get_response_image(image_path))

            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

            return jsonify({'result': encoded_imges})
            # return {"filename": defaultPath}
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)


def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r')  # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')  # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode(
        'ascii')  # encode as base64
    return encoded_img


def get_img_files(data_dir: Path) -> List[Path]:
    """return all image files contained in a folder"""
    res = []
    for ext in ['*.png', '*.jpg', '*.bmp']:
        res += Path(data_dir).files(ext)
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=Path('../data/line'))
    parser.add_argument('--kernel_size', type=int, default=25)
    parser.add_argument('--sigma', type=int, default=11)
    parser.add_argument('--theta', type=int, default=7)
    parser.add_argument('--min_area', type=int, default=100)
    parser.add_argument('--img_height', type=int, default=50)
    parsed = parser.parse_args()

    for fn_img in get_img_files(parsed.data):
        print(f'Processing file {fn_img}')

        # load image and process it
        img = prepare_img(cv2.imread(fn_img), parsed.img_height)
        res = detect_words(img,
                           kernel_size=parsed.kernel_size,
                           sigma=parsed.sigma,
                           theta=parsed.theta,
                           min_area=parsed.min_area)

        # plot results
        plt.imshow(img, cmap='gray')
        for det in res:
            xs = [det.bbox.x, det.bbox.x, det.bbox.x +
                  det.bbox.w, det.bbox.x + det.bbox.w, det.bbox.x]
            ys = [det.bbox.y, det.bbox.y + det.bbox.h,
                  det.bbox.y + det.bbox.h, det.bbox.y, det.bbox.y]
            plt.plot(xs, ys)
        plt.show()


if __name__ == '__main__':
    main()
