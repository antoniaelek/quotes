from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from textwrap import wrap
import requests
from io import BytesIO
from datetime import datetime

url = "https://source.unsplash.com/featured/1600x900/?landscape"
fonts_folder = "data/fonts/"
out_folder = "data/out/"


def calculate_font_size(path_to_font, text, image, image_fraction):
    """

    :param path_to_font: path to font file to use
    :param text: text to calculate width for
    :param image: image to fit
    :param image_fraction: fraction of image width to fit text to
    :return: font size that fits image
    """
    size = 1
    font = ImageFont.truetype(path_to_font, 28)

    # find font size that fits
    while font.getsize(text)[0] < image_fraction * image.size[0]:
        # iterate until the text size is just larger than the criteria
        size += 1
        font = ImageFont.truetype(path_to_font, size)

    # de-increment to be sure it is less than criteria
    size -= 1
    return size


def draw_text_with_border(draw, text, x, y, text_font, text_colour):
    size = text_font.getsize(text)[1]/100

    shadow_colour_narrow = (255-text_colour[0], 255-text_colour[1], 255-text_colour[2], 192)
    shadow_colour_middle = (255-text_colour[0], 255-text_colour[1], 255-text_colour[2], 128)
    shadow_colour_middle_2 = (255-text_colour[0], 255-text_colour[1], 255-text_colour[2], 64)
    shadow_colour_thick = (255-text_colour[0], 255-text_colour[1], 255-text_colour[2], 32)

    # Border
    draw_text_border(draw, text, x, y, text_font, 4*size, shadow_colour_thick)
    draw_text_border(draw, text, x, y, text_font, 3*size, shadow_colour_middle_2)
    draw_text_border(draw, text, x, y, text_font, 2*size, shadow_colour_middle)
    draw_text_border(draw, text, x, y, text_font, 1*size, shadow_colour_narrow)

    # Text
    draw.text((x, y), text, font=text_font, fill=text_colour)


def draw_text_border(draw, text, x, y, text_font, border_size, shadow_colour):
    # Border
    draw.text((x - border_size, y + border_size), text, font=text_font, fill=shadow_colour)
    draw.text((x + border_size, y + border_size), text, font=text_font, fill=shadow_colour)
    draw.text((x - border_size, y - border_size), text, font=text_font, fill=shadow_colour)
    draw.text((x + border_size, y - border_size), text, font=text_font, fill=shadow_colour)


def render_quote_to_image(image, quote_text, quote_author, image_margin, image_fraction, text_font, text_colour):
    # Wrap quote
    wrapped_quote = wrap(quote_text, width=image_margin)

    # Calculate font sizes
    font_size = calculate_font_size(text_font, wrapped_quote[0], image, image_fraction)
    font_normal = ImageFont.truetype(text_font, font_size)
    font_small = ImageFont.truetype(text_font, int(font_size / 2))

    # Add quote to image
    draw = ImageDraw.Draw(image)
    img_w, img_h = image.size
    w, h = draw.textsize(wrapped_quote[0], font=font_normal)
    y = (img_h - h) / 2 - (font_normal.getsize(wrapped_quote[0])[1] * (len(wrapped_quote)) / 2)
    for line in wrapped_quote:
        w, h = draw.textsize(line, font=font_normal)
        x = (img_w - w) / 2
        draw_text_with_border(draw, line, x, y, font_normal, text_colour)
        y += font_normal.getsize(line)[1]

    # Add author to image
    w, h = draw.textsize(quote_author, font=font_small)
    x = (img_w - w) / 2
    draw_text_with_border(draw, "", x, y, font_small, text_colour)
    y += font_normal.getsize(quote_author)[1]
    draw_text_with_border(draw, quote_author, x, y, font_small, text_colour)


def normalize_for_filename(text):
    return text.lower().replace(" ", "_").replace("/", "_").replace("<", "_").replace(">", "_").replace(":", "_")\
        .replace("\\", "_").replace("/", "_").replace("\"", "_").replace("|", "_").replace("?", "_").replace("*", "_")


def generate_images(quotes_list, quotes_font, quotes_colour, image_margin, image_fraction):
    quote_background = (255 - quotes_colour[0], 255 - quotes_colour[1], 255 - quotes_colour[1], 64)
    for q in quotes_list:
        # get quote and author
        quote, author = q

        # get wallpaper image
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert('RGBA')

        # make a blank image for the text, initialized to transparent text color
        txt_img = Image.new('RGBA', img.size, quote_background)

        # render text to blank image
        render_quote_to_image(txt_img, quote, author, image_margin, image_fraction, quotes_font, quotes_colour)

        # merge wallpaper with text
        out = Image.alpha_composite(img, txt_img)
        out.save(out_folder + normalize_for_filename(author) + "_" + normalize_for_filename(quote[:15]) + "_" +
                 datetime.now().strftime("%Y%m%d-%H%M%S") + ".png")


if __name__ == '__main__':
    font = fonts_folder + "Roboto-Regular.ttf"
    quote_colour = (255, 255, 255, 255)
    img_margin = 50
    img_fraction = 0.8

    quotes = [(
              "The easiest thing in the world is to convince yourself that you're right. As one grows old, it is easier still.",
              "Robert Ludlum")]
    generate_images(quotes, font, quote_colour,  img_margin, img_fraction)


