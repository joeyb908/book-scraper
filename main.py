from bs4 import BeautifulSoup
import lxml
import requests
import pprint
from flask import Flask, jsonify, request



pp = pprint.PrettyPrinter(indent=4, compact=True)
BASE_URL = 'https://www.royalroad.com/'
book_info = []
book_info_format = {
        'book': {
            'title': None,
            'information' : {
                'author': None,
                'tags': None,
                'pages': None,
                'chapter': None,
                'chapter_count': None,
                'rating': None,
                'total_rates': None,
                'views': None,
                'favorites': None,
                'followers': None,
            }
        }
    }
id = 0


def create_soup(book_link):
    URL = book_link
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


def create_book_info(book_info, book_link):
    global id
    soup = create_soup(book_link)
    title = find_title(soup)
    author = find_author(soup)
    tags = find_tags(soup)
    chapter_list = find_chapters(soup)
    list_of_stats = find_stats(soup)
    book_info.append({
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
    )
    id = id + 1
    return book_info


# create the book info
book_info = create_book_info(book_info, 'https://www.royalroad.com/fiction/36735/the-perfect-run')
book_info = create_book_info(book_info, 'https://www.royalroad.com/fiction/21220/mother-of-learning')
book_info = create_book_info(book_info, 'https://www.royalroad.com/fiction/39408/beware-of-chicken')
# pp.pprint(book_info)


# title = book_info[0]['title'].replace(' ', '%').lower()
# print(title)
# # pp.pprint(book_info)


# flask app creation in debug mode
app = Flask(__name__)
app.config['DEBUG'] = True


# set base flask path routing
@app.route('/')
def api_base():
    return '<h1>Book Scraper</h1>' \
           '<p>A prototype web-scraping API for use with https://www.royalroad.com/</p>'


@app.route('/api/v1/books/all')
def api_all():
    return jsonify(book_info)


# set routing for title of book
@app.route("/api/v1/books", methods=['GET'])
def api_book():
    # Check if a title was provided as part of the URL.
    # If the title is provided, assign it to a variable.
    # If no title is provided, display an error in the browser.
    if 'title' in request.args:
        title = str(request.args['title']).replace(' ', '_')
    else:
        return "Error: No id field provided. Please specify a title."

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested title.
    # Titles should be fairly unique, but other fields might return many results
    for book in book_info:
        if book['title'].replace(' ', '_').lower() == title:
            results.append(book)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)


#
if __name__ == '__main__':
    app.run()
