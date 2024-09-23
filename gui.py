from PyQt5 import QtWidgets, QtGui, QtCore


class SnippingWidget(QtWidgets.QWidget):
    snip_saved = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setWindowState(self.windowState() | QtCore.Qt.WindowFullScreen)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.screen_pixmap = QtGui.QGuiApplication.primaryScreen().grabWindow(0)

    def paintEvent(self, event):
        brush_color = (0, 0, 0, 100)
        lw = 2
        opacity = 0.3

        painter = QtGui.QPainter(self)
        painter.setOpacity(opacity)
        painter.drawPixmap(0, 0, self.screen_pixmap)

        painter.setOpacity(1)
        pen = QtGui.QPen(QtGui.QColor('red'), lw)
        painter.setPen(pen)
        painter.setBrush(QtGui.QColor(*brush_color))
        rect = QtCore.QRect(self.begin, self.end)
        painter.drawRect(rect.normalized())

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        rect = QtCore.QRect(self.begin, self.end).normalized()
        snip = self.screen_pixmap.copy(rect)
        self.snip_saved.emit(snip)
        self.close()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, ocr_reader):
        super().__init__()
        self.snip = None
        self.reader = ocr_reader
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Snipping Tool with Multiple OCR Methods')
        self.setGeometry(100, 100, 1200, 600)

        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        hbox = QtWidgets.QHBoxLayout()

        # Image label
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setMinimumWidth(400)
        hbox.addWidget(self.image_label, 1)

        # Vertical layout for text boxes
        vbox = QtWidgets.QVBoxLayout()

        # Text edit for OCR Method 1
        self.text_edit1 = QtWidgets.QTextEdit()
        self.text_edit1.setReadOnly(True)
        self.text_edit1.setPlaceholderText('Method 1: Current Text Detection')
        vbox.addWidget(self.text_edit1)

        # Text edit for OCR Method 2
        self.text_edit2 = QtWidgets.QTextEdit()
        self.text_edit2.setReadOnly(True)
        self.text_edit2.setPlaceholderText('Method 2: Upscaled Image')
        vbox.addWidget(self.text_edit2)

        # Text edit for OCR Method 3
        self.text_edit3 = QtWidgets.QTextEdit()
        self.text_edit3.setReadOnly(True)
        self.text_edit3.setPlaceholderText('Method 3: Enhanced Detection')
        vbox.addWidget(self.text_edit3)

        hbox.addLayout(vbox, 1)

        central_widget.setLayout(hbox)

        # Menu bar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')
        save_action = QtWidgets.QAction('Save', self)
        save_action.triggered.connect(self.save_snip)
        save_as_action = QtWidgets.QAction('Save As', self)
        save_as_action.triggered.connect(self.save_snip_as)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)

        # New menu
        new_menu = menubar.addMenu('New')
        new_action = QtWidgets.QAction('New Snip', self)
        new_action.triggered.connect(self.new_snip)
        new_menu.addAction(new_action)

        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        copy_text_action1 = QtWidgets.QAction('Copy Text from Method 1', self)
        copy_text_action1.triggered.connect(lambda: self.copy_text(1))
        copy_text_action2 = QtWidgets.QAction('Copy Text from Method 2', self)
        copy_text_action2.triggered.connect(lambda: self.copy_text(2))
        copy_text_action3 = QtWidgets.QAction('Copy Text from Method 3', self)
        copy_text_action3.triggered.connect(lambda: self.copy_text(3))
        edit_menu.addAction(copy_text_action1)
        edit_menu.addAction(copy_text_action2)
        edit_menu.addAction(copy_text_action3)

    def new_snip(self):
        self.hide()  # Hide the main window completely
        self.snipping_widget = SnippingWidget()
        self.snipping_widget.snip_saved.connect(self.on_snip_saved)
        self.snipping_widget.show()

    def on_snip_saved(self, snip):
        self.show()  # Restore the main window after snip
        self.snip = snip
        # Display the snipped image
        self.image_label.setPixmap(snip.scaled(
            self.image_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        return snip  # Return snip for further processing

    def display_extracted_text(self, extracted_text, method):
        if method == 1:
            self.text_edit1.setPlainText(extracted_text)
        elif method == 2:
            self.text_edit2.setPlainText(extracted_text)
        elif method == 3:
            self.text_edit3.setPlainText(extracted_text)

    def save_snip(self):
        if self.snip:
            default_path = 'snip.png'
            self.snip.save(default_path, 'PNG')
            QtWidgets.QMessageBox.information(self, 'Saved', f'Snip saved as {default_path}')
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'No snip to save.')

    def save_snip_as(self):
        if self.snip:
            options = QtWidgets.QFileDialog.Options()
            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save Snip As', '', 'PNG Files (*.png);;All Files (*)', options=options)
            if file_name:
                self.snip.save(file_name, 'PNG')
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'No snip to save.')

    def copy_text(self, method):
        if method == 1:
            extracted_text = self.text_edit1.toPlainText()
        elif method == 2:
            extracted_text = self.text_edit2.toPlainText()
        elif method == 3:
            extracted_text = self.text_edit3.toPlainText()
        else:
            extracted_text = ''

        if extracted_text:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(extracted_text)
            QtWidgets.QMessageBox.information(self, 'Copied', f'Text from Method {method} copied to clipboard.')
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'No text to copy.')
