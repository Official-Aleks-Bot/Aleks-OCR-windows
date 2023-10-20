import requests
import base64
import pytesseract
import re
import pyperclip
import tkinter as tk
from tkinter import PhotoImage
from tkinter import ttk
import pygetwindow as gw
import pygetwindow as gw
from PIL import Image, ImageGrab
import os

image_path = "screenshot.png"
window = tk.Tk()
window.resizable(False, False)
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if not os.path.exists(tesseract_path):
    tesseract_path = None
    print("Tesseract executable not found. Tesseract button is disabled.")
else:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Define the image_label before using it in run_ocr
image_label = tk.Label(window)
image_label.pack(pady=10) 

# Create a text widget instead of label
text_widget = tk.Text(window, wrap=tk.WORD, height=5, width=60)
text_widget.pack()

# Define two sets of data for the POST request
data_set1 = {
    "url": "https://www.mathway.com/OCR",
    "headers": {
        "Host": "www.mathway.com",
        "Cookie": "Mathway.LastSubject=Algebra; Mathway.IncomingCulture=en-US; Mathway.Culture=en-US; Mathway.Location=US;",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Ch-Ua-Mobile": "?0",
        "Referer": "https://www.mathway.com/Algebra",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=10.0",
    },
    "payload": {
        "imageData": "",
        "culture": "en-US"
    }
}

current_data_set = data_set1  # Start with the first set of data

def images():
    brave_window = gw.getWindowsWithTitle("chrome")[0]
    brave_window.activate()
    x, y, width, height = brave_window.left+10, brave_window.top + 180, brave_window.width-30, brave_window.height - 300
    screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    new_height = 400
    ratio = new_height / screenshot.height
    new_width = int(screenshot.width * ratio)
    resized_screenshot = screenshot.resize((new_width, new_height))
    resized_screenshot.save("screenshot1.png")
    screenshot = screenshot.convert('L')
    screenshot.save("screenshot.png")

    global image
    image = PhotoImage(file="screenshot1.png")
    image_label.config(image=image)

def run_ocr():
    images()

    base64_image = image_to_base64(image_path)

    current_data_set["payload"]["imageData"] = "data:image/png;base64," + base64_image

    response = requests.post(current_data_set["url"], headers=current_data_set["headers"], data=current_data_set["payload"])
    data = response.text

    input_string = data
    output_string = remove_text_before_and_after_pattern(input_string)
    output_string = output_string.replace(":", "")
    output_string = output_string.replace("}", "")
    output_string = output_string.replace("{", "")
    output_string = output_string.replace("]", "")
    output_string = output_string.replace("[", "")


    pyperclip.copy(output_string)
    text_widget.delete(1.0, tk.END)  # Clear previous text
    text_widget.insert(tk.END, output_string)

    pyperclip.copy(output_string)

def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            base64_data = base64.b64encode(image_file.read()).decode('utf-8')
            return base64_data
    except FileNotFoundError:
        return None

def remove_text_before_and_after_pattern(input_str):
    pattern = r'".*?AsciiMath":"(.*?)"'
    match = re.search(pattern, input_str)
    if match:
        result = match.group(1)
        return result
    return input_str

tesseract_available = tesseract_path is not None


def toggle_data_set():
    global current_data_set
    if current_data_set == data_set1:
        images()
        if tesseract_available:
            text = pytesseract.image_to_string(Image.open(image_path), lang='eng')
            text_widget.delete(1.0, tk.END)  # Clear previous text
            text_widget.insert(tk.END, text)
            pyperclip.copy(text)
        else:
            text_widget.delete(1.0, tk.END)  # Clear previous text
            text_widget.insert(tk.END, "Tesseract is not available. Please check the Tesseract path.")
    else:
        current_data_set = data_set1

def copy_text_to_clipboard():
    text_to_copy = text_widget.get(1.0, tk.END)  # Get the text from the text widget
    pyperclip.copy(text_to_copy.strip())

run_button = ttk.Button(window, text="Run Math OCR", command=run_ocr)
run_button.pack(side="left", padx=20, pady=20)

check_button = ttk.Button(window, text="Run Tesseract", command=toggle_data_set)
check_button.pack(side="left", padx=20, pady=20)

copy_text_button = ttk.Button(window, text="Copy", command=copy_text_to_clipboard)
copy_text_button.pack(side="left", padx=20, pady=20)

run_ocr()

window.mainloop()