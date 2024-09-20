import io
import fitz
from PIL import Image
from PIL.ImageFile import ImageFile


class PDFHandler:
    pages: int

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

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

    def extract_images(self, page_number: int | None = None) -> list[ImageFile]:
        images_list: list[ImageFile] = []
        if page_number is None:
            for page in range(self.pages):
                self.extract_images(page)
        else:
            page = self.file.load_page(page_number)
            images = page.get_images(full=True)
            for image in images:
                xref = image[0]
                base_image = self.file.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                images_list.append(image)
        return images_list
