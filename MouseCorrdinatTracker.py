import mouse, keyboard, time



def MouseTracker():
    while True:
        if keyboard.is_pressed('e'):
            break
        print(mouse.get_position())
        time.sleep(0.1)




if __name__ == "__main__":
    MouseTracker()