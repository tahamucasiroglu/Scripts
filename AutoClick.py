import pyautogui
import keyboard
import time

def click_mouse():
    pyautogui.click(button='left')

def main():
    while True:
        time.sleep(0.1)
        if keyboard.is_pressed('shift'):
            while True:
                click_mouse()
                time.sleep(0.05)  # İstediğiniz hızda tıklamalar için bu değeri ayarlayabilirsiniz
                if keyboard.is_pressed('alt'):
                    break

if __name__ == "__main__":
    main()
 