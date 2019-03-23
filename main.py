from functions import generate_image
from goodreads.goodreads import get_quotes

out_folder = "data/out/antonia/"

if __name__ == '__main__':
    quotes = get_quotes('5705326', 'antonia', sort=True)

    # quote = quotes[4]
    # generate_image(out_folder, quote[1], quote[0])

    print(len(quotes))

    for quote in quotes[:]:
        if len(quote[1]) < 80:
            print(quote)
            generate_image(out_folder, quote[1], quote[0])
