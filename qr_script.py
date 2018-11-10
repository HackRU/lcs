#!/usr/bin/env python
# run with `chromium $(python qr_script.py test@example.com)`

import io
import qrcode
import PIL
import base64
import sys
import subprocess

SAMPLE_CODE_BASE_PATH = '/home/architect/dymo-cups-drivers/samples/test_label/'
PHOTO_PATH = SAMPLE_CODE_BASE_PATH + 'tel.png'
PRINTER_CMD = SAMPLE_CODE_BASE_PATH + 'TestLabel'

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

def run_printer(p_exec, email, qr_path):
    #mk QR like above...
    img = qrcode.make(email)
    with open(qr_path, 'wb') as qr_out:
        img.save(qr_out, format='PNG')
    pr = subprocess.run(p_exec)
    print(pr)
    return pr.returncode

if __name__ == '__main__':
    email = sys.argv[1] if len(sys.argv) >= 2 else 'rnd@hackru.org'
    name = sys.argv[2] if len(sys.argv) >= 3 else 'Ms. Cupcake'
    print(run_printer([PRINTER_CMD, 'labels', name, email], email, PHOTO_PATH))
