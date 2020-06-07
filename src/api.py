import requests
import logging
import json
import base64
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Api:
    def __init__(self):
        self.end_point = "http://0.0.0.0:9999"

        # Pretty dumb, but easy
        if not os.path.exists('database'):
            os.makedirs('database')

    def set_photo(self, photo, chat_id):
        photo = str(base64.b64encode(photo).decode('utf-8'))
        with open(f"database/{chat_id}_input.jpg", "w") as fh:
            fh.write(photo)

    def set_video(self, video, chat_id):
        video = str(base64.b64encode(video).decode('utf-8'))
        with open(f"database/{chat_id}_input_video.mp4", "w") as fh:
            fh.write(video)

    def _request(self, path, data=None):
        logger.info(f"POST {self.end_point + path}")
        resp = requests.post(self.end_point + path, data=data)
        logger.info(f"{path}-{resp.status_code}")
        
        return resp.json()

    def to_telegram_gif(self, result):
        gif = result['video']

    def set_data(self, path, chat_id):
        with open(f"database/{chat_id}_input.jpg") as file:
            img = file.read()
        with open(f"database/{chat_id}_input_video.mp4") as file:
            video = file.read()
        data = json.dumps({'img':   img,
                           'video': video})
        result = self._request(path=path, data=data)
        return result
