# -*- coding: utf-8 -*-
"""
Created on Fri Aug  6 14:56:52 2021

@author: krose
"""

from os import path
from os import getcwd
from re import sub


class NoPassengerFileException(Exception):
    pass


class NoPassengersException(Exception):
    pass


class PassengerHandler:

    def __init__(self, passengers='preferences/passengers.txt'):
        """
        __init__ - handles parsing the passengers file
        :param passengers: path to the file containing passengers and confirmation details
        """
        self.passengers = dict()

        passengers_path = path.join(getcwd(), passengers)
        if not path.exists(passengers_path):
            raise NoPassengerFileException("Passengers File does not exist @: " + passengers_path)

        passenger_data = list()

        with open(passengers_path, "r") as passengers_file:
            for line in passengers_file:
                if not line.strip().startswith("#") and line.strip() != "":
                    passenger_data.append(line.strip())

        if len(passenger_data) == 0:
            raise NoPassengersException("Locations File does not contain any locations")

        for passenger in passenger_data:
            passenger_info = [info.strip() for info in passenger.split("-")]
            first, last, confirmation = passenger_info[0], passenger_info[1], passenger_info[2]

            self.passengers[first + ":" + last] = int(sub("[^0-9]", "", confirmation) if
                                                      confirmation.strip() != "" else 0)
