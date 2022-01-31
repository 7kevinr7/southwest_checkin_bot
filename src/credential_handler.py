"""
This module provides a credential parser.
"""

from os import path
from os import getcwd


class NoCredentialsFileException(Exception):
    pass


class NoCredentialsException(Exception):
    pass


class CredentialHandler:
    """ This class provides a credential handler. """

    def __init__(self, credentials='preferences/credentials.txt'):
        """
        __init__ - constructor that handles the parsing the credentials file
        :param credentials: path to the credentials file
        """
        self.credentials = list()

        credentials_path = path.join(getcwd(), credentials)
        if not path.exists(credentials_path):
            raise NoCredentialsFileException("Credentials File does not exist @: "
                                             + credentials_path)

        with open(credentials_path, "r") as credentials_file:
            for line in credentials_file:
                if line.strip() != "" and not line.startswith("#"):
                    self.credentials.append(line.strip())

        if len(self.credentials) == 0:
            raise NoCredentialsException("Credentials File does not contain any credentials")
