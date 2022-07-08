# Book Scraping Project For API and DB Practice

## Description

This is a prototype project to get more experience in working with and developing
an API as well as serve as an introduction to working with webservers and databases. 
The end goal of this project is to create a simple webserver that can be used by others
to search for a book from [Royal Road](https://www.royalroad.com) to pull information such as total 
views, ratings, tags, and more.

## Setup

setup.py will install the dependencies. It will install the following:
1. Flask
2. lxml
3. requests
4. BeautifulSoup4

### Installation

1. Create a virtual environment 
   1. ```commandline
      python3 -m venv c:\path\to\myenv
      ```
      
2. Activate your virtual environment
   1. ```text
      <venv>\Scripts\activate.bat 
      ```

3. Navigate to setup.py and install dependencies
   1. ```commandline
      cd ~/projectdirectory/setup/
      pip install .
      ```

## Directions

After installing the dependencies:
1. Run main.py
2. Open up a web browser and navigate to http://127.0.0.1:5000 
3. To search for a book, adjust the url to include the routing path to the actual
search. http://127.0.0.1:5000/api/v1/resources/books?title=
4. Include the name of the book you want to search for after the title parameter:
5. To search for books on the following pages, include the value that is associated:
```text
top ongoing -> ?top=True&ongoing=True
best rated -> ?top=True&best rated=True
top complete -> ?top=True&completed=True
top rising stars -> ?top=True&rising stars=True
top trending -> ?top=True&weekly popular=True
```


## Import things to know before using:
1. Do **NOT** format the title parameter. The script will handle formatting for you.
Include spaces as you would a normal search on Google.
2. Apostrophes will cause the program to throw an error. This will be fixed in the
future but is not a priority at this point in time.
