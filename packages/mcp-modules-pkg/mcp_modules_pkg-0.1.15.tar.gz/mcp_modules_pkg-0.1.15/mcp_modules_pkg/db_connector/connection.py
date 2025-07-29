
from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

from .database import ID_LEN, DataBase

Base = declarative_base()

class Connection(Base):
    """Represents a database connection record.

    This class provides methods to handle database connections, including retrieving and
    decrypting connection information from a database.

    Attributes:
        EXTRA_KEY (str): A class attribute that stores the key name for extra attributes.
        __tablename__ (str): The name of the database table this class is mapped to.
        id (Column): The primary key column.
        conn_id (Column): A unique identifier for the connection.
        conn_type (Column): The type of the connection.
        description (Column): A description of the connection.
        host (Column): The host of the database.
        schema (Column): The schema of the database.
        login (Column): The login username.
        _password (Column): The encrypted password (not directly accessible).
        port (Column): The port number for the connection.
        is_encrypted (Column): A flag indicating if the password is encrypted.
        is_extra_encrypted (Column): A flag indicating if the extra is encrypted.
        _extra (Column): Encrypted extra configuration options (not directly accessible)
    """

    EXTRA_KEY = "__extra__"

    __tablename__ = "connection"

    id = Column(Integer(), primary_key=True)
    conn_id = Column(String(ID_LEN), unique=True, nullable=False)
    conn_type = Column(String(500), nullable=False)
    description = Column(Text(5000))
    host = Column(String(500))
    schema = Column(String(500))
    login = Column(String(500))
    _password = Column("password", String(5000))
    port = Column(Integer())
    is_encrypted = Column(Boolean, unique=False, default=False)
    is_extra_encrypted = Column(Boolean, unique=False, default=False)
    _extra = Column("extra", Text())

    @classmethod
    def get_db(cls):
        """Retrieves a database session.

        Returns:
            A database session object.
        """
        db = DataBase.session_local()
        return db

    @classmethod
    def get_connection(cls, conn_id: str) -> "Connection":
        """Gets a connection object by its connection ID.

        Args:
            conn_id (str): The connection ID to search for.

        Returns:
            Connection: An instance of `Connection` with the specified connection ID.

        Raises:
            Exception: If the connection cannot be retrieved or decrypted.
        """
        try:
            db = cls.get_db()
            conn = db.query(Connection).filter(Connection.conn_id == conn_id).first()
            conn = cls.decrypt_connection(conn)
            return conn
        except Exception as err:
            print(err)
        finally:
            db.close()

    @classmethod
    def decrypt_connection(cls, conn: "Connection") -> "Connection":
        """Decrypts the password and extra information of a connection.

        Args:
            conn (Connection): The connection object to decrypt.

        Returns:
            Connection: The connection object with decrypted values.
        """
        if conn.is_encrypted:
            conn._password = cls.decrypt_passwd(conn._password)
        if conn.is_extra_encrypted:
            conn._extra = cls.decrypt_passwd(conn._extra)
        return conn

    @classmethod
    def decrypt_passwd(cls, password: str) -> str:
        """Decrypts an encrypted password.

        Args:
            password (str): The encrypted password.

        Returns:
            str: The decrypted password.
        """
        fernet = DataBase.get_fernet()
        return fernet.decrypt(bytes(password, "utf-8")).decode()

    @classmethod
    def decrypt_extra(cls, extra: str) -> str:
        """Decrypts encrypted extra configuration options.

        Args:
            extra (str): The encrypted extra configuration options.

        Returns:
            str: The decrypted extra configuration options.
        """
        fernet = DataBase.get_fernet()
        return fernet.decrypt(bytes(extra, "utf-8")).decode()


def main():
    """Main function to demonstrate use of the Connection class."""
    a = Connection()
    conn = a.get_connection(conn_id="idb_prediction_report")
    print(conn.host)
    print(conn.login)


if __name__ == "__main__":
    main()

