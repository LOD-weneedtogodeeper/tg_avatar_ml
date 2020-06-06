import requests
import logging
import json
import base64

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Api:
    def __init__(self):
        self.end_point = "http://0.0.0.0:9999"
        self.photo = None
        self.video = None

    def set_photo(self, photo):
        self.photo = str(base64.b64encode(photo).decode('utf-8'))

    def set_video(self, video):
        self.video = str(base64.b64encode(video).decode('utf-8'))

    def _request(self, path, data=None):
        logger.info(f"POST {self.end_point + path}")
        resp = requests.post(self.end_point + path, data=data)
        logger.info(f"{path}-{resp.status_code}")
        
        return resp.json()

    def to_telegram_gif(self, result):
        gif = result['video']

    def set_data(self, path, data=None):
        data = json.dumps({'img': self.photo,
                           'video': self.video})
        result = self._request(path=path, data=data)
        return result
