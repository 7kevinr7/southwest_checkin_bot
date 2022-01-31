"""
This module provides the Overseer which performs each of the bot's functions
"""

import multiprocessing as mp
from traceback import print_exc
from selenium import webdriver
from os import path
from os import getcwd

from src.southwest_checkin import CheckIn
import src.preferences_handler as ph


class Overseer:
    """ This class provides the Overseer which handles all of the bot's main
        functionality. """

    def __init__(self, prefs='preferences/preferences.txt'):
        """
        __init__ - basic constructor
        :param prefs: the preference file to be used
        """
        self.preferences = ph.PreferencesHandler(prefs)

    @staticmethod
    def merge_parameters(locations, rec_type):
        return [[location, rec_type] for location in locations]

    def start_driver(self, passenger):
        """
        start_driver - creates the chrome driver and starts the browser
        :param passenger: the passenger that this driver is being created for
        :return: None
        """
        driver = None
        try:
            print(CheckIn.format_passenger_string(passenger) + ": driver starting")
            exec_path = path.join(getcwd(), 'chromedriver')
            driver = webdriver.Chrome(executable_path=exec_path,
                                      chrome_options=webdriver.ChromeOptions())
            driver.maximize_window()
            driver.implicitly_wait(self.preferences.wait_duration)

        except Exception as e:
            print(print_exc())
            print(CheckIn.format_passenger_string(passenger)
                  + ": Unable to create driver for location: ")
            driver = None

        if driver is not None:
            checkin = CheckIn(driver=driver, preferences=self.preferences,
                              passenger=passenger)

            if not checkin.execute():
                print(CheckIn.format_passenger_string(passenger) + ": driver stopping")
                driver.quit()
            else:
                print(CheckIn.format_passenger_string(passenger) + ": successfully checked in")

    def start(self):
        """
        start - creates a separate process for each driver
        :return: None
        """
        process_pool = mp.Pool(processes=len(self.preferences.reservation_details.keys()))

        process_pool.map(self.start_driver, self.preferences.reservation_details.keys())

