#!/usr/bin/env python
# run with `chromium $(python qr_script.py test@example.com)`

import io
import qrcode
import PIL
import base64
import sys

def email2qr(email):
    #construct the QR code
    img = qrcode.make(email)
    #save as a byte array
    byteArr = io.BytesIO()
    img.save(byteArr, format='PNG')
    byteImg = byteArr.getvalue()
    #then read and encode.
    encodedImg = base64.standard_b64encode(byteImg)
    return 'data:image/png;base64,' + encodedImg.decode()

if __name__ == '__main__':
    email = sys.argv[1] if len(sys.argv) >= 2 else 'test@example.com'
    print(email2qr(email))
