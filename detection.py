import cv2
import easyocr
import numpy as np
from PyQt5 import QtCore


class OCRWorker(QtCore.QThread):
    ocr_completed = QtCore.pyqtSignal(str, int)

    def __init__(self, image, method, reader):
        super().__init__()
        self.image = image
        self.method = method
        self.reader = reader

    def run(self):
        if self.method == 1:
            # Method 1: Current text detection (no additional preprocessing)
            processed_img = self.image
        elif self.method == 2:
            # Method 2: Upscale image to improve detection of pixelated letters
            scale_percent = 200  # Increase size by 200%
            width = int(self.image.shape[1] * scale_percent / 100)
            height = int(self.image.shape[0] * scale_percent / 100)
            dim = (width, height)
            processed_img = cv2.resize(self.image, dim, interpolation=cv2.INTER_CUBIC)
        elif self.method == 3:
            # Method 3: Best approach with advanced preprocessing
            img_rgb = cv2.cvtColor(self.image, cv2.COLOR_RGBA2RGB)
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            adaptive_thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            processed_img = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
            processed_img = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2RGB)
        else:
            processed_img = self.image

        # Run OCR on the processed image
        result = self.reader.readtext(processed_img)
        extracted_text = '\n'.join([res[1] for res in result])
        self.ocr_completed.emit(extracted_text, self.method)
