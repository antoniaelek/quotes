import feedparser
import html


def get_quotes(user_id, user_name, sort=False):
    feed = feedparser.parse('https://www.goodreads.com/quotes/list_rss/' + user_id + '-' + user_name)

    quotes = []

    for entry in feed.entries:
        summary = entry.summary
        sep = summary.rfind('-- ')
        quote = html.unescape(summary[1:sep-2])
        author = html.unescape(summary[sep+3:])
        quotes.append((author, quote))

    if sort:
        quotes.sort()

    return quotes
