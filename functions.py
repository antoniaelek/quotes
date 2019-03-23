from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from textwrap import wrap
import requests
from io import BytesIO
from datetime import datetime

url = "https://source.unsplash.com/featured/1600x900/?landscape"
fonts_folder = "data/fonts/"
font = fonts_folder + "Roboto-Regular.ttf"
colour = (255, 255, 255, 255)
img_margin = 40
img_fraction = 0.8


def _calculate_font_size(font_file, text, image, image_fraction):
    """
    Calculates font size so that the text fits the specified fraction of image width.
    :param font_file: path to font file to use
    :param text: text to calculate width for
    :param image: image to fit
    :param image_fraction: fraction of image width to fit text to
    :return: font size that fits image
    """
    font_size = 1
    text_font = ImageFont.truetype(font_file, 12)

    # find font size that fits width
    while text_font.getsize(text)[0] < image_fraction * image.size[0]:
        # iterate until the text size is just larger than the criteria
        font_size += 1
        text_font = ImageFont.truetype(font_file, font_size)

    # de-increment to be sure it is less than criteria
    font_size = font_size - 1

    while text_font.getsize(text)[1] > 0.3 * image.size[1]:
        # iterate until the text size is just larger than the criteria
        font_size -= 1
        text_font = ImageFont.truetype(font_file, font_size)

    return font_size


def _draw_text_plain(draw, text, x, y, text_font, text_colour):
    draw.text((x, y), text, font=text_font, fill=text_colour)


def _draw_text_with_shadow(draw, text, x, y, text_font, text_colour):
    """
    Draws text with inverted shadow border.
    :param draw: Drawing context
    :param text: Text to draw
    :param x: X coordinate of text
    :param y: y coordinate of text
    :param text_font: Text font
    :param text_colour: Text colour
    """
    size = text_font.getsize(text)[1]/100

    shadow_colour_narrow = (255-text_colour[0], 255-text_colour[1], 255-text_colour[2], 192)
    shadow_colour_middle = (255-text_colour[0], 255-text_colour[1], 255-text_colour[2], 128)
    shadow_colour_middle_2 = (255-text_colour[0], 255-text_colour[1], 255-text_colour[2], 64)
    shadow_colour_thick = (255-text_colour[0], 255-text_colour[1], 255-text_colour[2], 32)

    # Border
    _draw_text_border(draw, text, x, y, text_font, 4 * size, shadow_colour_thick)
    _draw_text_border(draw, text, x, y, text_font, 3 * size, shadow_colour_middle_2)
    _draw_text_border(draw, text, x, y, text_font, 2 * size, shadow_colour_middle)
    _draw_text_border(draw, text, x, y, text_font, 1 * size, shadow_colour_narrow)

    # Text
    draw.text((x, y), text, font=text_font, fill=text_colour)


def _draw_text_border(draw, text, x, y, text_font, border_size, border_colour):
    """
    Draws border for text.
    :param draw: Draw context
    :param text: Text to draw
    :param x: X coordinate of text
    :param y: y coordinate of text
    :param text_font: Text font
    :param border_size: Border size
    :param border_colour: Border colour
    :return:
    """
    # Border
    draw.text((x - border_size, y + border_size), text, font=text_font, fill=border_colour)
    draw.text((x + border_size, y + border_size), text, font=text_font, fill=border_colour)
    draw.text((x - border_size, y - border_size), text, font=text_font, fill=border_colour)
    draw.text((x + border_size, y - border_size), text, font=text_font, fill=border_colour)


def _render_quote_to_image(image, quote_text, quote_author, image_margin, image_fraction, text_font, text_colour):
    """
    Adds quote to image.
    :param image: Image
    :param quote_text: Quote text
    :param quote_author: Quote author
    :param image_margin: Image margin
    :param image_fraction: Fraction of image width to use for text
    :param text_font: Text font
    :param text_colour: Text colour
    """
    # Wrap quote
    wrap_width = len(quote_text)/4 if len(quote_text)/4 > image_margin else image_margin
    wrapped_quote = wrap(quote_text, width=wrap_width)

    # Calculate font sizes
    font_size = _calculate_font_size(text_font, max(wrapped_quote, key=len), image, image_fraction)
    font_normal = ImageFont.truetype(text_font, font_size)

    font_small_size = int(font_size / 2) if int(font_size / 2) > 20 else 20
    font_small = ImageFont.truetype(text_font, font_small_size)

    # Add quote to image
    draw = ImageDraw.Draw(image)
    img_w, img_h = image.size
    w, h = draw.textsize(wrapped_quote[0], font=font_normal)
    y = (img_h - h) / 2 - (font_normal.getsize(wrapped_quote[0])[1] * (len(wrapped_quote)) / 2)
    for line in wrapped_quote:
        w, h = draw.textsize(line, font=font_normal)
        x = (img_w - w) / 2
        _draw_text_plain(draw, line, x, y, font_normal, text_colour)
        y += font_normal.getsize(line)[1]

    # Add author to image
    w, h = draw.textsize(quote_author, font=font_small)
    x = (img_w - w) / 2
    draw.text((x, y), "", font=font_small, fill=text_colour)
    y += font_normal.getsize(quote_author)[1]
    _draw_text_plain(draw, quote_author, x, y, font_small, text_colour)


def _normalize_for_filename(text):
    """
    Normalizes text for using it in filename. Converts text to lowercase and
    replaces the following characters with underscore: whitespace, _, <, >, :, \, /, ", |, ?, *
    :param text: Text to normalize
    :return: Normalized text
    """
    return text.lower().replace(" ", "_").replace("/", "_").replace("<", "_").replace(">", "_").replace(":", "_")\
        .replace("\\", "_").replace("/", "_").replace("\"", "_").replace("|", "_").replace("?", "_").replace("*", "_")


def generate_image(output_folder, quote, author, text_font=font, text_colour=colour,
                   image_margin=img_margin, image_fraction=img_fraction):
    """
    Generates image with given quote.
    :param output_folder: Output folder
    :param quote: String
    :param author: String
    :param text_font: Text font
    :param text_colour: Text colour
    :param image_margin: Image margin
    :param image_fraction: Fraction of image width to use for text
    :return: 
    """
    quote_background = (255 - text_colour[0], 255 - text_colour[1], 255 - text_colour[1], 128)

    # get wallpaper image
    response = requests.get(url)
    img = Image.open(BytesIO(response.content)).convert('RGBA')

    # make a blank image for the text, initialized to transparent text color
    txt_img = Image.new('RGBA', img.size, quote_background)

    # render text to blank image
    _render_quote_to_image(txt_img, quote, author, image_margin, image_fraction, text_font, text_colour)

    # merge wallpaper with text
    out = Image.alpha_composite(img, txt_img)
    out.save(output_folder + _normalize_for_filename(author) + "_" + _normalize_for_filename(quote[:13]) + "_" +
             datetime.now().strftime("%Y%m%d-%H%M%S") + ".png")

