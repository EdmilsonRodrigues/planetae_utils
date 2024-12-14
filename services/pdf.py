import asyncio
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

    async def __aenter__(self):
        await asyncio.get_event_loop().run_in_executor(None, self.open)
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await asyncio.get_event_loop().run_in_executor(None, self.close)

    def conver_pdf_to_images(
        self, output_folder: str, image_format: str = "png", dpi: int = 300
    ) -> list[str]:
        # Ensure output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Convert PDF pages to images
        if os.name == "nt":
            if not POPPLER_PATH:
                raise ValueError(
                    "Please provide the path to the Poppler binaries in the config file"
                )
            images = convert_from_path(
                self.pdf_path, dpi=dpi, poppler_path=POPPLER_PATH
            )
        else:
            # Remember to install poppler-utils
            images = convert_from_path(self.pdf_path, dpi=dpi)

        images_list = []

        # Save each page as an image file
        for i, image in enumerate(images):
            image_path = os.path.join(
                output_folder, f"page_{i + 1}.{image_format}"
            )
            image.save(image_path, image_format.upper())
            print(f"Saved {image_path}")
            images_list.append(image_path)

        return images_list
    
    async def async_convert_pdf_to_images(
        self, output_folder: str, image_format: str = "png", dpi: int = 300
    ) -> list[str]:
        return await asyncio.get_event_loop().run_in_executor(None, self.conver_pdf_to_images, output_folder, image_format, dpi)
