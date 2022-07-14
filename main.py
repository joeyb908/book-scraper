import sqlalchemy.exc
from flask import Flask, jsonify, request
from web_scraper import Scraper
from sqlalchemy.orm import sessionmaker
import database_setup as db

scraper = Scraper()


def check_db_length():
    """Checks the length of the database and returns the... length (duh)"""
    Session = sessionmaker(bind=db.engine)
    session = Session()

    num_books = session.query(db.Book).count()

    session.close()
    print(f'You have {num_books} books already entered in the database... setting the new entry ID!')
    return num_books


def enable_cors(json):
    """Enables cross-origin resource sharing (CORS) to requests"""
    response = json
    response.headers.add('Access-Control-Allow-Origin', 'localhost')
    return response


def create_session():
    """Creates connection to the database"""
    Session = sessionmaker(bind=db.engine)
    return Session()


# Flask app creation in debug mode
app = Flask(__name__)
app.config['DEBUG'] = True


# set base flask path routing
@app.route('/')
def api_base():
    return '<h1>Book Scraper</h1>' \
           '<p>A prototype web-scraping API for use with https://www.royalroad.com/</p>'


@app.route('/api/v1/resources/all', methods=['GET'])
def api_all():
    # Provide JSON for all the scraped books
    session = create_session()

    # Queries the database to return a JSON
    books = session.query(db.Book).all()
    for book in books:
        scraper.book_info.append(book.serialize())

    books = jsonify(scraper.book_info)
    return books


# set routing for title of book
@app.route("/api/v1/resources/books", methods=['GET'])
def api_book():
    book_id = check_db_length()
    """Returns JSON of the searched book"""

    if 'title' in request.args:
        scraper.scrape_title()
        session = create_session()

        # Grab the latest entry
        try:
            entry = db.Book(id=book_id, **scraper.book_info[-1])

        # If duplicate, stop adding to the database
        except TypeError:
            print('Pulling from the database due to duplicate!')
            session.close()

        # If successful, add to database
        else:
            session.add(entry)

            # Try to commit
            try:
                session.commit()

            # If already found, rollback any changes
            except sqlalchemy.exc.IntegrityError:
                session.rollback()

            # Once committed, add one to the book ID
            else:
                book_id += 1

            # Always close the database connection
            finally:
                session.close()

    elif 'top' in request.args:
        print('entered')
        scraper.scrape_top()

        for book in range(0, len(scraper.book_info)):
            session = create_session()
            try:
                entry = db.Book(id=book_id, **scraper.book_info[book])

            # If duplicate, stop adding to the database
            except TypeError:
                print('Pulling from the database due to duplicate!')
                session.close()

            # If successful, add to database
            else:
                session.add(entry)
                try:
                    session.commit()
                except sqlalchemy.exc.IntegrityError:
                    # Entry already found
                    session.rollback()
                else:
                    # If successful, adds one to the book id
                    book_id += 1
                finally:
                    session.close()

    if not scraper.results:
        return "Error: No title field provided. Please specify a title."

    book_data = enable_cors(jsonify(scraper.book_info))
    scraper.results = []
    scraper.book_info = []
    return book_data


if __name__ == '__main__':
    app.run(debug=True)
