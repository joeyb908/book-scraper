from bs4 import BeautifulSoup
import lxml
import requests
import pprint
from flask import Flask

pp = pprint.PrettyPrinter(indent=4, compact=True)
BASE_URL = 'https://www.royalroad.com/'
URL = 'https://www.royalroad.com/fiction/21220/mother-of-learning'
response = requests.get(url=URL)
webpage = response.text
soup = BeautifulSoup(webpage, 'lxml')
# pp.pprint(soup)

# finds book title
title = soup.find(property='name', ).get_text()

# find author using selectors
# a list gets returned even though it's only a single index
author = soup.select_one('.col > h4 > :last-child > a').get_text()

# finds all the tags
found_tags = soup.findAll(class_='tags')
# creates list of tags
tags = [(tag.get_text().strip('\n').splitlines()) for tag in found_tags]
# 'unpacks list of tags' into a single dimension list as returned
# value from the comprehension was a nested empty list
[tags] = tags

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
    # pp.pprint(published_date)

# finds the rating and total rates of the book
rating = soup.find(property='ratingValue').attrs['content']
rate_count = soup.find(property='ratingCount').attrs['content']

# find total views, followers, favorites, and pages
stats = soup.select('.stats-content > :last-child > ul > :nth-child(even)')
views = stats[0].get_text()
followers = stats[2].get_text()
favorites = stats[3].get_text()
pages = stats[5].get_text()

book_info = {
    'title': title,
    'author': author,
    'tags': tags,
    'pages': pages,
    'chapter': chapter_list,
    'chapter_count': len(chapter_list),
    'rating': rating,
    'total_rates': rate_count,
    'views': views,
    'favorites': favorites,
    'followers': followers,
}

pp.pprint(book_info)

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route("/", methods=['GET'])
def home():
    return "<p>Hello, World!</p>"

#
# if __name__ == '__main__':
#     app.run()
