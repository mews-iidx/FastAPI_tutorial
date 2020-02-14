from typing import List
from fastapi import FastAPI, File, UploadFile
from starlette.responses import HTMLResponse, StreamingResponse
import os
import request_predict

from starlette.templating import Jinja2Templates 
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

import cv2
import io

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount('/uploadfiles/static', StaticFiles(directory='static'), name='static')

@app.post("/uploadfiles/")
async def create_upload_files(request: Request, files: List[UploadFile] = File(...)):
    fnames = []
    bins = []
    for  f in files:
        fnames.append(f.filename)
        bins.append(f.file.read())
    endpoint = os.getenv("ENDPOINT")
    rets = request_predict.request_bins(bins, endpoint)


#save images
    for f, b in zip(fnames, bins):
        img = request_predict.byte2cv(b)
        fname = os.path.join('static', f)
        cv2.imwrite(fname, img)

    return_dict = []
    for img_file, ret in zip( fnames, rets):
        placeholder = {
                'filename' : 'filename', 
                'classes' : [],
                'probs' : []
            }
        names = []
        probs = []
        for _, name, prob in ret:
            names.append(name)
            probs.append(prob)
        placeholder['filename'] = img_file
        print(placeholder['filename'])
        placeholder['classes'] = names
        placeholder['probs'] = probs

        return_dict.append(placeholder)
        
    for r in return_dict:
        print(r)
    return templates.TemplateResponse('upload_files.html', {'request' : request, 'results' : return_dict  })
            


@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse('index.html', {'request' : request})

