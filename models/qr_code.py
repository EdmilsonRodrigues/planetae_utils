from typing import Iterator
from PIL.ImageFile import ImageFile
from pyzbar.pyzbar import decode


class QrCodeHandler:
    @staticmethod
    def scan_qr_codes(images: Iterator[ImageFile]):
        qr_codes = []

        for image in images:
            qr_code = QrCodeHandler.scan_qr_code(image)
            if qr_code:
                qr_codes.append(qr_code)

        return qr_codes

    @staticmethod
    def scan_qr_code(image: ImageFile):
        decoded_objects = decode(image)

        for obj in decoded_objects:
            return obj.data.decode("utf-8")
