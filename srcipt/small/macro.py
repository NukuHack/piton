# pip install pynput mouse
from pynput import keyboard
import threading
import time


class AutoMacro:
    def __init__(self):
        self.keyboard = keyboard.Controller()
        self.running = False
        self.thread = None

    def press_key(self, key):
        self.keyboard.press(key)
        self.keyboard.release(key)

    def craft_loop(self):
        print("Auto-crafting started! (Press HOME to stop)")
        while self.running:
            self.press_key("r")
            time.sleep(0.05)

    def on_press(self, key):
        if key == keyboard.Key.home:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self.craft_loop)
                self.thread.start()
            else:
                self.running = False
                self.thread.join()
                self.thread = None
                print("Auto-crafting stopped. (Press HOME to start again)")

    def start(self):
        print("Auto-craft macro ready! Press HOME to start/stop")
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

if __name__ == "__main__":
    AutoMacro().start()