import sqlalchemy.exc
from flask import Flask, jsonify, request
from web_scraper import Scraper
from sqlalchemy.orm import sessionmaker, relationship
import database_setup as db
import json

scraper = Scraper()


def check_db_length():
    Session = sessionmaker(bind=db.engine)
    session = Session()

    num_books = session.query(db.Book).count()
    print(f'You have {num_books} books already entered in the database... setting the new entry ID!')
    return num_books



def enable_cors(json):
    """Enables cross-origin resource sharing (CORS) to requests"""
    response = json
    response.headers.add('Access-Control-Allow-Origin', 'localhost')
    return response


# Flask app creation in debug mode
app = Flask(__name__)
app.config['DEBUG'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book-collection.db'
# db = SQLAlchemy(app)
#
#
# class Book(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String, unique=False, nullable=False)
#     # url = db.Column(db.String, unique=True, nullable=False)
#     # img_url = db.Column(db.String, unique=True, nullable=False)
#     # author = db.Column(db.String, unique=False, nullable=False)
#     # tags = db.Column(db.String, unique=False, nullable=False)
#     # pages = db.Column(db.String, unique=False, nullable=False)
#     # chapter = db.Column(db.String, unique=False, nullable=False)
#     # chapter_count = db.Column(db.String, unique=False, nullable=False)
#     # rating = db.Column(db.String, unique=False, nullable=False)
#     # total_rates = db.Column(db.String, unique=False, nullable=False)
#     # views = db.Column(db.String, unique=False, nullable=False)
#     # favorites = db.Column(db.String, unique=False, nullable=False)
#     # followers = db.Column(db.String, unique=False, nullable=False)
#     #
#     def __repr__(self):
#         return '<Book %r>' % self.title
#
#
# db.create_all()


# set base flask path routing
@app.route('/')
def api_base():
    return '<h1>Book Scraper</h1>' \
           '<p>A prototype web-scraping API for use with https://www.royalroad.com/</p>'


@app.route('/api/v1/books/resources/all', methods=['GET'])
def api_all():
    # Provide JSON for all the scraped books

    Session = sessionmaker(bind=db.engine)
    session = Session()

    books = session.query(db.Book.metadata.tables['books']).all()


    books = jsonify(books)
    return books


# set routing for title of book
@app.route("/api/v1/resources/books", methods=['GET'])
def api_book():
    book_id = check_db_length()
    """Returns JSON of the searched book"""

    if 'title' in request.args:
        scraper.scrape_title()
        Session = sessionmaker(bind=db.engine)
        session = Session()
        print(scraper.book_info[-1])
        entry = db.Book(id=book_id, **scraper.book_info[-1])

        session.add(entry)
        try:
            print(book_id)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            print('A duplicate has been detected, skipping!')
            session.rollback()
        else:
            book_id +=1
        print(book_id)
        session.close()

    elif 'top' in request.args:
        print('entered')
        scraper.scrape_top()

        for book in range(0, len(scraper.book_info)):
            Session = sessionmaker(bind=db.engine)
            session = Session()
            entry = db.Book(id=book_id, **scraper.book_info[book])
            session.add(entry)
            try:
                session.add(entry)
            except sqlalchemy.exc.IntegrityError:
                print('A duplicate has been detected, skipping!')
                session.rollback()
            else:
                session.add(entry)
            book_id += 1

            session.close()


    if not scraper.results:
        return "Error: No title field provided. Please specify a title."

    book_data = enable_cors(jsonify(scraper.results))
    scraper.results = []
    scraper.book_info = []
    # Book.query.all()
    return book_data


if __name__ == '__main__':
    app.run(debug=True)
