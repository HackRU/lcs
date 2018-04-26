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
    It also takes optional parameters fgOpacity and bgOpacity,
    which set the foreground and background opacity, respectively.
    It can also take a boolean transparentBackground which, if true,
    overrides bgOpacity and makes the background fully transparent.
    Provided this, the function returns the base-64
    encoded QR code for the email in color passed in
    as 'color' and background color passed as 'background'.
    """

    # We default to a black on white QR
    # and full opacity in both the foreground and background.
    color = event.get('color', [0x0,0x0,0x0])
    background = event.get('background', [0xff,0xff,0xff])
    fgOpacity = event.get('fgOpacity', 0xff)
    bgOpacity = event.get('bgOpacity', 0xff)
    bgOpacity = 0x0 if event.get('transparentBackground') else bgOpacity

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
    a = pilImg.point(lambda x: fgOpacity if x == 0 else bgOpacity, mode='L')
    #we merge the RGB processed as above.
    img = PIL.Image.merge('RGBA', (r,g,b,a))
    #save as a byte array
    byteArr = io.BytesIO()
    img.save(byteArr, format='PNG')
    byteImg = byteArr.getvalue()
    #then read and encode.
    encodedImg = base64.standard_b64encode(byteImg)
    return config.add_cors_headers({'statusCode':200, 'body':'data:image/png;base64,' + encodedImg.decode()})
