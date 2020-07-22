import argparse
import os
from uuid import uuid4

import qrcode
from fpdf import FPDF

# directory within which this file is within
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# pixels per inch
PPI = 72

# spacing between each QR code generated
QR_CODE_SPACING = 7

# width and height defined in terms of pixels within letter size paper
PAGE_WIDTH = 8.5 * PPI
PAGE_HEIGHT = 11 * PPI

# size of the QR code square generated
DEFAULT_WIDTH = 1.9


def check_side_length(arg: str):
    """
    Function used to verify the side length command line argument
    """
    try:
        # tries to convert string to float first
        num = float(arg)
        # verifies side length is not negative
        if num <= 0:
            print("Side length is too low. Using the default option of 1.9 inches")
            return DEFAULT_WIDTH
        # verifies side length is not more than such that at least 1 can fit within the defined dimensions
        if num * PPI >= PAGE_WIDTH - 2 * QR_CODE_SPACING:
            print("Side length is too high. Using the default option of 1.9 inches")
            return DEFAULT_WIDTH
        return num
    except ValueError:
        msg = f"Couldn't understand \"{arg}\". It should be a valid number or the string \"max\""
        raise argparse.ArgumentTypeError(msg)


def check_per_page(arg: str):
    """
    Function used to verify the number of QR codes to put per page
    """
    # if the argument is max, then most amount of images will be attempted to be fitted on each page
    if arg == "max":
        return arg
    # otherwise ensures the argument is a positive number
    if arg.isnumeric():
        num = int(arg)
        if num <= 0:
            print("QR codes per page is too low. Using the default option \"max\"")
            return "max"
        return num

    msg = f"Couldn't understand \"{arg}\". It should be a valid positive number or the string \"max\""
    raise argparse.ArgumentTypeError(msg)


def check_color(arg: str):
    """
    Function that ensures the given argument can be translated to a valid color
    """
    from PIL.ImageColor import getrgb
    # attempts to use getrgb to interpret the argument string and returns an error if that fails
    try:
        getrgb(arg)
        return arg
    except ValueError:
        msg = f"The color \"{arg}\" is not recognized as a valid color. You can specify the color through its name, " \
              "or using some common reference methods like rgb([r],[g],[b]) or #[color hex]"
        raise argparse.ArgumentTypeError(msg)


def handle_args():
    """
    Function used to handle command line arguments
    """
    arg_parser = argparse.ArgumentParser(description="Generate a given number of random QR codes using a given prefix "
                                                     "and output them into a PDF")
    arg_parser.add_argument("number", type=int, help="number of QR codes to generate")
    arg_parser.add_argument("prefix", type=str, help="prefix to use while generating the QR code")
    arg_parser.add_argument("-s", dest="side_length", type=check_side_length, required=False, default=1.9,
                            help="side length of the QR code square generated in *inches* (default: 1.9)")
    arg_parser.add_argument("-n", dest="per_page", type=check_per_page, required=False, default="max",
                            help="number QR codes to put per page of the PDF (default: max - fit as many as possible)")
    arg_parser.add_argument("-fc", dest="fill_color", type=check_color, required=False, default="black",
                            help="color of the QR code (default: black)")
    arg_parser.add_argument("-bc", dest="back_color", type=check_color, required=False, default="white",
                            help="color for the background of the QR code (default: white)")
    arg_parser.add_argument("-x", dest="x", type=int, required=False, default=17,
                            help="top left x coordinate for the QR code grid in *pixels* (default: 17)")
    arg_parser.add_argument("-y", dest="y", type=int, required=False, default=41,
                            help="top left y coordinate for the QR code grid in *pixels* (default: 41)")
    return arg_parser.parse_args()


def generate():
    """
    Function used to generate the QR codes
    """
    # fetches the command line arguments
    args = handle_args()
    # creates a QRCode instance to generate codes
    qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=0
    )
    # creates a FPDF instance to save generated QRCodes to PDF
    pdf = FPDF(unit="pt", format="letter")
    x = args.x
    y = args.y
    s = args.side_length * PPI - 1
    # adds the first page to the output PDF file
    pdf.add_page()

    # determines the minimum number of QR codes that can fit within one page and as long as the desired number of
    # codes per page is less than that, then it's considered valid
    use_max = True
    if args.per_page != "max":
        min_x_pages = (PAGE_WIDTH - args.x) // (s + QR_CODE_SPACING)
        min_y_pages = (PAGE_HEIGHT - args.y) // (s + QR_CODE_SPACING)
        if args.per_page <= min_x_pages * min_y_pages:
            use_max = False

    # for every QR code generated
    for i in range(args.number):
        # data is added in the format of [prefix]_[random UUID]
        qr.add_data(args.prefix + "_" + str(uuid4()))
        # the QR code is made by calling the make method
        qr.make(fit=True)
        # a temporary image file is generated to save the generated code
        tmp_img_loc = os.path.join(BASE_DIR, f"temp{i}.png")
        # the generated QR code is converted to an image and saved to this temp file
        qr.make_image(fill_color=args.fill_color, back_color=args.back_color).save(tmp_img_loc)
        # and this temp file's image is used to paste into the PDF (this is necessary because of how FPDF works)
        # it is pasted at the given (x,y) coordinate with the given side length
        pdf.image(tmp_img_loc, x, y, s, s)
        # finally this temp image is removed
        os.remove(tmp_img_loc)
        # if the maximum number of codes per page have reached, a new page is added to the PDF
        # and the top-left (x,y) coordinates are reset for the next page
        if not use_max and (i + 1) % args.per_page == 0:
            pdf.add_page()
            x = args.x
            y = args.y
        else:
            # otherwise, the x coordinate for pasting the image within PDF is shifted by the side length + spacing
            # to prepare for the next image to be shifted (essentially moving right within the page)
            x += s + QR_CODE_SPACING
            # if pasting another image at this new location would make it go out of page, then...
            if x + s + QR_CODE_SPACING > PAGE_WIDTH:
                # the y coordinate is increased to move down within the page
                y += s + QR_CODE_SPACING
                # again if pasting the next image would make it go out of the page then the entire page has been
                # exhausted, so a new page is added for new images and the top-left x,y coordinates are reset
                if y + s + QR_CODE_SPACING > PAGE_HEIGHT:
                    pdf.add_page()
                    x = args.x
                    y = args.y
                # otherwise, there is vertical space available so the x coordinate is reset to be left-aligned
                else:
                    x = args.x
        # the data within qr instance is cleared for next use
        qr.clear()
    # finally all the images are output into a PDF created within the current directory
    pdf.output(os.path.join(BASE_DIR, "qr_codes.pdf"))


if __name__ == '__main__':
    generate()
