# pip install Pillow mss pynput matplotlib

from PIL import Image, ImageDraw
import mss
import numpy as np
import time
from pynput import keyboard
import threading
import sys
import matplotlib.pyplot as plt
import queue
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

TIME_INTERVAL = 0.1
MAX_TIME_WINDOW = 3
THRESHOLD = 10000

class ScreenMonitor:
    def __init__(self):
        self.running = False
        self.frames = []  # Stores tuples of (time, numpy array)
        self.image_queue = queue.Queue()
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.title("Screen Change Detector")
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.im = None

    def capture(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while self.running:
                now = time.time()
                sct_img = sct.grab(monitor)
                arr = np.array(Image.frombytes('RGB', (monitor['width'], monitor['height']),
                                              sct_img.bgra, 'raw', 'BGRX')).astype(np.int32)
                img = Image.fromarray(arr.astype('uint8'), 'RGB')

                if self.frames:
                    prev_time, prev_arr = self.frames[-1]
                    diff = np.abs(arr - prev_arr).sum()
                    if diff > THRESHOLD:
                        mask = np.abs(arr - prev_arr).any(axis=2)
                        coords = np.where(mask)
                        if coords[0].size > 0:
                            tl = (coords[1].min(), coords[0].min())
                            br = (coords[1].max(), coords[0].max())
                            draw = ImageDraw.Draw(img)
                            draw.rectangle([tl, br], outline='red', width=2)
                            print(f"Change detected! Difference: {diff}")

                self.frames.append((now, arr))
                while self.frames and self.frames[0][0] < now - MAX_TIME_WINDOW:
                    self.frames.pop(0)

                self.image_queue.put(img)
                time.sleep(TIME_INTERVAL)

    def update(self):
        try:
            while True:
                img = self.image_queue.get_nowait()
                arr = np.array(img)
                if self.im is None:
                    self.im = self.ax.imshow(arr)
                else:
                    self.im.set_data(arr)
                self.canvas.draw()
        except queue.Empty:
            pass
        finally:
            self.root.after(50, self.update)

    def toggle(self, key):
        if key == keyboard.Key.home:
            if not self.running:
                self.start()
            else:
                self.stop()

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.capture, daemon=True).start()
            self.update()  # Initialize plot updates

    def stop(self):
        self.running = False
        self.frames.clear()

    def exit(self):
        self.stop()
        self.root.destroy()
        sys.exit()

    def run(self):
        keyboard.Listener(on_press=self.toggle, daemon=True).start()
        self.root.mainloop()

if __name__ == "__main__":
    ScreenMonitor().run()