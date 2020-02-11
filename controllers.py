from fastapi import FastAPI, File, UploadFile
from typing import List
from starlette.templating import Jinja2Templates  # new
from starlette.requests import Request
import os
import request_predict


app = FastAPI(
    title='FastAPIでつくるtoDoアプリケーション',
        description='FastAPIチュートリアル：FastAPI(とstarlette)でシンプルなtoDoアプリを作りましょう．',
            version='0.9 beta'
            )


# new テンプレート関連の設定 (jinja2)
templates = Jinja2Templates(directory="templates")
jinja_env = templates.env  # Jinja2.Environment : filterやglobalの設定用


def index(request: Request):
    return templates.TemplateResponse('index.html',
                                          {'request': request})
def admin(request: Request):
    return templates.TemplateResponse('admin.html', {'request': request, 'username': 'admin'})

@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    fnames = []
    bins = []
    for  f in files:
        fnames.append(f.filename)
        bins.append(f.file.read())
    endpoint = os.getenv("ENDPOINT")
    rets = request_predict.request_bins(bins, endpoint)

    placeholder = {
            'filename' : 'filename', 
            'classes' : [],
            'probs' : []
        }
    names = []
    probs = []

    return_dict = []
    for img_file, ret in zip( fnames, rets):
        for _, name, prob in ret:
            names.append(name)
            probs.append(prob)
        placeholder['filename'] = img_file
        placeholder['classes'] = names
        placeholder['probs'] = probs
        return_dict.append(placeholder)
        
    return {'return' : return_dict}
