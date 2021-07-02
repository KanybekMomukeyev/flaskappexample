import argparse
from typing import List
import cv2
import matplotlib.pyplot as plt
from path import Path
from word_detector import detect_words, prepare_img

import uuid
import os
from PIL import Image


from flask import Flask
app = Flask(__name__)


@app.route("/")
def hello():
    return {"Hello": "World"}


def get_img_files(data_dir: Path) -> List[Path]:
    """return all image files contained in a folder"""
    res = []
    for ext in ['*.png', '*.jpg', '*.bmp']:
        res += Path(data_dir).files(ext)
    return res

# python main.py --data ../data/page --img_height 1000 --theta 5


path = os.getcwd()
SAVE_FOLDER = os.path.join(path, 'uploads/')


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

        # for det in res:
        #     imagePath222 = uuid.uuid4().hex + ".png"
        #     im = Image.fromarray(det.img)
        #     im.save(SAVE_FOLDER+imagePath222)
        #     # im.save('test.png')
        #     # print(f'Processing file {det.img}')
        #     print('----------------------')

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
