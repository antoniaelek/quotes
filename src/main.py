from functions import generate_image
from goodreads import get_quotes

out_folder = "data/out/"

if __name__ == '__main__':
    quotes = get_quotes('64367923', 'anamaria-elek', sort=True)

    quote = quotes[4]
    generate_image(out_folder, quote[1], quote[0])

    # for quote in quotes:
    #     print(quote)
    #     generate_image(out_folder, quote[1], quote[0])
