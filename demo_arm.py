from time import sleep
from PIL.Image import new
from PIL.ImageDraw import Draw
from cv2 import CascadeClassifier, \
                VideoCapture, flip, \
                line, rectangle, \
                imshow, waitKey, \
                destroyAllWindows
from robotic_arm import Arm
from Adafruit_SSD1306 import SSD1306_128_64
from random import randint

PARMS = (
    {"Port": 0, "Adjust": 5, "Min": 130, "Max": 475, "Reverse": True},
    {"Left Port": 1, "Right Port": 2, "Left Adjust": 20, "Min": 130, "Max": 475, "Reverse": True},
    {"Port": 3, "Adjust": -5, "Min": 150, "Max": 500, "Reverse": True},
    {"Port": 4, "Adjust": -5, "Min": 125, "Max": 540, "Reverse": True},
    {"Port": 5, "Min": 280, "Max": 450}
)

DEG = 10
NMOVE = 15
RCHANCE = 20
WCHANCE = 30
NDISABLE = 50
EYEADJUST = 5
SENTENCES = [
"Hello",
"I am angry !",
"I hate smiles",
"I am always angry",
"I am never happy",
"I dislike the word \"happy\""
]
TSMILE = "Stop to smile !!!"

NDEG = DEG * -1
MOVE = 0
DISABLE = NDISABLE + 1
LEN = len(SENTENCES) - 1
KEY = -1
TEXT = ""

SMILE_CASCADE = CascadeClassifier("Cascades/smile.xml")
FACE_CASCADE = CascadeClassifier("Cascades/face.xml")
EYE_CASCADE = CascadeClassifier("Cascades/eye.xml")

DISP = SSD1306_128_64(None)
DISP.begin()
DISP.clear()
DISP.set_contrast(1)
DISP.display()

WIDTH = DISP.width
HEIGHT = DISP.height

TEXTX = WIDTH - 15

ARM = Arm(PARMS, (90, 90, 90, 0, 90))
ARM.activate(False)

CAM = VideoCapture(0)

