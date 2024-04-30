from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout, QFileDialog
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor
import qrcode
import sys

class ToggleSwitch(QWidget):
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self.checked = False
        self.bg_color = {False: QColor("#ccc"), True: QColor("#7289DA")}
        self.knob_color = QColor("#fff")
        self.anim = QTimer(self)
        self.anim.setInterval(30)
        self.anim.timeout.connect(self.animate)
        self.knob_position = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.bg_color[self.checked]))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() / 2, self.height() / 2)
        knob_x = self.width() - self.height() if self.checked else 0
        painter.setBrush(QBrush(self.knob_color))
        painter.drawEllipse(knob_x, 0, self.height(), self.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.checked = not self.checked
            self.anim.start()
            self.clicked.emit()

    def animate(self):
        final_position = self.width() - self.height() if self.checked else 0
        step = (final_position - self.knob_position) // 10 or (1 if final_position > self.knob_position else -1)
        self.knob_position += step
        if self.knob_position == final_position:
            self.anim.stop()
        self.update()

class QRCodeGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint)
        self.dark_mode = False
        self.initUI()
        self.updateStyleSheet(self.dark_mode)
        self.qr_cache = None
        self.m_drag = False
        self.m_drag_position = QPoint()

    def updateStyleSheet(self, enabled):
        style = {
            True: {'bg': '#333', 'text': '#FFF', 'button': '#555', 'hover': '#666', 'line': '#555'},
            False: {'bg': '#FFF', 'text': '#000', 'button': '#EEE', 'hover': '#DDD', 'line': '#CCC'}
        }
        s = style[enabled]
        self.setStyleSheet(f"""
            QWidget {{ background-color: {s['bg']}; color: {s['text']}; }}
            QPushButton {{ background-color: {s['button']}; border: none; padding: 10px 15px; margin: 5px; }}
            QPushButton:hover {{ background-color: {s['hover']}; }}
            QLineEdit {{ background-color: {s['button']}; color: {s['text']}; border: 2px solid {s['line']}; padding: 10px; margin: 5px; }}
        """)

    def initUI(self):
        self.resize(400, 350)
        self.setWindowTitle("QR Code Generator")

        top_layout = QHBoxLayout()
        self.switch = ToggleSwitch()
        self.switch.clicked.connect(lambda: self.updateStyleSheet(self.switch.checked))
        self.close_button = QPushButton("✖")
        self.close_button.clicked.connect(self.close)
        top_layout.addWidget(self.switch)
        top_layout.addStretch(1)
        top_layout.addWidget(self.close_button)

        mid_layout = QHBoxLayout()
        self.textbox = QLineEdit()
        self.textbox.setPlaceholderText("Enter text or URL here...")
        mid_layout.addWidget(self.textbox)

        bottom_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate QR")
        self.generate_button.clicked.connect(self.on_click)
        self.save_button = QPushButton("Save QR")
        self.save_button.clicked.connect(self.save_image)
        bottom_layout.addWidget(self.generate_button)
        bottom_layout.addWidget(self.save_button)

        self.image_label = QLabel()
        self.image_label.setFixedSize(300, 300)
        self.image_label.setAlignment(Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(mid_layout)
        main_layout.addWidget(self.image_label, 0, Qt.AlignCenter)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_drag_position = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.m_drag and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.m_drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_drag = False

    def on_click(self):
        self.generateQRCode(self.textbox.text())

    def generateQRCode(self, text):
        if self.qr_cache != (text, self.switch.checked):
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save("qr_code_temp.png")
            self.qr_cache = (text, self.switch.checked)
        pixmap = QPixmap("qr_code_temp.png").scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            pixmap = self.image_label.pixmap()
            pixmap.save(file_path, "PNG")

def main():
    app = QApplication(sys.argv)
    qr_code_generator = QRCodeGenerator()
    qr_code_generator.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
