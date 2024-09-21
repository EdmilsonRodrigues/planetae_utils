import io
import os
import threading
import fitz
from PIL import Image, ImageDraw
from PIL.ImageFile import ImageFile
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
        images = convert_from_path(self.pdf_path, dpi=dpi, poppler_path=POPPLER_PATH)

        images_list = []

        # Save each page as an image file
        for i, image in enumerate(images):
            image_path = os.path.join(output_folder, f"page_{i+1}.{image_format}")
            image.save(image_path, image_format.upper())
            print(f"Saved {image_path}")
            images_list.append(image_path)

        return images_list

    def extract_images(
        self, page_number: int | None = None
    ) -> list[ImageFile | Image.Image]:
        if page_number is None:
            images_list: list[Image.Image | ImageFile] = []
            for page in range(self.pages):
                images_list += self.extract_images(page)
        else:
            images_list = []
            page = self.file.load_page(page_number)
            images = page.get_images(full=True)
            for image in images:
                xref = image[0]
                base_image = self.file.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))

                # Convert the image to RGB if it's in an unsupported mode
                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGB")

                images_list.append(image)
        return images_list

    def extract_drawings(self, page_number: int | None = None) -> list[dict]:
        if page_number is None:
            content = []
            for page in range(self.pages):
                content += self.extract_drawings(page)
        else:
            page = self.file.load_page(page_number)
            content = page.get_drawings()
        return content

    def extract_drawings_as_images(
        self, page_number: int | None = None
    ) -> list[Image.Image]:
        if page_number is None:
            images = []
            for page in range(self.pages):
                images += self.extract_drawings(page)
        else:
            images = []
            page = self.file.load_page(page_number)
            drawings = page.get_drawings()

            for drawing in drawings:
                # Create a blank canvas
                rect = drawing["rect"]
                width, height = int(rect.width), int(rect.height)

                if width <= 0 or height <= 0:
                    continue

                image = Image.new("RGB", (width, height), "white")
                draw = ImageDraw.Draw(image)
                for item in drawing["items"]:
                    color = drawing.get("color", "black")
                    if isinstance(color, tuple):
                        color = self.convert_color(color)
                    line_width = drawing.get("width", 1)
                    if line_width is None:
                        line_width = 1
                    else:
                        line_width = int(line_width)
                    match item[0]:
                        case "l":  # Line
                            start, end = item[1], item[2]
                            draw.line(
                                [start.x, start.y, end.x, end.y],
                                fill=color,
                                width=line_width,
                            )
                        case "r":
                            rect = item[1]
                            draw.rectangle(
                                [rect.x0, rect.y0, rect.x1, rect.y1],
                                outline=color,
                                width=line_width,
                            )
                        case "c":
                            points = [item[1], item[2], item[3], item[4]]
                            draw.line(
                                [(p.x, p.y) for p in points],
                                fill=color,
                                width=line_width,
                            )
                        case "p":
                            points = item[1]
                            draw.polygon(
                                [(p.x, p.y) for p in points],
                                outline=color,
                                width=line_width,
                            )
                        case "t":
                            start = item[1]
                            draw.text(
                                (start.x, start.y),
                                item[2],
                                fill=color,
                                font=drawing.get("font", None),
                            )
                        case _:
                            pass
                    # Add more shape types as needed
                    if image.mode not in ("RGB", "RGBA"):
                        image = image.convert("RGB")
                images.append(image)
        return images

    def extract_all_images(self, page_number: int | None = None) -> list[Image.Image]:
        threads = []
        images = []  # Initialize the images list outside the if-else block

        if page_number is None:
            for page in range(self.pages):
                thread = threading.Thread(
                    target=self._extract_and_append_images, args=(page, images)
                )
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
        else:
            images += self.extract_images(page_number)
            images += self.extract_drawings_as_images(page_number)

        return images

    def _extract_and_append_images(self, page: int, images: list[Image.Image]):
        extracted_images = self.extract_images(page)
        extracted_drawings = self.extract_drawings_as_images(page)

        with self.lock:
            images += extracted_images
            images += extracted_drawings

    @staticmethod
    def convert_color(color: tuple[float, ...]) -> tuple[int, ...]:
        return tuple(int(c * 255) for c in color)

    def convert_drawings_to_images(self, drawings: list[dict]) -> list[Image.Image]:
        images = []
        for drawing in drawings:
            # Create a blank canvas
            rect = drawing["rect"]
            width, height = int(rect.width), int(rect.height)

            if width <= 0 or height <= 0:
                continue

            image = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(image)
            for item in drawing["items"]:
                color = drawing.get("color", "black")
                if isinstance(color, tuple):
                    color = self.convert_color(color)
                line_width = drawing.get("width", 1)
                if line_width is None:
                    line_width = 1
                else:
                    line_width = int(line_width)
                match item[0]:
                    case "l":  # Line
                        start, end = item[1], item[2]
                        draw.line(
                            [start.x, start.y, end.x, end.y],
                            fill=color,
                            width=line_width,
                        )
                    case "r":
                        rect = item[1]
                        draw.rectangle(
                            [rect.x0, rect.y0, rect.x1, rect.y1],
                            outline=color,
                            width=line_width,
                        )
                    case "c":
                        points = [item[1], item[2], item[3], item[4]]
                        draw.line(
                            [(p.x, p.y) for p in points],
                            fill=color,
                            width=line_width,
                        )
                    case "p":
                        points = item[1]
                        draw.polygon(
                            [(p.x, p.y) for p in points],
                            outline=color,
                            width=line_width,
                        )
                    case "t":
                        start = item[1]
                        draw.text(
                            (start.x, start.y),
                            item[2],
                            fill=color,
                            font=drawing.get("font", None),
                        )
                    case _:
                        pass
                # Add more shape types as needed
                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGB")
            images.append(image)
        return images
