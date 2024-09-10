from sqlalchemy import Column, Integer, String, ForeignKey, Table ,MetaData, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text


engine = create_engine('sqlite:///digikala.db', echo=True)
Base = declarative_base()
session = sessionmaker(bind=engine)()


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    asset_id = Column(String)
    link = Column(String)
    photo = Column(String)
    name = Column(String)

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    asset_id = Column(String)
    link = Column(String)
    name = Column(String)
    price = Column(Integer)
    discount = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category")

Base.metadata.create_all(engine)