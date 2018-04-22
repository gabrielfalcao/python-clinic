# -*- coding: utf-8 -*-
import io
import qrcode
from flask import Response

from python_clinic.logs import get_logger
from python_clinic.web.controllers import Controller


logger = get_logger(__name__)


class WebUIController(Controller):

    def make_qrcode_image(self, string):
        qr = qrcode.QRCode(
            # version=1,
            # # maximum error correction level for warehouse environment
            # error_correction=qrcode.constants.ERROR_CORRECT_H,
            # box_size=10,
            # border=4,
        )
        qr.add_data(string)
        img = qr.make_image()
        return img

    def png_response(self, data, status_code=200):
        return Response(data, status_code, mimetype='image/png')

    def qrcode_png_response(self, string, status_code=200):
        img = self.make_qrcode_image(string)
        out = io.BytesIO()
        img.save(out)
        return self.png_response(out.getvalue(), status_code)
