from bs4 import BeautifulSoup
import lxml
import requests
from flask import Flask, jsonify, request
import time

BASE_URL = 'https://www.royalroad.com/'
book_info = []
added_novels = []


# def speed_calc_decorator(function):
#     def wrapper_function():
#         # mark the start time of the function
#         start_time = time.time()
#         # run the function
#         function()
#         # print the function name as well as the current time subtracted from the start time
#         print(f'{function.__name__} run speed: {time.time() - start_time}')
#
#     return wrapper_function


def create_soup(book_link):
    """Creates Soup to be able to parse webpage"""
    url = book_link
    response = requests.get(url=url)
    webpage = response.text
    return BeautifulSoup(webpage, 'lxml')


def find_title(soup):
    """Finds book title"""
    return soup.find(property='name', ).get_text()


def find_author(soup):
    """Finds the author using selectors"""

    # worked but ran into issues when col did not exist on the page (was a div tag instead)
    # return soup.select_one('.col > h4 > :last-child > a').get_text()
    author = soup.find(property='author').get_text().strip('\n')
    head, sep, tail = author.partition('\n\n')
    return tail


def find_tags(soup):
    """Finds all tags and returns them as a list"""

    found_tags = soup.findAll(class_='tags')
    tags = [(tag.get_text().strip('\n').splitlines()) for tag in found_tags]
    [tags] = tags
    return tags


def find_chapters(soup):
    """Finds all chapters and accompanying links"""

    chapter_list = []
    chapters = soup.findAll(class_='chapter-row')
    for chapter in chapters:
        # Separates the chapter name from the 'junk' that is returned
        head, sep, tail = chapter.get_text().strip().partition('\n')
        link = chapter.find(href=True)
        appended_link = f'{BASE_URL}{link["href"]}'
        chapter_list.append([head, appended_link])
    return chapter_list


def find_stats(soup):
    """Finds general stats related to the book"""

    # Finds the rating and total rates of the book
    rating = soup.find(property='ratingValue').attrs['content']
    rate_count = soup.find(property='ratingCount').attrs['content']

    stats = soup.select('.stats-content > :last-child > ul > :nth-child(even)')
    views = stats[0].get_text()
    followers = stats[2].get_text()
    favorites = stats[3].get_text()
    pages = stats[5].get_text()

    return [rating, rate_count, views, followers, favorites, pages]


def find_image_url(soup):
    """Finds the link to the book's cover art"""
    link = soup.find(property='image').attrs['src']
    return link


def create_book_info(book_link):
    """Creates dictionary with all relevant book information"""

    already_present = check_if_added(book_link)
    if already_present:
        return
    soup = create_soup(book_link)
    title = find_title(soup)
    already_present = check_if_added(title)
    if already_present:
        return
    author = find_author(soup)
    tags = find_tags(soup)
    chapter_list = find_chapters(soup)
    list_of_stats = find_stats(soup)
    img_url = find_image_url(soup)

    book_info.append({
        'title': title,
        'url': book_link,
        'img_url': img_url,
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
    })

    # Append book url to list of already seen book urls
    added_novels.append(book_link)


def return_single_book():
    """Returns a single book from book_info if book_info has more than one book within it. Doesn't need to return a
        value because it appends to a list that's global"""

    # Create an empty results tag that will be unmodified if a book is not found
    results = []

    # Grab the searched title from the parameters and format it, so it will match a found book if one exists
    title = str(request.args['title']).replace('%20', ' ').lower()

    # Loop through the data and match results that fit the requested title.
    # Titles should be fairly unique, but other fields might return many results
    for book in book_info:
        if book['title'].lower() == title:
            results.append(book)
            return results

    # No book found and return empty results
    else:
        return results


