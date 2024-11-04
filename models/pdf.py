import os
import threading
import fitz
from pdf2image import convert_from_path

from config import POPPLER_PATH


class PDFHandler:
    pages: int

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.lock = threading.Lock()

    def open(self):
        self.file = fitz.open(self.pdf_path)
        self.pages = self.file.page_count

    def close(self):
        self.file.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def conver_pdf_to_images(
        self, output_folder: str, image_format: str = "png", dpi: int = 300
    ) -> list[str]:
        # Ensure output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Convert PDF pages to images
        images = convert_from_path(
            self.pdf_path, dpi=dpi, poppler_path=POPPLER_PATH
        )

        images_list = []

        # Save each page as an image file
        for i, image in enumerate(images):
            image_path = os.path.join(
                output_folder, f"page_{i+1}.{image_format}"
            )
            image.save(image_path, image_format.upper())
            print(f"Saved {image_path}")
            images_list.append(image_path)

        return images_list
