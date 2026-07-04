import mss
import sys
import numpy as np
import easyocr
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QCursor

reader = easyocr.Reader(['en', 'ru'])
class AIworker(QThread):
    signals_coords = pyqtSignal(list)
    def __init__(self):
        super().__init__()
        self.coords_to_draw = []
        self.bad_words = ['python','frame', 'import' ]

    def run(self):
        with mss.mss() as sct:
            while True:
                self.cursor_pos = QCursor.pos()
                mouse_x = self.cursor_pos.x()
                mouse_y = self.cursor_pos.y()
                top = mouse_y - 200
                left = mouse_x - 200
                width_cursor = 400
                height_cursor = 400
            
            
                sct_img = sct.grab({"top": top, "left": left, "width": width_cursor, "height": height_cursor})

                frame = np.array(sct_img)
                frame = frame[:,:,:3][:,:,::-1]
                results = reader.readtext(frame, text_threshold=0.5, low_text=0.3)

                self.coords_to_draw.clear()

                for bbox, text, confidence in results:
                    for bad_word in self.bad_words:
                        if(bad_word in text.lower()):
                            width = bbox[2][0] - bbox[0][0]
                            height = bbox[2][1] - bbox[0][1]

                            self.coords_to_draw.append((bbox[0][0] + left, bbox[0][1] + top , width, height))
                            break
                self.signals_coords.emit(self.coords_to_draw)

class Blackshape(QWidget):

    def __init__(self):
        super().__init__()

        self.setGeometry(0,0,1920,1080)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.Window|
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowTransparentForInput
        )

        self.worker = AIworker()
        self.worker.start()
        self.worker.signals_coords.connect(self.signalCatcher)
        self.coords_to_draw = []
    
    def signalCatcher(self, coords):
        self.coords_to_draw = coords
        self.update()

    def paintEvent(self, event):
        self.painter = QPainter(self)
        self.painter.setBrush(QColor(0,0,0))
        for x, y , w, h in self.coords_to_draw:
            self.painter.drawRect(int(x), int(y), int(w) , int(h))
        self.painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Blackshape()
    window.show()

    sys.exit(app.exec())