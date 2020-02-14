import cv2
import os
import json
import cv2
import requests
import sys
import glob
import io
from PIL import Image
import numpy as np

payload_temp = {
    "data": {
        "names": ["image"],
        "ndarray": []
    }
}

headers = {'content-type': 'application/json'}


def byte2cv(img_binary):
	img_binarystream = io.BytesIO(img_binary)
	img_pil = Image.open(img_binarystream)
	img_numpy = np.asarray(img_pil)
	img_numpy_bgr = cv2.cvtColor(img_numpy, cv2.COLOR_RGBA2BGR)
	return np.array(img_numpy_bgr, dtype=np.uint8)


def request_bins(binaries, endpoint ):
    imgs = []
    for binary in binaries:
        image = byte2cv(binary)
        target_size = (224, 224)
        img_resized = cv2.resize(image, target_size)
        imgs.append(img_resized.tolist())

    payload_temp["data"]['ndarray'] = imgs

    resp = requests.post(
        endpoint,
        data=json.dumps(payload_temp),
        headers=headers
    )
    result_dict = json.loads(resp.content.decode('utf-8'))
    rets = result_dict['data']['ndarray']
    return rets

def request_predict(filenames, endpoint):
    imgs = []
    for filename in filenames:
        print(filename)
        image = cv2.imread(filename)
        print(image.shape)
        target_size = (224, 224)
        img_resized = cv2.resize(image, target_size)
        imgs.append(img_resized.tolist())

    payload_temp["data"]['ndarray'] = imgs

    resp = requests.post(
        endpoint,
        data=json.dumps(payload_temp),
        headers=headers
    )

    return resp

if __name__ == '__main__':
    
    input_dir = sys.argv[1]
    endpoint = sys.argv[2]
    files = glob.glob((os.path.join(input_dir, '*.jpg')))

    resp = request_predict(files, endpoint)

    if not resp.ok:
        print("ERROR EXIT FAILED")
        print(resp.content)
        quit(-100)
    result_dict = json.loads(resp.content.decode('utf-8'))
    rets = result_dict['data']['ndarray']

    for img_file, ret in zip( files, rets):
        print("------ {} prediction results ------ ".format(img_file))
        for _, name, prob in ret:
            print("  {} : {}".format(name, prob))
        print("")
