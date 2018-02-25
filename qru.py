import io
import config
import qrcode
import PIL
import base64

def email2qr(event, context):
    """
    The event is expected to have an email
    and optionally a color and a background (color)
    (both being 3-tuples of RGB values).
    Provided this, the function returns the base-64
    encoded QR code for the email in color passed in
    as 'color' and background color passed as 'background'.
    """

    #We default to a black on white QR.
    if 'color' not in event:
        color = (0,0,192)
    else:
        color = event['color']
    if 'background' not  in event:
        background = (255,255,255)
    else:
        background = event['background']

    #email must be provided
    if 'email' not in event:
        return config.add_cors_headers({'statusCode':400, 'body':'Invalid request format.'})

    email = event['email']
    pilImg = qrcode.make(email)
    #We take the bitmap and put the foreground color if the bit is 0
    #and the background otherwise.
    r = pilImg.point(lambda x: color[0] if x == 0 else background[0], mode='L')
    g = pilImg.point(lambda x: color[1] if x == 0 else background[1], mode='L')
    b = pilImg.point(lambda x: color[2] if x == 0 else background[2], mode='L')
    #we merge the RGB processed as above.
    img = PIL.Image.merge('RGB', (r,g,b))
    #save as a byte array
    byteArr = io.BytesIO()
    img.save(byteArr, format='PNG')
    byteImg = byteArr.getvalue()
    #then read and encode.
    encodedImg = base64.standard_b64encode(byteImg)
    return config.add_cors_headers({'statusCode':200, 'body':'data:image/png;base64,' + encodedImg.decode()})
