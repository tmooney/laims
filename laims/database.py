from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from laims.models import Base


def open_db(db_path):
    db_url = 'sqlite:///' + db_path
    db = create_engine(db_url)
    Base.metadata.create_all(db)
    return sessionmaker(bind=db)

