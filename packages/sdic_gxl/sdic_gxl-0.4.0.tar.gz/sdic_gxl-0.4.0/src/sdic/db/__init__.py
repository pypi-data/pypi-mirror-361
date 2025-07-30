from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import oracledb


class SdicDB:

    def __init__(self):
        self.uri = None
        self.engine = None
        self.sessionLocal = None
        self.session = None

    def connect(self, uri):
        """
        Connect to the database using the provided URI.
        :param uri: e.g: oracle+oracledb://root:password@localhost:1521/orcl
        :return: session object if connection is successful, otherwise raises an exception.
        """
        self.uri = uri
        self.engine = create_engine(self.uri, echo=True)
        self.sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.sessionLocal()
        # check if the connection is successful
        try:
            self.engine.connect()
            print("Database connection established.")
            return self.session
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            self.close()
            raise

    def close(self):
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
        self.session = None
        self.engine = None
        self.sessionLocal = None
        self.uri = None
        return True


client = SdicDB()


