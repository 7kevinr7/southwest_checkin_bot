# -*- coding: utf-8 -*-
"""
Created on Fri Aug  6 14:56:52 2021

@author: krose
"""

from traceback import print_exc
from time import sleep

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class CheckIn:

    def __init__(self, driver=None, preferences=None, passenger=None):
        self._driver = driver
        self._passenger = passenger
        self._confirmation_number = preferences.reservation_details[passenger]
        self._credentials = preferences.credentials
        self._login = preferences.login
        self._wait_duration = preferences.wait_duration
        self._long_delay = preferences.long_delay
        self._url = preferences.url
        self._num_refreshes = preferences.num_refreshes

    @staticmethod
    def find_parent_with_tag(element, target):
        """
        find_parent_with_tag - provides parent traversal to find a tag set to value
        :param element: the child element of the desired element
        :param target: the tag name to look for
        :return: WebElement: the parent WebElement of the provided child, None if the element is not found
        """
        try:
            while element.tag_name.strip() != target:
                element = element.find_element_by_xpath("..")
            return element

        except Exception as e:
            print("CheckIn.find_parent_with_tag() failed")
            print(print_exc())

        return None

    @staticmethod
    def format_passenger_string(passenger_str):
        """
        format_passenger_string - formats the passenger string into a decent format
        :param passenger_str: the passenger to format
        :return:
        """
        return " - ".join(passenger_str.split(":"))

    def execute(self):
        try:
            self._navigate_site()
            self._log_into_account()
            return self._poll()

        except Exception as e:
            print(print_exc())

        return False

    def _poll(self):
        retries = 0
        while retries < self._num_refreshes:
            self._driver.refresh()
            self._check_in()
            self._finish()
            retries += 1

        return False

    def _navigate_site(self):
        """
        navigate_site - opens the desired url in the driver
        :return: None
        """
        try:
            self._driver.get(self._url)
        except Exception as e:
            print(CheckIn.format_passenger_string(self._passenger) + ": CheckIn._navigate_site() failed: " + self._url)
            print(print_exc())
            raise e

    def _log_into_account(self):
        """
        log_into_account - logs into the account with credentials provided if desired
        :return: None
        """
        try:
            # Only logs in if intended to and has valid credentials
            if not self._login or self._credentials is None:
                return

            # Grab the sign-in button
            login_button = self._driver.find_element_by_xpath("//span[contains(text(), 'Log in')]")
            login_button = CheckIn.find_parent_with_tag(login_button, "button")
            login_button.click()

            WebDriverWait(self._driver, self._long_delay).until(ec.visibility_of_element_located((By.ID, "username")))

            # Grab the username / password elements
            username = self._driver.find_element_by_id("username")
            password = self._driver.find_element_by_id("password")

            # Send credentials
            username.send_keys(self._credentials[0])
            password.send_keys(self._credentials[1])

            submit_button = self._driver.find_elements_by_class_name("login-form--submit-button")

            if len(submit_button) > 0 and submit_button[0].tag_name == "button":
                submit_button[0].click()
            else:
                login_button.send_keys(Keys.ESCAPE)

            # Wait for login screen to clear
            sleep(self._wait_duration)

        except Exception as e:
            print(CheckIn.format_passenger_string(self._passenger) + ": CheckIn._log_into_account() failed")
            print(print_exc())
            raise e

    def _check_in(self):
        """
        _check_in - fills out this passengers info and hits "Check in"
        :return: None
        """
        try:
            confirmation_number = self._driver.find_element_by_id("confirmationNumber")
            first_name = self._driver.find_element_by_id("passengerFirstName")
            last_name = self._driver.find_element_by_id("passengerLastName")

            confirmation_number.send_keys(Keys.CONTROL + 'a')
            confirmation_number.send_keys(self._confirmation_number)
            first_name.send_keys(Keys.CONTROL + 'a')
            first_name.send_keys(self._passenger.split(":")[0])
            last_name.send_keys(Keys.CONTROL + 'a')
            last_name.send_keys(self._passenger.split(":")[1])

            checkin_button = self._driver.find_element_by_id("form-mixin--submit-button")
            checkin_button.click()

        except Exception as e:
            print(print_exc())
            print(CheckIn.format_passenger_string(self._passenger) + ": CheckIn._fill_out_info() failed")
            raise e

    def _finish(self):
        """
        _finish - handles processing of page after check in has occurred
        :return:
        """
        #sleep(self._long_delay)
        pass
