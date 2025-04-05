from .BaseOCR import get_ocr_engine
from .BaseTextProcessor import get_text_processor


class ImageToTextPipeline:
    def __init__(self, ocr_engine="google", text_processor="gemini", api_key=None):
        self.ocr = get_ocr_engine(ocr_engine)
        self.text_processor = get_text_processor(text_processor, api_key)

    def process_image(self, image_path):
        extracted_text = self.ocr.extract_text(image_path)
        processed_text = self.text_processor.process_text(extracted_text)
        return processed_text
