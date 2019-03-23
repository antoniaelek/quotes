import feedparser
import html


def get_quotes(user_id, user_name, sort=False):
    url = 'https://www.goodreads.com/quotes/list_rss/' + user_id + '-' + user_name
    quotes = []
    page = 1
    while True:
        try:
            new_quotes = _parse_rss_page(url + '?page=' + str(page))
            if len(new_quotes) == 0:
                break
            quotes.extend(new_quotes)
            page = page + 1
        except:
            break

    if sort:
        quotes.sort()

    return quotes


def _parse_rss_page(url):
    feed = feedparser.parse(url)
    page_quotes = []

    for entry in feed.entries:
        try:
            summary = entry.summary
            sep = summary.rfind('-- ')
            quote = html.unescape(summary[1:sep - 2])
            author = html.unescape(summary[sep + 3:])
            page_quotes.append((author, quote))
        except:
            continue

    return page_quotes
