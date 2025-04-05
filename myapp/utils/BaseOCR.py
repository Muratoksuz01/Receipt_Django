from abc import ABC, abstractmethod
from google.cloud import vision
import pytesseract
from PIL import Image

class BaseOCR(ABC):
    @abstractmethod
    def extract_text(self, image_path):
        pass

class GoogleVisionOCR(BaseOCR):
    def extract_text(self, image_path):
        client = vision.ImageAnnotatorClient()
        with open(image_path, "rb") as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            return texts[0].description
        else:
            return "Metin bulunamadı."

class PytesseractOCR(BaseOCR):
    def __init__(self):
        self.tesseract_path = "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    def extract_text(self, image_path):
        return pytesseract.image_to_string(Image.open(image_path))

# OCR Seçici Fonksiyon
def get_ocr_engine(engine="google"):
    if engine == "google":
        return GoogleVisionOCR()
    elif engine == "pytesseract":
        return PytesseractOCR()
    else:
        raise ValueError("Geçersiz OCR Motoru Seçildi")
