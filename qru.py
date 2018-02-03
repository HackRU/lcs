import io
import config
import qrcode
import PIL
import base64

def email2qr(event, context):
    color = (0,0,192)
    if 'email' not in event:
        return config.add_cors_headers({'statusCode':400, 'body':'Invalid request format.'})
    email = event['email']
    pilImg = qrcode.make(email)
    r = pilImg.point(lambda x: color[0] if x == 0 else 255, mode='L')
    g = pilImg.point(lambda x: color[1] if x == 0 else 255, mode='L')
    b = pilImg.point(lambda x: color[2] if x == 0 else 255, mode='L')
    img = PIL.Image.merge('RGB', (r,g,b))
    byteArr = io.BytesIO()
    img.save(byteArr, format='PNG')
    byteImg = byteArr.getvalue()
    encodedImg = base64.standard_b64encode(byteImg)
    return config.add_cors_headers({'statusCode':200, 'body':'data:image/png;base64,' + encodedImg.decode()})
