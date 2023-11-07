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

        self.frame_grabber.start()

    def _set_up(self):
        while True:
            try:
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
                        break
            except:
                print("Could not connect to stream. Retrying...")
            time.sleep(5)
        
    def _grab_frames(self):
        try:
            cap = cv2.VideoCapture(self.stream_url)
        except:
            print("Asking for restart (no cap available)")
            self.frame_buffer.put(None)
        print("Starting stream with fps: {}".format(self.fps))

        while True:
            try:
                ret, frame = cap.read()
                if ret:
                    if self.crop is not None:
                        frame = ip.crop_percentages(frame, self.crop)
                    if self.adjustments is not None:
                        frame = ip.image_adjustment(frame, **self.adjustments)
                    frame = ip.center_crop(frame, self.size[0] / self.size[1])
                    frame = cv2.resize(frame, self.size, interpolation=cv2.INTER_AREA)

                    # Skip ahead if there are a ton of frames in the buffer
                    if self.frame_buffer.full():
                        while self.frame_buffer.qsize() > 10*self.fps:
                            self.frame_buffer.get()

                    self.frame_buffer.put(frame)
                else:
                    print("Ret was false")
                    break
            except:
                print("Error reading frame")
                break
        
        print("Asking for restart (error reading frame)")
        self.frame_buffer.put(None)

    def _try_restart(self):
        print("Found None frame, restarting...")
        self.frame_grabber.terminate()
        self.frame_grabber.join()
        self._set_up()
        self.frame_grabber = mp.Process(target=self._grab_frames)
        self.frame_grabber.start()
        frame = self.frame_buffer.get()
        return frame

    def get_frame(self):
        print(self.frame_buffer.qsize())
        if self.last_frame_time is not None:
            # Throw away frames if we are falling behind
            frames_to_skip = int((time.time() - self.last_frame_time) * self.fps)
            for _ in range(frames_to_skip):
                frame = self.frame_buffer.get()
                if frame is None:
                    frame = self._try_restart()

            # Wait if we are ahead of schedule
            time_to_wait = 1 / self.fps - (time.time() - self.last_frame_time)
            if time_to_wait > 0:
                time.sleep(time_to_wait)

            if self.frame_buffer.empty():
                time.sleep(5)

        self.last_frame_time = time.time()
        frame = self.frame_buffer.get()
        if frame is None:
            frame = self._try_restart()
        return frame
        