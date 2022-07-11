from flask import Flask, jsonify, request
from web_scraper import Scraper

scraper = Scraper()


def enable_cors(json):
    """Enables cross-origin resource sharing (CORS) to requests"""
    response = json
    response.headers.add('Access-Control-Allow-Origin', 'localhost')
    return response


# Flask app creation in debug mode
app = Flask(__name__)
app.config['DEBUG'] = True


# set base flask path routing
@app.route('/')
def api_base():
    return '<h1>Book Scraper</h1>' \
           '<p>A prototype web-scraping API for use with https://www.royalroad.com/</p>'


@app.route('/api/v1/books/resources/all')
def api_all():
    # Provide JSON for all the scraped books

    book_data = enable_cors(jsonify(scraper.book_info))
    # book_data = enable_cors(jsonify(book_info))
    return book_data


# set routing for title of book
@app.route("/api/v1/resources/books", methods=['GET'])
def api_book():
    """Returns JSON of the searched book"""

    if 'title' in request.args:
        scraper.scrape_title()

    elif 'top' in request.args:
        print('entered')
        scraper.scrape_top()

    if not scraper.results:
        return "Error: No title field provided. Please specify a title."

    book_data = enable_cors(jsonify(scraper.results))
    return book_data


if __name__ == '__main__':
    app.run()
