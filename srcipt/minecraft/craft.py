# pip install pynput mouse
from pynput import keyboard;
import mouse;
import threading;
import time;
import sys;

# this is an actual application of mouse and keyboard to craft a single item repeatedly (forever) until the user presses ESC
# actually had to make something like this for myself so i tought why not give it a try it python ?
# learn and make something useful ? really nice

class AutoCraft:
    def __init__(self):
        self.k,self.m=keyboard.Controller(),mouse
        self.r=self.s=self.e=False

    def press_key(self, c):
        self.k.press(c); self.k.release(c)

    def loop_craft(self):
        while not self.s:
            self.press_key(" ")
            with self.k.pressed(keyboard.Key.shift_l):
                self.m.click('left')
            time.sleep(.1)
        self.r = False

    def on_press(self, k):
        if k==keyboard.Key.home and not self.r:
            self.s=False;time.sleep(.4);self.r=True
            threading.Thread(target=self.loop_craft).start()

    def on_release(self, k):
        if self.r and k==keyboard.Key.home:
            self.s=self.e=True
            return False
        return True

    def start(self):
        with keyboard.Listener(on_press=self.on_press,on_release=self.on_release) as l:l.join()
        if self.e:print("Exiting in a second...");time.sleep(1);sys.exit()

if __name__ == "__main__":AutoCraft().start()






# Keyboard 


# keyboard.type("Here is a long text!")  ->  types the entire long stuff
# .touch(key, is_press)  ->  Calls either press() or release() depending on the value of is_press.

# .pressed(key)  ->  Executes a block with some keys pressed.

# here are the "non char" keycodes use them like "Key.<code>"


# alt = <Key.f1: 0>
# A generic Alt key. This is a modifier.

# alt_gr = <Key.f1: 0>
# The AltGr key. This is a modifier.

# alt_l = <Key.f1: 0>
# The left Alt key. This is a modifier.

# alt_r = <Key.f1: 0>
# The right Alt key. This is a modifier.

# backspace = <Key.f1: 0>
# The Backspace key.

# caps_lock = <Key.f1: 0>
# The CapsLock key.

# cmd = <Key.f1: 0>
# A generic command button. On PC platforms, this corresponds to the Super key or Windows key, and on Mac it corresponds to the Command key. This may be a modifier.

# cmd_l = <Key.f1: 0>
# The left command button. On PC platforms, this corresponds to the Super key or Windows key, and on Mac it corresponds to the Command key. This may be a modifier.

# cmd_r = <Key.f1: 0>
# The right command button. On PC platforms, this corresponds to the Super key or Windows key, and on Mac it corresponds to the Command key. This may be a modifier.

# ctrl = <Key.f1: 0>
# A generic Ctrl key. This is a modifier.

# ctrl_l = <Key.f1: 0>
# The left Ctrl key. This is a modifier.

# ctrl_r = <Key.f1: 0>
# The right Ctrl key. This is a modifier.

# delete = <Key.f1: 0>
# The Delete key.

# down = <Key.f1: 0>
# A down arrow key.

# end = <Key.f1: 0>
# The End key.

# enter = <Key.f1: 0>
# The Enter or Return key.

# esc = <Key.f1: 0>
# The Esc key.

# f1 = <Key.f1: 0>
# The function keys. F1 to F20 are defined.

# home = <Key.f1: 0>
# The Home key.

# insert = <Key.f1: 0>
# The Insert key. This may be undefined for some platforms.

# left = <Key.f1: 0>
# A left arrow key.

# menu = <Key.f1: 0>
# The Menu key. This may be undefined for some platforms.

# num_lock = <Key.f1: 0>
# The NumLock key. This may be undefined for some platforms.

# page_down = <Key.f1: 0>
# The PageDown key.

# page_up = <Key.f1: 0>
# The PageUp key.

# pause = <Key.f1: 0>
# The Pause/Break key. This may be undefined for some platforms.

# print_screen = <Key.f1: 0>
# The PrintScreen key. This may be undefined for some platforms.

# right = <Key.f1: 0>
# A right arrow key.

# scroll_lock = <Key.f1: 0>
# The ScrollLock key. This may be undefined for some platforms.

# shift = <Key.f1: 0>
# A generic Shift key. This is a modifier.

# shift_l = <Key.f1: 0>
# The left Shift key. This is a modifier.

# shift_r = <Key.f1: 0>
# The right Shift key. This is a modifier.

# space = <Key.f1: 0>
# The Space key.

# tab = <Key.f1: 0>
# The Tab key.

# up = <Key.f1: 0>
# An up arrow key.





# Mouse 


# mouse.move(100, 100, absolute=False, duration=0.2)
# This will move the mouse relatively for 0.2 seconds. Let's break down what each parameter in this function call means:
# 
# (100, 100): These are the x and y coordinates to which you want to move the mouse cursor. In this case, both are set to 100.
# absolute=False: This parameter determines the nature of the movement:
# When absolute is set to False, the movement is relative. This means the cursor will move 100 pixels to the right (x-coordinate) and 100 pixels down (y-coordinate) from its current position.
# If absolute were set to True, the cursor would move to the absolute position (100, 100) on the screen, where (0, 0) is typically the top-left corner of the screen.
# duration=0.2: This parameter specifies the duration of the movement in seconds. It's set to 0.2, meaning the cursor will take 0.2 seconds to complete the movement. This creates a smooth, animated cursor movement rather than an instantaneous jump. If the duration were set to 0, the movement would be immediate.
#
# there is also a drag function (move just with pressed)
# mouse.drag(0, 0, 100, 100, absolute=False, duration=0.1) 
# same stuff 

# In : mouse.get_position()
# Out: (646, 407)

# mouse.click('left') or 'right' or 'middle'

# check pressing : mouse.is_pressed("right")

# make a listener when left button is clicked
# mouse.on_click(lambda: print("Left Button clicked."))
# make a listener when right button is clicked
# mouse.on_right_click(lambda: print("Right Button clicked."))

# scroll down
# mouse.wheel(-1)
# scroll up
# mouse.wheel(1)