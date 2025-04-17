
#pip install pygetwindow pyautogui

import pygetwindow as gw
import pyautogui
import time

def get_topmost_window():
    """Get the topmost window."""
    windows = gw.getAllWindows()
    # Sort windows by their Z-order (topmost first)
    windows.sort(key=lambda win: win.zOrder, reverse=True)
    return windows[0] if windows else None

def focus_topmost_window():
    """Focus the topmost window if no window is focused."""
    # Wait for a short period to ensure we don't interfere with user input
    time.sleep(0.01)

    # Get the currently active window
    active_window = gw.getActiveWindow()

    # If no window is active, try to focus the topmost window
    if active_window is None:
        topmost_window = get_topmost_window()
        if topmost_window:
            print(f"Focusing on window: {topmost_window.title}")
            topmost_window.activate()  # Bring the window to the foreground
            pyautogui.click(topmost_window.left + 10, topmost_window.top + 10)  # Simulate a click inside the window
        else:
            print("No windows found.")

if __name__ == "__main__":
    print("Script started. Press Ctrl+C to stop.")
    while True:
        try:
            focus_topmost_window()
            time.sleep(0.3)  # Run every second
        except KeyboardInterrupt:
            print("\nScript stopped by user.")
            break