while True:
    for i in range(0, 10):
        CAM.grab()
    RET, IMG = CAM.retrieve()
    if RET:
        IMG = flip(IMG, -1)
        FACES = FACE_CASCADE.detectMultiScale(IMG, 1.2, 10)
        if not isinstance(FACES, tuple):
            FACES = FACES.tolist()
            FACES.sort(key=lambda val: val[2] * val[3], reverse=True)
            X, Y, W, H = FACES[0]
            HW = int(round(W / 2))
            HH = int(round(H / 2))
            QW = int(round(HW / 2))
            QH = int(round(HH / 2))
            line(IMG, (X, Y), (X, Y - HH), (0, 255, 255), 2)
            line(IMG, (X, Y - HH), (X + QW, Y - QH), (0, 255, 255), 2)
            line(IMG, (X + QW, Y - QH), (X + HW, Y - HH), (0, 255, 255), 2)
            line(IMG, (X + HW, Y - HH), (X + 3 * QW, Y - QH), (0, 255, 255), 2)
            line(IMG, (X + 3 * QW, Y - QH), (X + W, Y - HH), (0, 255, 255), 2)
            line(IMG, (X + W, Y - HH), (X + W, Y), (0, 255, 255), 2)
            SMT = False
            for x, y, w, h in FACES:
                rectangle(IMG, (x, y), (x + w, y + h), (0, 0, 255), 2)
                face = IMG[y:y + h, x:x + w]
                eyes = EYE_CASCADE.detectMultiScale(face, 1.05, 5)
                for ex, ey, ew, eh in eyes:
                    rectangle(face, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 2)
                smiles = SMILE_CASCADE.detectMultiScale(face, 1.2, 15)
                for sx, sy, sw, sh in smiles:
                    SMT = True
                    rectangle(face, (sx, sy), (sx + sw, sy + sh), (0, 255, 0), 2)
            if SMT:
                if TEXT != TSMILE:
                    TEXT = TSMILE
                    TEXTX = WIDTH - 15
            XW = X + HW
            YH = Y + HH
            MX = int(round(IMG.shape[1] / 2))
            MY = int(round(IMG.shape[0] / 2))
            DX = (MX - XW) * 65 / MX
            DY = (MY - YH) * 65 / MX
            MOVE += 1
            DISABLE = 0
            if DX > DEG or NDEG > DX:
                ARM.base.set(ARM.base.get() - DX)
                MOVE = 0
                ETY = 0
            else:
                ETY = DY / EYEADJUST * -1
            if DY > DEG or NDEG > DY:
                POS = ARM.elbow.get() + ARM.wrist.get() + DY
                if POS < 90:
                    ARM.elbow.set(POS)
                    ARM.wrist.set(0)
                else:
                    ARM.elbow.set(90)
                    ARM.wrist.set(POS - 90)
                MOVE = 0
                ETX = 0
            else:
                ETX = DX / EYEADJUST
            if MOVE == 0:
                line(IMG, (XW, YH), (MX, MY), (255, 255, 255), 2)
                if randint(0, WCHANCE) == 0:
                    ARM.wrench.set(0)
                    ARM.wrench.set(90)
            if TEXT == "" and randint(0, RCHANCE) == 0:
                TEXT = SENTENCES[randint(0, LEN)]
        else:
            if KEY == 81:
                MOVE = 0
                DISABLE = 0
                ARM.base.set(ARM.base.get() - 10)
            elif KEY == 82:
                MOVE = 0
                DISABLE = 0
                POS = ARM.elbow.get() + ARM.wrist.get() + 10
                if POS < 90:
                    ARM.elbow.set(POS)
                    ARM.wrist.set(0)
                else:
                    ARM.elbow.set(90)
                    ARM.wrist.set(POS - 90)
            elif KEY == 83:
                MOVE = 0
                DISABLE = 0
                ARM.base.set(ARM.base.get() + 10)
            elif KEY == 84:
                MOVE = 0
                DISABLE = 0
                POS = ARM.elbow.get() + ARM.wrist.get() - 10
                if POS < 90:
                    ARM.elbow.set(POS)
                    ARM.wrist.set(0)
                else:
                    ARM.elbow.set(90)
                    ARM.wrist.set(POS - 90)
            elif KEY == 32:
                DISABLE = 0
                MOVE = NMOVE
            elif KEY == 13:
                ARM.wrench.set(0)
                ARM.wrench.set(90)
            else:
                DISABLE += 1
            ETX = 0
            ETY = 0
        imshow("Camera", IMG)
    else:
        DISABLE = NDISABLE
    if DISABLE > NDISABLE:
        MOVE = 0
        sleep(0.5)
    elif DISABLE < NDISABLE:
        SCREEN = new("1", (WIDTH, HEIGHT))
        DRAW = Draw(SCREEN)
        DRAW.rectangle(((15, 0), (50, 40)), 0, 1, 2)
        DRAW.rectangle(((WIDTH - 50, 0), (WIDTH - 15, 40)), 0, 1, 2)
        ETY += 18
        DRAW.rectangle(((ETX + 31, ETY), (ETX + 34, ETY + 3)), 1)
        DRAW.rectangle(((ETX + WIDTH - 31, ETY), (ETX + WIDTH - 34, ETY + 3)), 1)
        if MOVE > NMOVE:
            DRAW.polygon(((15, 0), (50, 0), (50, 15), (15, 15)), 1)
            DRAW.polygon(((WIDTH - 50, 0), (WIDTH - 15, 0), (WIDTH - 15, 15), (WIDTH - 50, 15)), 1)
        elif MOVE < NMOVE:
            DRAW.polygon(((15, 0), (50, 0), (50, 20), (15, 5)), 1)
            DRAW.polygon(((WIDTH - 50, 0), (WIDTH - 15, 0), (WIDTH - 15, 5), (WIDTH - 50, 20)), 1)
        else:
            ARM.activate(False)
            MOVE += 1
            DRAW.polygon(((15, 0), (50, 0), (50, 18), (15, 10)), 1)
            DRAW.polygon(((WIDTH - 50, 0), (WIDTH - 15, 0), (WIDTH - 15, 10), (WIDTH - 50, 18)), 1)
        DRAW.rectangle(((15, HEIGHT - 15), (WIDTH - 15, HEIGHT - 1)), 0, 1, 2)
        if TEXT != "":
            if len(TEXT) * 6 + TEXTX - 15 <= 0:
                TEXT = ""
                TEXTX = WIDTH - 15
            else:
                DRAW.text((TEXTX, HEIGHT - 14), TEXT, 1)
                DRAW.rectangle(((0, HEIGHT - 15), (14, HEIGHT - 1)), 0)
                DRAW.rectangle(((WIDTH, HEIGHT - 15), (WIDTH - 14, HEIGHT - 1)), 0)
                TEXTX -= 10
        DISP.image(SCREEN)
        DISP.display()
        sleep(0.1)
    else:
        ARM.set((90, 90, 90, 0, 90))
        ARM.activate(False)
        DISP.clear()
        DISP.display()
        DISABLE += 1
    KEY = waitKey(10)
    if KEY == 27:
        break

destroyAllWindows()

CAM.release()

ARM.set((90, 90, 90, 0, 90))
ARM.activate(False)

DISP.clear()
DISP.display()
