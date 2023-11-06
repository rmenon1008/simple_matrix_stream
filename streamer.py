import multiprocessing as mp
import yt_dlp
import cv2
import time

import image_processing as ip

class Streamer:
    def __init__(self, url, desired_width=240, size=(96, 48), adjustments=None, crop=None):
        self.url = url
        self.desired_width = desired_width
        self.size = size
        self.adjustments = adjustments
        self.crop = crop
        self.last_frame_time = None
        self.fps = None
        self.stream_url = None
        self._set_up()

        m = mp.Manager()
        self.frame_buffer = m.Queue(maxsize=20*self.fps)
        self.frame_grabber = mp.Process(target=self._grab_frames)

    def __del__(self):
        self.frame_grabber.terminate()
        self.frame_grabber.join()

    def _set_up(self):
        if ".m3u8" in self.url:
            self.stream_url = self.url
            self.fps = 30
        else:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(self.url, download=False, process=False)
                formats = info['formats']

                for format in formats:
                    if 'height' in format:
                        if format['height'] == self.desired_width:
                            break
                    else:
                        continue
                else:
                    raise ValueError("No format with desired width found")

                self.stream_url = format['url']
                self.fps = format['fps']

    def start(self):
        self.frame_grabber.start()
        
    def _grab_frames(self):
            cap = cv2.VideoCapture(self.stream_url)
            print("Starting stream with fps: {}".format(self.fps))
        
            while True:
                ret, frame = cap.read()
                if ret:
                    if self.crop is not None:
                        frame = ip.crop_percentages(frame, self.crop)
                    if self.adjustments is not None:
                        frame = ip.image_adjustment(frame, **self.adjustments)
                    frame = ip.center_crop(frame, self.size[0] / self.size[1])
                    frame = cv2.resize(frame, self.size)

                    if self.frame_buffer.full():
                        self.frame_buffer.get()
                    self.frame_buffer.put(frame)
                else:
                    break

    def get_frame(self):
        if self.last_frame_time is not None:
            # Throw away frames if we are falling behind
            frames_to_skip = int((time.time() - self.last_frame_time) * self.fps)
            for _ in range(frames_to_skip):
                self.frame_buffer.get()

            # Wait if we are ahead of schedule
            time_to_wait = 1 / self.fps - (time.time() - self.last_frame_time)
            if time_to_wait > 0:
                time.sleep(time_to_wait)

        self.last_frame_time = time.time()
        return self.frame_buffer.get()
        