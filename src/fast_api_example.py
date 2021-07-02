import argparse
from typing import List

from cv2 import cv2
import matplotlib.pyplot as plt
# from path import Path
from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile
from word_detector import detect_words, prepare_img
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable
import os as os

app = FastAPI()


@app.post("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.post("/import_file")
def save_upload_file_tmp(kanofile: UploadFile = File(...)):

    print(kanofile.file.name)

    global upload_folder
    file_object = kanofile.file
    # create empty file to copy the file_object to
    upload_folder = open(os.path.join(upload_folder, kanofile.filename), 'wb+')
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()

    try:
        suffix = Path(kanofile.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(kanofile.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        kanofile.file.close()

    # --------------
    # img = prepare_img(cv2.imread(tmp_path), 50)

    # res = detect_words(img,
    #                    kernel_size=25,
    #                    sigma=11,
    #                    theta=7,
    #                    min_area=100)

    # plot results
    # plt.imshow(img, cmap='gray')
    # for det in res:
    #     xs = [det.bbox.x, det.bbox.x, det.bbox.x +
    #           det.bbox.w, det.bbox.x + det.bbox.w, det.bbox.x]
    #     ys = [det.bbox.y, det.bbox.y + det.bbox.h,
    #           det.bbox.y + det.bbox.h, det.bbox.y, det.bbox.y]
    #     plt.plot(xs, ys)
    # plt.show()
    # ---------
    return {
        "kanofile.filenamemod": kanofile.filename,
        "tmp_path": tmp_path,
        "kanofile.file.name": kanofile.file.name,
        "content_type": kanofile.content_type,
        "filename": kanofile.filename,
        "file_size": len(kanofile.filename),
    }


def get_img_files(data_dir: Path) -> List[Path]:
    """return all image files contained in a folder"""
    res = []
    for ext in ['*.png', '*.jpg', '*.bmp']:
        res += Path(data_dir).files(ext)
    return res
