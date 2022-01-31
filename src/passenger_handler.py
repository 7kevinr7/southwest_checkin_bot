"""
This module performs parsing of the passenger's info
"""

from os import path
from os import getcwd
from re import sub


class NoPassengerFileException(Exception):
    pass


class NoPassengersException(Exception):
    pass


class PassengerHandler:
    """ This class provides a passenger handler. """

    def __init__(self, passengers='preferences/passengers.txt'):
        """
        __init__ - handles parsing the passengers file
        :param passengers: path to the file containing passengers and confirmation details
        """
        self.passengers = dict()

        passengers_path = path.join(getcwd(), passengers)
        if not path.exists(passengers_path):
            raise NoPassengerFileException("Passengers File does not exist @: "
                                           + passengers_path)

        passenger_data = list()

        with open(passengers_path, "r") as passengers_file:
            for line in passengers_file:
                if not line.strip().startswith("#") and line.strip() != "":
                    passenger_data.append(line.strip())

        if len(passenger_data) == 0:
            raise NoPassengersException("Passengers File does not contain any passengers")

        for passenger in passenger_data:
            passenger_info = [info.strip() for info in passenger.split("-")]
            first, last, confirmation = passenger_info[0], passenger_info[1], passenger_info[2]

            self.passengers[first + ":" + last] = confirmation.strip()
