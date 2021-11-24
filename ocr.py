from typing import List
import pyautogui
import pygetwindow
from PIL import Image
from pytesseract import image_to_string, pytesseract
import numpy as np
from decimal import Decimal
import re


LOOT_RE = "([a-zA-Z\(\) ]+) [\(\{\[](\d+[\.\,]\d+) PED[\)\]\}]"


pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def screenshot_window():
    window_name = None

    for window_name in pygetwindow.getAllTitles():
        if window_name.startswith("Entropia Universe Client"):
            found_window = window_name
            break

    if not window_name:
        return None, 0, 0

    window = pygetwindow.getWindowsWithTitle(window_name)[0]
    window.activate()

    im = pyautogui.screenshot()

    top_left = window.topleft
    width = window.width
    height = window.height

    im1 = im.crop((top_left.x, top_left.y, top_left.x + width, top_left.y + height))
    return im1, width, height


def change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))

    def contrast(c):
        return 128 + factor * (c - 128)

    return img.point(contrast)


def get_loot_instances_from_screen():
    loots = []

    img = screenshot_window()

    img = img.convert('LA')
    data = np.array(img)
    img = change_contrast(img, 150)

    # Greyscale and try and isolate text
    converted = np.where((data // 39) == 215 // 39, 0, 255)

    img = Image.fromarray(converted.astype('uint8'))

    text = image_to_string(img)
    lines = text.split("\n")
    for s in lines:
        match = re.match(LOOT_RE, s)
        print(s)
        if match:
            name, value = match.groups()
            value = Decimal(value.replace(",", "."))
    return loots


def capture_target(contrast=0, banding=35, filter=225):
    im = pyautogui.screenshot()

    width, height = im.size

    sides = width / 3
    bottom = height / 3

    print((0, 0, sides, bottom))
    im1 = im.crop((sides, 0, width - sides, bottom))

    im1 = im1.convert('LA')
    data = np.array(im1)
    im1 = change_contrast(im1, contrast)

    # Greyscale and try and isolate text
    converted = np.where((data // banding) == filter // banding, 0, 255)

    img = Image.fromarray(converted.astype('uint8'))
    text = image_to_string(img)
    lines = text.split("\n")
    for s in lines:
        if s:
            print(s)
