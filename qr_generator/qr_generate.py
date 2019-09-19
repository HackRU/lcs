import qrcode
from uuid import uuid4
import argparse
from fpdf import FPDF
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
QR_CODE_SPACING = 0.1
PAGE_WIDTH = 8.5
PAGE_HEIGHT = 11


def check_side_length(arg: str):
    try:
        num = float(arg)
        if num <= 0:
            print("Side length is too low. Using the default option of 2 inches")
            return 2
        if num >= PAGE_WIDTH - 2 * QR_CODE_SPACING:
            print("Side length is too high. Using the default option of 2 inches")
            return 2
        return num
    except ValueError:
        msg = f"Couldn't understand \"{arg}\". It should be a valid number or the string \"max\""
        raise argparse.ArgumentTypeError(msg)


def check_per_page(arg: str):
    if arg == "max":
        return arg
    if arg.isnumeric():
        num = int(arg)
        if num <= 0:
            print("QR codes per page is too low. Using the default option \"max\"")
            return "max"
        return num

    msg = f"Couldn't understand \"{arg}\". It should be a valid positive number or the string \"max\""
    raise argparse.ArgumentTypeError(msg)


def check_color(arg: str):
    from PIL.ImageColor import getrgb
    try:
        getrgb(arg)
        return arg
    except ValueError:
        msg = f"The color \"{arg}\" is not recognized as a valid color. You can specify the color through its name, " \
              "or using some common reference methods like rgb([r],[g],[b]) or #[color hex]"
        raise argparse.ArgumentTypeError(msg)


def handle_args():
    arg_parser = argparse.ArgumentParser(description="Generate a given number of random QR codes using a given prefix "
                                                     "and output them into a PDF")
    arg_parser.add_argument("number", type=int, help="number of QR codes to generate")
    arg_parser.add_argument("prefix", type=str, help="prefix to use while generating the QR code")
    arg_parser.add_argument("-s", dest="side_length", type=check_side_length, required=False, default=2,
                            help="side length of the QR code square generated in *inches* (default: 2)")
    arg_parser.add_argument("-n", dest="per_page", type=check_per_page, required=False, default="max",
                            help="number QR codes to put per page of the PDF (default: max - fit as many as possible)")
    arg_parser.add_argument("-fc", dest="fill_color", type=check_color, required=False, default="black",
                            help="color of the QR code (default: black)")
    arg_parser.add_argument("-bc", dest="back_color", type=check_color, required=False, default="white",
                            help="color for the background of the QR code (default: white)")
    return arg_parser.parse_args()


def generate():
    args = handle_args()
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=0
    )
    pdf = FPDF(unit="in", format="letter")
    x = y = QR_CODE_SPACING
    s = args.side_length
    pdf.add_page()

    use_max = True
    if args.per_page != "max" and QR_CODE_SPACING + (s + QR_CODE_SPACING) * args.per_page < PAGE_WIDTH:
        use_max = False

    for i in range(args.number):
        qr.add_data(args.prefix + "_" + str(uuid4()))
        qr.make(fit=True)
        tmp_img_loc = os.path.join(BASE_DIR, f"temp{i}.png")
        qr.make_image(fill_color=args.fill_color, back_color=args.back_color).save(tmp_img_loc)
        pdf.image(tmp_img_loc, x, y, s, s)
        os.remove(tmp_img_loc)
        if not use_max and (i+1) % args.per_page == 0:
            pdf.add_page()
            x = y = QR_CODE_SPACING
        else:
            x += s + QR_CODE_SPACING
            if x + s + QR_CODE_SPACING > PAGE_WIDTH:
                y += s + QR_CODE_SPACING
                if y + s + QR_CODE_SPACING > PAGE_HEIGHT:
                    pdf.add_page()
                    x = y = QR_CODE_SPACING
                else:
                    x = QR_CODE_SPACING

        qr.clear()
    pdf.output(os.path.join(BASE_DIR, "qr_codes.pdf"))


if __name__ == '__main__':
    generate()
