# pip install pynput mouse
from pynput import keyboard
import mouse
import threading
import time


# this is s simple script i made for minecraft craftmine update :)
# it works and is nice so yeah :)



class AutoPlant:
    def __init__(self):
        self.running = False
        self.thread = None

    def click_loop(self):
        while self.running:
            mouse.click('left')
            time.sleep(0.04)
            mouse.click('right')
            time.sleep(0.04)

    def on_press(self, key):
        if key == keyboard.Key.home:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self.click_loop)
                self.thread.start()
            else:
                self.running = False
                self.thread.join()
                self.thread = None

    def start(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

if __name__ == "__main__":
    AutoPlant().start()