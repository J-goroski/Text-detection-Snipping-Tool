import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from gui import MainWindow, SnippingWidget  # Import SnippingWidget from gui.py
from detection import OCRWorker
import easyocr
import warnings
import contextlib
import os

# Suppress CPU warning from easyocr and FutureWarnings from torch
warnings.filterwarnings("ignore", category=FutureWarning)

@contextlib.contextmanager
def suppress_stdout():
    """Temporarily suppress stdout (e.g., for muting easyocr CPU warning)"""
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


class Application(MainWindow):
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)
        super().__init__(self.reader)
        self.ocr_threads = []  # To store active threads


    def new_snip(self):
        """ Minimize the window and trigger the snipping after a short delay. """
        self.hide()  # Hide the main window
        # Delay starting the snipping tool to ensure the window has hidden
        QtCore.QTimer.singleShot(300, self.start_snip)  # 300ms delay before showing the snipping tool


    def start_snip(self):
        self.snipping_widget = SnippingWidget()  # This now references the imported SnippingWidget
        self.snipping_widget.snip_saved.connect(self.on_snip_saved)
        self.snipping_widget.show()

    def on_snip_saved(self, snip):
        self.show()  # Bring back the main window after snip
        self.snip = snip
        self.image_label.setPixmap(snip.scaled(
            self.image_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        # Convert QPixmap to numpy array
        qimage = snip.toImage()
        qimage = qimage.convertToFormat(QtGui.QImage.Format_RGBA8888)
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(qimage.byteCount())
        img = np.array(ptr).reshape(height, width, 4)

        # Start OCR processing for all three methods
        self.text_edit1.setPlainText('Processing...')
        self.text_edit2.setPlainText('Processing...')
        self.text_edit3.setPlainText('Processing...')

        # Method 1
        ocr_worker1 = OCRWorker(img.copy(), 1, self.reader)
        ocr_worker1.ocr_completed.connect(lambda text, method: self.display_extracted_text(text, method))
        ocr_worker1.start()
        self.ocr_threads.append(ocr_worker1)

        # Method 2
        ocr_worker2 = OCRWorker(img.copy(), 2, self.reader)
        ocr_worker2.ocr_completed.connect(lambda text, method: self.display_extracted_text(text, method))
        ocr_worker2.start()
        self.ocr_threads.append(ocr_worker2)

        # Method 3
        ocr_worker3 = OCRWorker(img.copy(), 3, self.reader)
        ocr_worker3.ocr_completed.connect(lambda text, method: self.display_extracted_text(text, method))
        ocr_worker3.start()
        self.ocr_threads.append(ocr_worker3)

    def closeEvent(self, event):
        # Ensure all threads are properly finished before closing
        for thread in self.ocr_threads:
            thread.quit()
            thread.wait()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec_())
