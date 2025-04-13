# pip install pynput
from pynput import keyboard
# pip install mouse
import mouse;
import threading;
import time;


# this is s simple script i made for minecraft craftmine update :)
# it works and is nice so yeah :)



class AutoPlant:
    def __init__(self):
        self.keyboard = keyboard.Controller()
        self.running = False  # Tracks if the loop is running
        self.exit_flag = False  # Tracks if the loop should exit
        self.thread = None  # Reference to the thread running the loop

    def loop(self):
        while not self.exit_flag:
            mouse.click('left')
            time.sleep(0.04)
            mouse.click('right')
            time.sleep(0.04)

    def on_press(self, key):
        if key == keyboard.Key.home and not self.running:
            # Start the loop in a new thread
            self.thread = threading.Thread(target=self.loop)
            self.thread.start()
            time.sleep(0.4)  # Needed to avoid immediate exit
            self.running = True

    def on_release(self, key):
        if key == keyboard.Key.home and self.running:
            # Set the exit flag and wait for the thread to finish
            self.exit_flag = True
            print("Exiting in a second...")
            time.sleep(1)

            # Stop the thread gracefully
            self.thread.join()
            self.running = False
            self.exit_flag = False
            print("Loop stopped. Ready to restart.")

    def start(self):
        keyboard.Listener(on_press=self.on_press, on_release=self.on_release).run()

if __name__ == "__main__":
    AutoPlant().start()
