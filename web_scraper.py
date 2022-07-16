from bs4 import BeautifulSoup
import lxml
import requests
from flask import request
import database_setup as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import table, column, select


def check_if_added(url):
    db_item_location = None
    """Checks if a book has already been added to the JSON file"""
    Session = sessionmaker(bind=db.engine)
    session = Session()

    # Queries the URL column in the database to see if the URL exists
    query = select([db.Book.url]).where(db.Book.url == url)
    result = session.execute(query).fetchall()[0][0]
    session.close()

    if result:
        return True


def grab_duplicate_from_db(url):
    Session = sessionmaker(bind=db.engine)
    session = Session()

    # Grab URL in database that already exists
    query = select([db.Book]).where(db.Book.url == url)
    result = session.execute(query).fetchall()[0][0]
    session.close()
    return result.serialize()


class Scraper:

    def __init__(self):
        self.BASE_URL = 'https://www.royalroad.com/'
        self.book_info = []
        self.added_novels = []
        self.duplicate_novels = []
        self.results = []
        self.soup = None

    def create_soup(self, book_link):
        """Creates Soup to be able to parse webpage"""
        url = book_link
        response = requests.get(url=url)
        webpage = response.text
        self.soup = BeautifulSoup(webpage, 'lxml')

    def find_title(self):
        """Finds book title"""
        return self.soup.find(property='name', ).get_text()

    def find_author(self):
        """Finds the author using selectors"""

        # Worked but ran into issues when col did not exist on the page (was a div tag instead)
        # return soup.select_one('.col > h4 > :last-child > a').get_text()

        # Finds the author, then separates everything from the right-half of the first '\n' to the tail
        author = self.soup.find(property='author').get_text().strip('\n')
        head, sep, tail = author.partition('\n\n')
        return tail

    def find_tags(self):
        """Finds all tags and returns them as a list"""

        found_tags = self.soup.findAll(class_='tags')
        tags = [(tag.get_text().strip('\n').splitlines()) for tag in found_tags]

        # Unpacks the returns tags because they're in a nested empty list
        # i.e, [[fiction, fantasy]] instead of [fiction, fantasy]
        [tags] = tags
        return tags

    def find_chapters(self):
        """Finds all chapters and accompanying links"""

        chapter_list = []
        chapters = self.soup.findAll(class_='chapter-row')
        for chapter in chapters:
            # Separates the chapter name from the 'junk' that is returned
            head, sep, tail = chapter.get_text().strip().partition('\n')
            link = chapter.find(href=True)
            appended_link = f'https://www.royralroad.com{link["href"]}'
            chapter_list.append([str(head), str(appended_link)])
        return chapter_list

    def find_stats(self):
        """Finds general stats related to the book"""

        # Finds the rating and total rates of the book
        rating = float(self.soup.find(property='ratingValue').attrs['content'])
        rate_count = int(self.soup.find(property='ratingCount').attrs['content'].replace(",", "_"))

        stats = self.soup.select('.stats-content > :last-child > ul > :nth-child(even)')
        views = int(stats[0].get_text().replace(",", "_"))
        followers = int(stats[2].get_text().replace(',', "_"))
        favorites = int(stats[3].get_text().replace(",", "_"))
        pages = int(stats[5].get_text().replace(",", "_"))

        return [rating, rate_count, views, followers, favorites, pages]

    def find_image_url(self):
        """Finds the link to the book's cover art"""
        link = self.soup.find(property='image').attrs['src']
        return link

    def create_book_info(self, book_link):
        """Creates dictionary with all relevant book information"""

        # Checks if the book is already in the database
        try:
            check_if_added(book_link)

        # If it's not, added it
        except IndexError:
            self.create_soup(book_link)
            title = self.find_title()
            author = self.find_author()
            tags = self.find_tags()
            chapter_list = self.find_chapters()
            list_of_stats = self.find_stats()
            img_url = self.find_image_url()

            self.book_info.append({
                'title': str(title),
                'url': str(book_link),
                'img_url': str(img_url),
                'author': str(author),
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
            self.added_novels.append(book_link)
            print('book added')

        # If book is in the database, append it the book_info
        else:
            self.book_info.append(grab_duplicate_from_db(book_link))
            return

    def return_single_book(self):
        print('entered')
        """Returns a single book from book_info if book_info has more than one book within it. Doesn't need to return a
            value because it appends to a list that's global"""

        # Grab the searched title from the parameters and format it, so it will match a found book if one exists
        title = str(request.args['title']).replace('%20', ' ').lower()

        # Loop through the data and match results that fit the requested title.
        # Titles should be fairly unique, but other fields might return many results
        for book in self.book_info:
            if book['title'].lower() == title:
                print(f'book {title} appended')
                self.results.append(book)
                return self.results

        else:
            return self.results

    def search_for_book(self):
        """Searches https://www.royalroad.com/ for entered book"""

        url = f'https://www.royalroad.com/fictions/search?title={request.args["title"]}'

        # Pulls the link for the book's page
        self.create_soup(url)
        book_link = self.soup.find(class_='fiction-title')
        try:
            book_link = book_link.find(href=True)
        except AttributeError:
            return []
        book_link = f'https://www.royalroad.com{book_link["href"]}'

        self.create_book_info(book_link)
        return self.return_single_book()

    def top_books_on_site(self):
        print('entered')
        """Pulls for the top books on the site"""
        top_rated_and_more_links = {'best%20rated': 'https://www.royalroad.com/fictions/best-rated',
                                    'ongoing': 'https://www.royalroad.com/fictions/active-popular',
                                    'weekly%20popular': 'https://www.royalroad.com/fictions/weekly-popular',
                                    'rising%20stars': 'https://www.royalroad.com/fictions/rising-stars',
                                    'top%20completed': 'https://www.royalroad.com/fictions/complete'}

        # Checks to see if the parameter has been included
        if 'best rated' in request.args:
            print('Beginning best rated novels...')
            self.whole_page_books(top_rated_and_more_links['best%20rated'])
            print('Completed best rated novels\n')
        if 'ongoing' in request.args:
            print('yes')
            print('Beginning top current ongoing novels...')
            self.whole_page_books(top_rated_and_more_links['ongoing'])
            print('Completed top ongoing novels.\n')
        if 'weekly popular' in request.args:
            print('Beginning top books of the week...')
            self.whole_page_books(top_rated_and_more_links['weekly%20popular'])
            print('Completed top books of the week.\n')
        if 'rising stars' in request.args:
            print('Beginning top rising stars...')
            self.whole_page_books(top_rated_and_more_links['rising%20stars'])
            print('Completed top rising stars.\n')
        if 'top completed' in request.args:
            print('Beginning top completed novels...')
            self.whole_page_books(top_rated_and_more_links['top%20completed'])
            print('Finished top completed novels\n')

        # At the end, will let user know of the duplicate URLs
        if self.duplicate_novels:
            print('The following urls had duplicates and were not added twice:')
            for book in self.duplicate_novels:
                print(book)

    def whole_page_books(self, url):
        """Searches the whole pages for books and adds them to the JSON file"""
        print(f'Adding books from {url}. Hold on to your butts...')
        i = 1
        self.create_soup(url)
        books = self.soup.find_all(class_='fiction-title')
        for book in books:
            book_link = f'https://www.royalroad.com{book.find(href=True)["href"]}'
            self.create_book_info(book_link)
            if i % 5 == 0:
                print(f'Finished book {i}/{len(books)}...')
            i = i + 1

    def scrape_title(self):
        self.results = []
        self.return_single_book()
        if not self.results:
            self.results = self.search_for_book()
            if not self.results:
                return False

    def scrape_top(self):
        self.results = []
        self.top_books_on_site()


