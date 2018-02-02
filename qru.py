import io
import config
import qrcode
import base64

def email2qr(event, context):
    if 'email' not in event:
        return config.add_cors_headers({'statusCode':400, 'body':'Invalid request format.'})
    email = event['email']
    pilImg = qrcode.make(email)
    byteArr = io.BytesIO()
    pilImg.save(byteArr)
    byteImg = byteArr.getvalue()
    encodedImg = base64.encodestring(byteImg)
    return config.add_cors_headers({'statusCode':200, 'body':'data:image/png;base64,' + encodedImg})

#if __name__ == '__main__':
#    pilImg = qrcode.make('test@example.com')
#    byteArr = io.BytesIO()
#    pilImg.save(byteArr)
#    byteImg = byteArr.getvalue()
#    encodedImg = base64.encodestring(byteImg)
#    print(encodedImg)
