from bs4 import BeautifulSoup
import lxml
import requests
from flask import Flask, jsonify, request
import time


class Scraper:

    def __init__(self):
        self.BASE_URL = 'https://www.royalroad.com/'
        self.book_info = []
        self.added_novels = []
        self.duplicate_novels = []
        self.results = []
        self.soup = None

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

        # worked but ran into issues when col did not exist on the page (was a div tag instead)
        # return soup.select_one('.col > h4 > :last-child > a').get_text()
        author = self.soup.find(property='author').get_text().strip('\n')
        head, sep, tail = author.partition('\n\n')
        return tail

    def find_tags(self):
        """Finds all tags and returns them as a list"""

        found_tags = self.soup.findAll(class_='tags')
        tags = [(tag.get_text().strip('\n').splitlines()) for tag in found_tags]
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
            chapter_list.append([head, appended_link])
        return chapter_list

    def find_stats(self):
        """Finds general stats related to the book"""

        # Finds the rating and total rates of the book
        rating = self.soup.find(property='ratingValue').attrs['content']
        rate_count = self.soup.find(property='ratingCount').attrs['content']

        stats = self.soup.select('.stats-content > :last-child > ul > :nth-child(even)')
        views = stats[0].get_text()
        followers = stats[2].get_text()
        favorites = stats[3].get_text()
        pages = stats[5].get_text()

        return [rating, rate_count, views, followers, favorites, pages]

    def find_image_url(self):
        """Finds the link to the book's cover art"""
        link = self.soup.find(property='image').attrs['src']
        return link

    def create_book_info(self, book_link):
        """Creates dictionary with all relevant book information"""

        already_present = self.check_if_added(book_link)
        if already_present:
            self.duplicate_novels.append(book_link)
            return
        else:
            self.create_soup(book_link)
            title = self.find_title()
            author = self.find_author()
            tags = self.find_tags()
            chapter_list = self.find_chapters()
            list_of_stats = self.find_stats()
            img_url = self.find_image_url()

            self.book_info.append({
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
            self.added_novels.append(book_link)
            print('book added')

    def return_single_book(self):
        """Returns a single book from book_info if book_info has more than one book within it. Doesn't need to return a
            value because it appends to a list that's global"""

        # Grab the searched title from the parameters and format it, so it will match a found book if one exists
        title = str(request.args['title']).replace('%20', ' ').lower()

        # Loop through the data and match results that fit the requested title.
        # Titles should be fairly unique, but other fields might return many results
        for book in self.book_info:
            if book['title'].lower() == title:
                self.results.append(book)

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
        self.return_single_book()

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

    def check_if_added(self, url):
        """Checks if a book has already been added to the JSON file"""
        if url in self.added_novels:
            return True

    def whole_page_books(self, url):
        """Searches the whole pages for books and adds them to the JSON file"""
        print(f'Adding books from {url}. Hold on to your butts...')
        i = 1
        self.create_soup(url)
        books = self.soup.find_all(class_='fiction-title')
        for book in books:
            print('yes')
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
                return 'Error: Book not found'

    def scrape_top(self):
        self.results = []
        self.top_books_on_site()


