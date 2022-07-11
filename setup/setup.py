from setuptools import setup

setup(name='book-scraper',
      version='0.1',
      description='A prototype book-scraper',
      url='https://github.com/joeyb908/book-scraper',
      author='joeyb908',
      author_email='joey@ohannesian.io',
      license='MIT',
      install_requires=['beautifulsoup4==4.11.1',
                        'flask==2.1.2',
                        'lxml==4.9.0',
                        'requests==2.28.1',
                        'Flask-SQLAlchemy==2.5.1'],
      )
