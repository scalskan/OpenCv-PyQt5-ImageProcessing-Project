import sys
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox

class VideoWidget(QWidget):
    def __init__(self, video_path):
        super().__init__()

        # Video dosyasını yükleme
        self.capture = cv2.VideoCapture(video_path)

        # QLabel widget oluşturma ve yatay hizalama
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.last_frame_label = QLabel()
        self.last_frame_label.setAlignment(Qt.AlignCenter)

        # QHBoxLayout oluşturma ve QLabel widget ekleme
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.video_label)
        self.layout.addWidget(self.last_frame_label)

        # Ana düzeni oluşturma ve QHBoxLayout'a ekleme
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.layout)

        # Görüntü Al, Başlat/Durdur ve Kapat buttonları oluşturma
        self.capture_button = QPushButton('Goruntu Al')
        self.toggle_button = QPushButton('Baslat')
        self.close_button = QPushButton('Kapat')

        # Dikey buttonlar için QVBoxLayout oluşturma
        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.capture_button)
        self.button_layout.addWidget(self.toggle_button)
        self.button_layout.addWidget(self.close_button)

        # Ana düzeni güncelleme
        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)

        # Buttonlara tıklama işlemlerini bağlama
        self.capture_button.clicked.connect(self.capture_frame)
        self.toggle_button.clicked.connect(self.toggle_video)
        self.close_button.clicked.connect(self.close_application)

        # Video durumu
        self.playing = False

        # Timer oluşturma
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        # Görüntü boyutu
        self.width = 960
        self.height = 540

        # Görüntü sayacı
        self.frame_count = 0

        # Son alınan görüntü
        self.last_frame = None

    def capture_frame(self):
        # Videodan bir kare alma
        ret, frame = self.capture.read()
        if ret:
            # Son alınan görüntüyü güncelleme
            self.last_frame = frame

            # Görüntüyü PyQt5 arayüzünde göstermek için uygun formata dönüştürme. RGB tercih edildi
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = QPixmap.fromImage(convert_to_qt_format.scaled(self.width // 2, self.height, Qt.KeepAspectRatio))
            self.video_label.setPixmap(p)

            # Görüntüyü aynı dizine kaydetme
            self.frame_count += 1
            file_path = f"frame_{self.frame_count}.png"
            cv2.imwrite(file_path, frame)
            print(f"Goruntu kaydedildi: {file_path}")

            # Son alınan görüntüyü ayrı bir QLabel'da gösterme
            last_frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            last_frame_qimage = QImage(last_frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            last_frame_pixmap = QPixmap.fromImage(last_frame_qimage.scaled(self.width // 2, self.height, Qt.KeepAspectRatio))
            self.last_frame_label.setPixmap(last_frame_pixmap)

        else:
            QMessageBox.warning(self, 'Uyari', 'Video sonuna ulasildi.')

    def toggle_video(self):
        # Video durumunu değiştirme
        self.playing = not self.playing
        if self.playing:
            self.toggle_button.setText('Durdur')
            self.timer.start(33)  # 30 FPS (1000 ms / 30)
        else:
            self.toggle_button.setText('Baslat')
            self.timer.stop()

    def update_frame(self):
        # Video oynatılıyorsa ve dosya okunabilir durumdaysa bir kare alma
        ret, frame = self.capture.read()
        if ret:
            # Görüntüyü PyQt5 arayüzünde göstermek için uygun formata dönüştürme
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = QPixmap.fromImage(convert_to_qt_format.scaled(self.width // 2, self.height, Qt.KeepAspectRatio))
            self.video_label.setPixmap(p)

        else:
            QMessageBox.warning(self, 'Uyari', 'Video sonuna ulasildi.')
            self.toggle_button.setText('Baslat')  # Video sonunda 'Baslat' düğmesini ayarlayın
            self.timer.stop()  # Timer'ı durdurun

    def close_application(self):
        # Uygulamayı kapatma
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    video_path = "video.MOV"  # Videonun yeri

    window = VideoWidget(video_path)
    window.setWindowTitle('Video Goruntusu')
    window.setGeometry(100, 100, window.width + 200, window.height)  # Pencere boyutu
    window.show()
    sys.exit(app.exec_())
