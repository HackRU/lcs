import config
import qrcode
import base64

def email2qr(event, context):
    if 'email' not in event:
        return config.add_cors_headers({'statusCode':400, 'body':'Invalid request format.'})
    email = event['email']
    img = qrcode.make(email)
    encodedImg = base64.encodestring(img)
    return config.add_cors_headers({'statusCode':200, 'body':'data:image/png;base64,' + encodedImg})
