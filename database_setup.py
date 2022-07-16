from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableList

Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'

    id = Column('id', Integer, primary_key=True)
    title = Column('title', String, unique=False, nullable=False)
    url = Column('url', String, unique=True, nullable=False)
    img_url = Column('img_url', String, unique=True, nullable=False)
    author = Column('author', String, unique=False, nullable=False)
    tags = Column('tags', MutableList.as_mutable(PickleType), unique=False, default=[], nullable=False)
    pages = Column('pages', Integer, unique=False, nullable=False)
    chapter = Column('chapter', MutableList.as_mutable(PickleType), unique=False, default=[], nullable=False)
    chapter_count = Column('chapter_count', Integer, unique=False, nullable=False)
    rating = Column('rating', Float, unique=False, nullable=False)
    total_rates = Column('total_rates', Integer, unique=False, nullable=False)
    views = Column('views', Integer, unique=False, nullable=False)
    favorites = Column('favorites', Integer, unique=False, nullable=False)
    followers = Column('followers', Integer, unique=False, nullable=False)

    def __init__(self, id, title, url, img_url, tags, author, pages, chapter, chapter_count, rating, total_rates, views, favorites, followers):
        self.id = id
        self.title = title
        self.url = url
        self.img_url = img_url
        self.tags = tags
        self.rating = rating
        self.total_rates = total_rates
        self.views = views
        self.favorites = favorites
        self.followers = followers
        self.author = author
        self.pages = pages
        self.chapter = chapter
        self.chapter_count = chapter_count

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def serialize(self):

        return {'id': self.id,
                'title': self.title,
                'url': self.title,
                'img_url': self.img_url,
                'tags': self.tags,
                'rating': self.rating,
                'total_rates': self.total_rates,
                'views': self.views,
                'favorites': self.favorites,
                'followers': self.followers,
                'author': self.author,
                'pages': self.pages,
                'chapter': self.chapter,
                'chapter_count': self.chapter_count}


engine = create_engine('sqlite:///book-collection.db', echo=True)
Base.metadata.create_all(bind=engine)
