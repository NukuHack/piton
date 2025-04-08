import os
import sys
import ctypes
from pynput import keyboard
from screeninfo import get_monitors
import mouse
import threading
import time
from pywinauto import Application, Desktop

class AutomationBot:
    def __init__(self):
        self.keyboard = keyboard.Controller()
        self.exit_flag = False

    def press_key(self, key_char):
        """Simulate pressing a key"""
        self.keyboard.press(key_char)
        self.keyboard.release(key_char)

    def perform_actions(self):
        """Execute automated actions in a background thread"""
        try:
            # Get primary monitor dimensions
            primary_monitor = get_monitors()[0]
            center_x = primary_monitor.width // 2
            center_y = primary_monitor.height // 2

            # First action: click center and type "apple"
            mouse.move(center_x, center_y, absolute=True, duration=0.2)
            mouse.click('left')
            self.keyboard.type("apple")
            time.sleep(0.2)

            # Second action: move down and type "apple pie"
            mouse.move(center_x, center_y + 50, absolute=True, duration=0.2)
            mouse.click('left')
            self.keyboard.type("apple pie")
            time.sleep(0.1)

        except Exception as e:
            print(f"Action execution failed: {str(e)}")

    def on_key_press(self, key):
        """Handle key press events"""
        if key == keyboard.Key.home:
            threading.Thread(target=self.perform_actions).start()

    def on_key_release(self, key):
        """Handle key release events"""
        if key == keyboard.Key.esc:
            self.exit_flag = True
            return False  # Stop listener
        return True

    def start_listening(self):
        """Start the keyboard listener"""
        try:
            with keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            ) as listener:
                listener.join()
        except Exception as e:
            print(f"Listener error: {str(e)}")
            sys.exit(1)

        if self.exit_flag:
            print("Exiting program...")
            time.sleep(1)
            sys.exit(0)

def request_admin_rights():
    """Request administrative privileges"""
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True

    try:
        # Relaunch as administrator
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            f'"{os.path.abspath(sys.argv[0])}"',
            None,
            1
        )
        return False  # Exit the original process

    except Exception as e:
        print(f"Failed to get admin rights: {str(e)}")
        return False

def automate_admin_login():
    """Automate the "Run as Administrator" login process"""
    try:
        # Wait for the "Run as Administrator" prompt to appear
        time.sleep(5)  # Adjust delay as needed

        # Get the window title of the "Run as Administrator" prompt
        window_title = "Run as Administrator"

        # Attach to the window
        app = Application(backend="uia").connect(title=window_title)

        # Focus on the username field and send the email
        dlg = app.window(title=window_title)
        dlg.set_focus()  # Ensure the dialog is active
        username_field = dlg.child_window(title="Username", control_type="Edit")
        username_field.set_text("your_email@example.com")

        # Focus on the password field and send the password
        password_field = dlg.child_window(title="Password", control_type="Edit")
        password_field.set_text("your_password")

        # Click the "OK" button
        ok_button = dlg.child_window(title="OK", control_type="Button")
        ok_button.click()

        print("Successfully logged in as administrator.")
        return True

    except Exception as e:
        print(f"Failed to automate login: {str(e)}")
        return False

if __name__ == "__main__":
    # Request admin rights
    if not request_admin_rights():
        print("Please manually enter admin credentials.")
        if not automate_admin_login():
            print("Failed to log in as administrator. Exiting...")
            sys.exit(1)

    print("Automation Bot started. Press Home to trigger actions, ESC to exit.")
    
    bot = AutomationBot()
    bot.start_listening()