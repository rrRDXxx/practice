import os
import json
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QIcon, QImage
from PyQt6.QtCore import Qt, QSettings
from PIL.ImageQt import ImageQt
from image_processor import ImageProcessor

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.processor = ImageProcessor()

        self.original_img = None
        self.processed_img = None

        self.last_processed_img = None

        self.history = self.load_history()
        self.settings = QSettings("Mallenom", "ImageEditorProj4")

        os.makedirs("logs", exist_ok=True)
        os.makedirs("output", exist_ok=True)

        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle("Редактор изображений - Проект 4 (Малленом Системс)")
        self.setFixedSize(1200, 700)
        self.setAcceptDrops(True)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Кнопки
        btn_bar = QHBoxLayout()
        btn_load = QPushButton("Загрузить изображение")
        btn_load.clicked.connect(self.load_image_dialog)
        btn_bar.addWidget(btn_load)

        self.btn_undo = QPushButton("Отменить")
        self.btn_undo.clicked.connect(self.undo)
        self.btn_undo.setEnabled(False)
        btn_bar.addWidget(self.btn_undo)

        btn_save = QPushButton("Сохранить результат")
        btn_save.clicked.connect(self.save_image)
        btn_bar.addWidget(btn_save)
        btn_bar.addStretch()
        layout.addLayout(btn_bar)

        params = QGroupBox("Параметры обработки")
        params.setMaximumWidth(160)
        form = QFormLayout(params)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(800)
        self.width_spin.setFixedSize(60, 20)
        form.addRow("Ширина:", self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(600)
        self.height_spin.setFixedSize(60, 20)
        form.addRow("Высота:", self.height_spin)

        self.chk_sharpen = QCheckBox("Повысить резкость")
        form.addRow(self.chk_sharpen)

        self.chk_contour = QCheckBox("Контуры: вкл")
        form.addRow(self.chk_contour)

        layout.addWidget(params)

        imgs_layout = QHBoxLayout()
        self.lbl_orig = QLabel("Оригинал")
        self.lbl_orig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_orig.setFixedSize(640, 490)
        self.lbl_orig.setStyleSheet("border: 2px solid gray; background: white;")
        imgs_layout.addWidget(self.lbl_orig)

        self.lbl_proc = QLabel("После обработки")
        self.lbl_proc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_proc.setFixedSize(640, 490)
        self.lbl_proc.setStyleSheet("border: 2px solid gray; background: white;")
        # self.lbl_proc
        imgs_layout.addWidget(self.lbl_proc)

        layout.addLayout(imgs_layout)

        # layout.addSpacing(200)

        self.info_label = QLabel("Информация: -")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.width_spin.valueChanged.connect(self.apply_processing)
        self.height_spin.valueChanged.connect(self.apply_processing)
        self.chk_sharpen.stateChanged.connect(self.apply_processing)
        self.chk_contour.stateChanged.connect(self.apply_processing)


    def load_image_dialog(self):
        last_dir = self.settings.value("last_dir", "")
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение", last_dir,
            "Изображения (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
        )
        if path:
            self.load_image(path)

    def load_image(self, path: str):

        try:

            self.original_img = self.processor.load_image(path)

            self.display_image(self.original_img, self.lbl_orig)

            self.update_info()
            self.apply_processing()

            self.settings.setValue("last_dir", os.path.dirname(path))

            self.add_history("Загрузка", {"path": path})

            self.btn_undo.setEnabled(False)

        except Exception as e:

            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{e}")

    def display_image(self, pil_img, label: QLabel):

        if pil_img is None: 
            return
        
        qimg = ImageQt(pil_img)

        pixmap = QPixmap.fromImage(qimg)
        
        label.setPixmap(pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation))

    def update_info(self):

        if not self.original_img:

            self.info_label.setText("Информация: —")

            return
        
        # print(self.)
        
        info = self.processor.get_info(self.original_img)

        text = (f"Ширина: {info['width']} px | "
                f"Высота: {info['height']} px | "
                f"Формат: {info['format']} | "
                f"Режим: {info['mode']}")
        
        self.info_label.setText(text)

        self.width_spin.blockSignals(True)
        self.height_spin.blockSignals(True)
        self.width_spin.setValue(info['width'])
        self.height_spin.setValue(info['height'])
        self.width_spin.blockSignals(False)
        self.height_spin.blockSignals(False)

    def apply_processing(self):

        if not self.original_img:

            return

        self.last_processed_img = self.processed_img
        self.btn_undo.setEnabled(True)

        size = (self.width_spin.value(), self.height_spin.value())
        new_size = size if size != self.original_img.size else None

        try:
            self.processed_img = self.processor.process(
                self.original_img,
                new_size,
                self.chk_sharpen.isChecked(),
                self.chk_contour.isChecked()
            )
            self.display_image(self.processed_img, self.lbl_proc)
            self.add_history("Обработка", {
                "size": size,
                "sharpen": self.chk_sharpen.isChecked(),
                "contour": self.chk_contour.isChecked()
            })
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def undo(self):
        
        if self.last_processed_img:

            self.processed_img = self.last_processed_img

            self.display_image(self.processed_img, self.lbl_proc)

            old_size = self.last_processed_img.size

            self.width_spin.setValue(old_size[0])
            self.height_spin.setValue(old_size[1])

            self.last_processed_img = None

            self.btn_undo.setEnabled(False)

            self.add_history("Отмена действия")

    def save_image(self):
        if not self.processed_img:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить", "output/processed.png",
            "PNG (*.png);;JPEG (*.jpg *.jpeg)"
        )
        if path:
            self.processor.save(self.processed_img, path)
            self.add_history("Сохранение", {"path": path})
            QMessageBox.information(self, "Готово", f"Изображение сохранено:\n{path}")

    def add_history(self, action: str, params: dict = None):
        if params is None:
            params = {}
        entry = {
            "time": datetime.now().isoformat(sep=" ", timespec="seconds"),
            "action": action,
            "params": params
        }
        self.history.append(entry)
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def load_history(self):
        if os.path.exists("history.json"):
            try:
                with open("history.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        path = url.toLocalFile()
        if path.lower().split(".")[-1] in ["png", "jpg", "jpeg", "bmp", "tiff", "webp"]:
            self.load_image(path)
