import sqlalchemy

Base = sqlalchemy.orm.declarative_base()


class Joke(Base):
    __tablename__ = 'joke'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    joke = sqlalchemy.Column(sqlalchemy.String)
    english_joke = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    allowed = sqlalchemy.Column(sqlalchemy.String)


class Bans(Base):
    __tablename__ = 'bansuser'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
