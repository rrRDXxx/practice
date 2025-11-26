



import logging
from PIL import Image, ImageFilter
from typing import Tuple, Optional
import os
import time

os.makedirs("logs", exist_ok = True)

logging.basicConfig(
    filename = "logs/app.log",
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s",
    encoding = "utf-8"
)

def speedtest(func):

    def wrapper(*args, **kwargs):

        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        print(f"{func.__name__} выполнена за {(end-start) * 1000:.2f}ms")

        return result
    
    return wrapper

class ImageProcessor:

    @speedtest
    def load_image(self, path: str) -> Image.Image:

        if not os.path.exists(path):

            raise FileNotFoundError(f"Файл не найден: {path}")
        
        imgFile = Image.open(path) # .convert("RGB")

        img = imgFile.convert("RGB")
        img.format = imgFile.format

        logging.info(f"Загружено изображение: {path} ({img.size})")

        return img

    
    @speedtest
    def get_info(self, img: Image.Image) -> dict:

        # QImag

        return {
            "width": img.width,
            "height": img.height,
            "format": img.format or "UNKNOWN",
            "mode": img.mode
        }

    @speedtest
    def resize(self, img: Image.Image, size: Tuple[int, int]) -> Image.Image:

        if size == img.size:

            return img.copy()
        
        resized = img.resize(size, Image.LANCZOS)

        logging.info(f"Изменение размера → {size}")

        return resized

    @speedtest
    def sharpen(self, img: Image.Image) -> Image.Image:

        sharpened = img.filter(ImageFilter.SHARPEN)

        logging.info("Применено повышение резкости")

        return sharpened

    
    @speedtest
    def contour(self, img: Image.Image) -> Image.Image:

        contoured = img.filter(ImageFilter.CONTOUR)

        logging.info("Применён контурный фильтр")
        
        return contoured

    @speedtest
    def process(self, sourceImage: Image.Image, new_size: Tuple[int, int], apply_sharpen: bool, apply_contour: bool) -> Image.Image:

        processedImage : Image.Image = sourceImage.copy()
        
        if new_size and new_size != sourceImage.size:
            processedImage = self.resize(processedImage, new_size)

        if apply_sharpen:
            processedImage = self.sharpen(processedImage)

        if apply_contour:
            processedImage = self.contour(processedImage)
            
        logging.info("Обработка завершена")

        return processedImage

    @speedtest
    def save(self, img: Image.Image, path: str):

        img.save(path)

        logging.info(f"Изображение сохранено: {path}")