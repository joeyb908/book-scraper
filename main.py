from bs4 import BeautifulSoup
import lxml
import requests
import pprint
from flask import Flask, jsonify, request

pp = pprint.PrettyPrinter(indent=4, compact=True)
BASE_URL = 'https://www.royalroad.com/'


def create_soup():
    URL = 'https://www.royalroad.com/fiction/21220/mother-of-learning'
    response = requests.get(url=URL)
    webpage = response.text
    return BeautifulSoup(webpage, 'lxml')


def find_title(soup):
    # finds book title
    return soup.find(property='name', ).get_text()


def find_author(soup):
    # find author using selectors
    # a list gets returned even though it's only a single index
    return soup.select_one('.col > h4 > :last-child > a').get_text()


def find_tags(soup):
    # finds all the tags
    found_tags = soup.findAll(class_='tags')
    # creates list of tags
    tags = [(tag.get_text().strip('\n').splitlines()) for tag in found_tags]
    # 'unpacks list of tags' into a single dimension list as returned
    # value from the comprehension was a nested empty list
    [tags] = tags
    return tags


def find_chapters(soup):
    # finds all chapters and accompanying links
    chapter_list = []
    chapters = soup.findAll(class_='chapter-row')
    for chapter in chapters:
        # pulls only the chapter name into head value
        head, sep, tail = chapter.get_text().strip().partition('\n')

        # pulls the chapter link
        link = chapter.find(href=True)
        appended_link = f'{BASE_URL}{link["href"]}'
        chapter_list.append([head, appended_link])

        published_date = chapter.find('time').get_text()
    return chapter_list


def find_stats(soup):
    # finds the rating and total rates of the book
    rating = soup.find(property='ratingValue').attrs['content']
    rate_count = soup.find(property='ratingCount').attrs['content']

    # find total views, followers, favorites, and pages
    stats = soup.select('.stats-content > :last-child > ul > :nth-child(even)')
    views = stats[0].get_text()
    followers = stats[2].get_text()
    favorites = stats[3].get_text()
    pages = stats[5].get_text()
    list_of_stats = [rating, rate_count, views, followers, favorites, pages]
    return list_of_stats


def create_book_info():
    soup = create_soup()
    title = find_title(soup)
    author = find_author(soup)
    tags = find_tags(soup)
    chapter_list = find_chapters(soup)
    list_of_stats = find_stats(soup)
    book_info = {
        'title': title,
        'author': author,
        'tags': tags,
        'pages': list_of_stats[-1],
        'chapter': chapter_list,
        'chapter_count': len(chapter_list),
        'rating': list_of_stats[0],
        'total_rates': list_of_stats[1],
        'views': list_of_stats[2],
        'favorites': list_of_stats[4],
        'followers': list_of_stats[3],
    }
    return book_info

book_info = create_book_info()

title = book_info['title'].replace(' ', '%').lower()
print(title)
# pp.pprint(book_info)

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def api_base():
    return '<h1>Book Scraper</h1>' \
           '<p>A prototype web-scraping API for use with https://www.royalroad.com/</p>'


@app.route("/api/v1/books/<title>")
def api_book(title):
    return jsonify(book_info)

#
if __name__ == '__main__':
    app.run()
