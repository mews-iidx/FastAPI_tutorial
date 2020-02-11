from typing import List

from fastapi import FastAPI, File, UploadFile
from starlette.responses import HTMLResponse
from PIL import Image
import io

import cv2
import numpy as np

app = FastAPI()


def byte2cv(img_binary):
	img_binarystream = io.BytesIO(img_binary)
	img_pil = Image.open(img_binarystream)
	img_numpy = np.asarray(img_pil)
	img_numpy_bgr = cv2.cvtColor(img_numpy, cv2.COLOR_RGBA2BGR)
	return img_numpy_bgr

@app.post("/files/")
async def create_files(files: List[bytes] = File(...)):
    for idx, file in enumerate(files):
        cv_img = byte2cv(file)
        #img = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR) # cv2.IMREAD_COLOR in OpenCV 3.1
        cv2.imwrite('img{}.jpg'.format(idx), cv_img)

    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    fnames = []
    for idx, f in enumerate(files):
        fnames.append(f.filename)
        cv_img = byte2cv(f.file.read())
        cv2.imwrite(f.filename, cv_img)
    return {'message' : 'file saved', 'files': fnames}
            


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
