import requests
import logging
import json
import base64

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Api:
    def __init__(self):
        self.end_point = "URL"
        self.photo = None
        self.video = None

    def set_photo(self, photo):
        self.photo = str(base64.b64encode(photo))

    def set_video(self, video):
        self.video = str(base64.b64encode(video))

    def _request(self, method, path, data=None):
        logger.info(f"{method} {self.end_point + path, data}")
        # resp = requests.request(method, self.end_point + path, json=json)
        # logger.info(f"{path}-{resp.status_code}")
        # if resp.status_code == 200:
        #     data = resp.json()
        #     return data
        return None

    def set_data(self, path, data=None):
        data = json.dumps({'img': self.photo,
                           'video': self.video})
        result = self._request(method="GET", path=path, data=data)
        print(result)
