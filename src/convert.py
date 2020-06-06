import base64
import os
import subprocess


class Converter:
    """
    Usage:


        When creating this class you need to pass base64 encoded video, and base64 encoded audio file. The rest is optional.
        After creating an instance of this class, simply call the "convert" function with no arguments.
        The result will be in the root directory. It will also create a tmp directory but it will be empty at the end of the conversion.


    """

    def __init__(
        self,
        encoded_video,
        encoded_gif,
        video_name="video.mp4",
        gif_name="gif_file.gif",
        result="final.mp4",
    ):

        self.encoded_video = encoded_video
        self.encoded_gif = encoded_gif
        self.video_name = video_name

        self.video_path = os.path.join("tmp", video_name)
        self.gif_path = os.path.join("tmp", gif_name)

        self.audio_path = self.video_path.split(".")[0] + ".wav"
        self.video_from_gif_path = self.gif_path.split(".")[0] + ".mp4"

        self.result = result

    def save_encoded_data(self):

        if not os.path.exists("tmp"):
            os.mkdir("tmp")

        decoded_video = base64.b64decode(self.encoded_video)
        decoded_gif = base64.b64decode(self.encoded_gif)

        with open(self.video_path, "wb") as video_file, open(
            self.gif_path, "wb"
        ) as gif_file:

            video_file.write(decoded_video)
            gif_file.write(decoded_gif)

    def get_audio(self):

        command = f"ffmpeg -i {self.video_path} -ab 160k -ac 2 -ar 44100 -vn  {self.audio_path}"
        subprocess.call(command, shell=True)

    def convert_gif(self):

        command = f'ffmpeg -i {self.gif_path} -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" {self.video_from_gif_path}'
        subprocess.call(command, shell=True)

    def add_audio(self):

        command = f"ffmpeg -i {self.video_from_gif_path} -i {self.audio_path} -shortest {self.result}"
        subprocess.call(command, shell=True)

    def convert(self):

        self.save_encoded_data()
        self.get_audio()
        self.convert_gif()
        self.add_audio()

        for filename in os.listdir("tmp"):
            os.remove(os.path.join("tmp", filename))