def search_for_book():
    """Searches https://www.royalroad.com/ for entered book"""

    url = f'https://www.royalroad.com/fictions/search?title={request.args["title"]}'

    # Pulls the link for the book's page
    soup = create_soup(url)
    book_link = soup.find(class_='fiction-title')
    try:
        book_link = book_link.find(href=True)
    except AttributeError:
        return []
    book_link = f'https://www.royalroad.com{book_link["href"]}'

    create_book_info(book_link)
    return return_single_book()


def enable_cors(json):
    """Enables cross-origin resource sharing (CORS) to requests"""
    response = json
    response.headers.add('Access-Control-Allow-Origin', 'localhost')
    return response


def check_if_added(url):
    """Checks if a book has already been added to the JSON file"""
    if url in added_novels:
        return True


def whole_page_books(url):
    """Searches the whole pages for books and adds them to the JSON file"""
    print(f'Adding books from {url}. Hold on to your butts...')
    i = 1
    soup = create_soup(url)
    books = soup.find_all(class_='fiction-title')
    for book in books:
        book_link = f'https://www.royalroad.com{book.find(href=True)["href"]}'
        create_book_info(book_link)
        if i % 5 == 0:
            print(f'Finished book {i}/{len(books)}...')
        i = i + 1


def top_books_on_site():
    """Pulls for the top books on the site"""
    print('entered function')
    print(request.args)
    top_rated_and_more_links = {'best%20rated': 'https://www.royalroad.com/fictions/best-rated',
                                'ongoing': 'https://www.royalroad.com/fictions/active-popular',
                                'weekly%20popular': 'https://www.royalroad.com/fictions/weekly-popular',
                                'rising%20stars': 'https://www.royalroad.com/fictions/rising-stars',
                                'top%20completed': 'https://www.royalroad.com/fictions/complete'}

    # Checks to see if the parameter has been included
    if 'best rated' in request.args:
        print('Beginning best rated novels...')
        whole_page_books(top_rated_and_more_links['best%20rated'])
        print('Completed best rated novels\n')
    if 'ongoing' in request.args:
        print('Beginning top current ongoing novels...')
        whole_page_books(top_rated_and_more_links['ongoing'])
        print('Completed top ongoing novels.\n')
    if 'weekly popular' in request.args:
        print('Beginning top books of the week...')
        whole_page_books(top_rated_and_more_links['weekly%20popular'])
        print('Completed top books of the week.\n')
    if 'rising stars' in request.args:
        print('Beginning top rising stars...')
        whole_page_books(top_rated_and_more_links['rising%20stars'])
        print('Completed top rising stars.\n')
    if 'top completed' in request.args:
        print('Beginning top completed novels...')
        whole_page_books(top_rated_and_more_links['top%20completed'])
        print('Finished top completed novels\n')

    # At the end, will let user know of the duplicate URLs
    if added_novels:
        print('The following urls had duplicates and were not added twice:')
        for book in added_novels:
            print(book)


# Flask app creation in debug mode
app = Flask(__name__)
app.config['DEBUG'] = True


# set base flask path routing
@app.route('/')
def api_base():
    return '<h1>Book Scraper</h1>' \
           '<p>A prototype web-scraping API for use with https://www.royalroad.com/</p>'


@app.route('/api/v1/books/all')
def api_all():
    # Provide JSON for all the scraped books
    book_data = enable_cors(jsonify(book_info))
    return book_data


# set routing for title of book
@app.route("/api/v1/resources/books", methods=['GET'])
def api_book():
    """Returns JSON of the searched book"""

    # Check if a title was provided as part of the URL.
    # If title is a parameter, see if it's located within the saved book info list
    # If not, search for the book online and add it to the book info
    # If it still cannot be found, let the user know.
    if 'title' in request.args:
        results = return_single_book()
        if not results:
            results = search_for_book()
            if not results:
                return 'Error: Book not found'

    elif 'top' in request.args:
        print('top received')
        top_books_on_site()
        results = book_info

    else:
        return "Error: No title field provided. Please specify a title."

    book_data = enable_cors(jsonify(results))
    return book_data


if __name__ == '__main__':
    app.run()
