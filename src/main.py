from functions import generate_image

out_folder = "data/out/"

if __name__ == '__main__':
    quotes = [
        ("The easiest thing in the world is to convince yourself that you're right. As one grows old, it is easier still.", "Robert Ludlum"),
        ("We are all in the gutter, but some of us are looking at the stars.","Oscar Wilde"),
        ("Failure is an option here. If things are not failing, you are not innovating enough.","Elon Musk")]

    for quote in quotes:
        generate_image(out_folder, quote)
