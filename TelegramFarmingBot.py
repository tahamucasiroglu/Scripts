# pip install  keyboard mouse

import keyboard
import mouse
import time
import base64
import threading

parse = 10
sleepTime = 0.03

waitTimeIsActive = False
waitStepTime = 60
waitTime = 600

def WelcomeText():    
    # not to be searched
    text = "V2VsY29tZSBZZXNDb2luIFRlbGVncmFtIEJvdApGb3IgaW52aXRlIHdpdGggbXkgcmVmZmVyYWw6IGh0dHBzOi8vdC5tZS90aGVZZXNjb2luX2JvdC9ZZXNjb2luP3N0YXJ0YXBwPVhEVURDQg=="
    print(f"\n\n{base64.b64decode(text).decode()}\n\n")

def GetCoordinates() -> tuple[tuple[int,int],tuple[int,int]]:
    print("click left top corner")

    mouse.wait()

    mouse.get_position
    left_top = mouse.get_position()

    time.sleep(0.5)

    print(f"left top corner coordinat: {left_top}")

    print("click right bottom corner")

    mouse.wait()

    right_bottom = mouse.get_position()

    print(f"right bottom corner coordinat: {right_bottom}")

    time.sleep(0.5)

    return (left_top, right_bottom)

def GetStatus() -> bool:
    if(keyboard.is_pressed('p') or keyboard.is_pressed('e')):
        return True
    return False

def MakeList(left_top:tuple[int,int],right_bottom:tuple[int,int], parseSize:int = 10):
    YList = [i for i in range(left_top[1], right_bottom[1], (right_bottom[1] - left_top[1]) // parseSize)]
    YListReverse = YList.copy()
    YListReverse.reverse()

    XList = [i for i in range(left_top[0], right_bottom[0], (right_bottom[0] - left_top[0]) // parseSize)]
    XListReverse = XList.copy()
    XListReverse.reverse()

    return XList, XListReverse, YList, YListReverse

def HorizontalClicker(Y:int, X:list[int], sleepTimeSize:float = 0.01):
    global waitTimeIsActive
    if waitTimeIsActive:
        time.sleep(waitTime)
    for X in X:
        mouse.move(X, Y)
        time.sleep(sleepTimeSize)

def VerticalClicker(YList:list[int], XList:list[int], XListReverse:list[int], sleepTimeSize:float = 0.01):
    for i,Y in enumerate(YList):
        HorizontalClicker(Y, XList, sleepTimeSize) if i % 2 == 0 else HorizontalClicker(Y, XListReverse, sleepTimeSize)
        if GetStatus():
            break

def MoveMouse(left_top:tuple[int,int],right_bottom:tuple[int,int], parseSize:int = 10, sleepTimeSize:float = 0.01 ):

    XList, XListReverse, YList, YListReverse = MakeList(left_top, right_bottom, parseSize)

    while True:
        VerticalClicker(YList, XList, XListReverse, sleepTimeSize)
        VerticalClicker(YListReverse, XList, XListReverse, sleepTimeSize)
        if GetStatus():
            break

def WaitTimeHandler():
    global waitTimeIsActive
    while True:
        for i in range(waitStepTime, 0, -1):
            print(f"time left to stop {i} seconds")
            time.sleep(1)
        waitTimeIsActive = True
        print("stopping")
        for i in range(waitTime, 0, -1):
            print(f"time left to start {i} seconds")
            time.sleep(1)
        print("starting")
        waitTimeIsActive = False

if __name__ == "__main__":
    WelcomeText()
    print("\n'S' => Start\n'P' => Pause\n'E' => Exit")
    lt, rb = GetCoordinates()
    WaitTimeThread = threading.Thread(target= WaitTimeHandler, daemon=True)
    WaitTimeThread.start()
    while True:
        time.sleep(0.1)
        if keyboard.is_pressed('s'):
            MoveMouse(lt, rb, parse, sleepTime)
        if keyboard.is_pressed('e'):
            break














