from bs4 import BeautifulSoup
import lxml
import requests
import pprint
from flask import Flask, jsonify, request

pp = pprint.PrettyPrinter(indent=4, compact=True)
BASE_URL = 'https://www.royalroad.com/'
book_info = []


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
    return soup.select_one('.col > h4 > :last-child > a').get_text()


def find_tags(soup):
    """Finds all tags and returns them as a list"""

    # Initial search for raw tag html
    found_tags = soup.findAll(class_='tags')

    # Formats tags into a list
    tags = [(tag.get_text().strip('\n').splitlines()) for tag in found_tags]

    # Unpacks list of tags into a single dimension list because the returned value from the list comprehension
    # was a nested empty list; example: [['Adventure', 'Thriller']]
    [tags] = tags
    return tags


def find_chapters(soup):
    """Finds all chapters and accompanying links"""

    chapter_list = []

    # Locate the location of the webpage where chapters are housed
    chapters = soup.findAll(class_='chapter-row')
    for chapter in chapters:
        # Separates the chapter name from the 'junk' that is returned
        head, sep, tail = chapter.get_text().strip().partition('\n')

        # Pulls the chapter link
        link = chapter.find(href=True)
        appended_link = f'{BASE_URL}{link["href"]}'

        # Appends each chapter and accompanying link to chapter list.
        chapter_list.append([head, appended_link])
    return chapter_list


def find_stats(soup):
    """Finds general stats related to the book"""

    # Finds the rating and total rates of the book
    rating = soup.find(property='ratingValue').attrs['content']
    rate_count = soup.find(property='ratingCount').attrs['content']

    # Finds total views, followers, favorites, and pages
    stats = soup.select('.stats-content > :last-child > ul > :nth-child(even)')
    views = stats[0].get_text()
    followers = stats[2].get_text()
    favorites = stats[3].get_text()
    pages = stats[5].get_text()

    # Return the whole list of stats to be processed inside book_info
    list_of_stats = [rating, rate_count, views, followers, favorites, pages]
    return list_of_stats


def create_book_info(book_link):
    """Creates dictionary with all relevant book information"""

    # Creates Soup with provided book link
    soup = create_soup(book_link)

    # Finds the title, author, tags, chapter list, views, followers, favorites, and total pages
    title = find_title(soup)
    author = find_author(soup)
    tags = find_tags(soup)
    chapter_list = find_chapters(soup)
    list_of_stats = find_stats(soup)

    # Appends stats to the book info list
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
    # return book_info


def return_single_book():
    """Returns a single book from book_info if book_info has more than one book within it"""

    # Create an empty results tag that will be unmodified if a book is not found
    results = []

    # Grab the searched title from the parameters and format it so it will match a found book if one exists
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

    # Searches royalroad for the book
    URL = f'https://www.royalroad.com/fictions/search?title={request.args["title"]}'

    # Create the Soup and pulls the link for the book's page
    soup = create_soup(URL)
    book_link = soup.find(class_='fiction-title')
    book_link = book_link.find(href=True)
    book_link = f'https://www.royalroad.com{book_link["href"]}'

    # Pulls the book's information from its webpage and returns the results
    create_book_info(book_link)
    results = return_single_book()
    return results


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
    # Provide JSON for all of the scraped books
    return jsonify(book_info)


# set routing for title of book
@app.route("/api/v1/books", methods=['GET'])
def api_book():
    # Check if a title was provided as part of the URL.
    # If title is a parameter, see if it's located within the saved book info list
    # If not, search for the book online and add it to the book info
    # If it still cannot be found, let the user know.
    if 'title' in request.args:
        results = return_single_book()
        if not results:
            results = search_for_book()
            if not results:
                return "Error: Book could not be found. Please try another search."

    else:
        return "Error: No title field provided. Please specify a title."

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)


if __name__ == '__main__':
    app.run()
