from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, scoped_session, Session


class SdicDB:
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.Session = None

    def connect(self, uri: str):
        self.engine = create_engine(uri)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        print("""
        The connection to database has been established successfully.😊
        """)


sdic_db = SdicDB()
