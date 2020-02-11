from typing import List
from fastapi import FastAPI, File, UploadFile
from starlette.responses import HTMLResponse
import os
import request_predict
app = FastAPI()

@app.post("/files/")
async def create_files(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}


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
