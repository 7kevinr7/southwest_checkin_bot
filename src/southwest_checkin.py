"""
This module contains the check in functionality
"""

from traceback import print_exc
from time import sleep
from datetime import date, datetime
from datetime import timedelta

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class EndOfTriesException(Exception):
    pass


class CheckIn:
    """ This class provides the core check in functionality. """

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
        self._time_start = preferences.time_start
        self._time_end = preferences.time_end

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
            #self._log_into_account()
            self._poll()
            # unreachable unless successfully checked in
            # detaches browser so successful check in
            return True
        except EndOfTriesException as e:
            print(e)
        except Exception as e:
            print(print_exc())

        return False

    def _wait(self):
        """
        wait - pre-poll wait
        :return: None
        """

        if self._time_start is not None:
            current_time = datetime.now().time()
            print("Current time is " + str(current_time.strftime("%H:%M:%S")) +
                  ", Waiting until " + str(self._time_start) + " to begin polling the page")
            if self._time_start > current_time:
                current_time = datetime.now().time()
                curr_seconds = (current_time.hour * 60 + current_time.minute) * 60 + current_time.second
                start_seconds = \
                    (self._time_start.hour * 60 + self._time_start.minute) * 60 + self._time_start.second

                sleep(start_seconds - curr_seconds - 1)
            print("Began processing at " + str(self._time_start.strftime("%H:%M:%S")))

    def _poll(self):
        self._fill_out_form()
        self._wait()
        retries = 0

        if self._time_end:
            current_time = datetime.now().time()
            while current_time < self._time_end:
                self._checkin()
                if not self._check_for_errors():
                    self._handle_covid_case()
                    self._finish()
                    return True

                retries += 1
                current_time = datetime.now().time()
                #self._fill_out_form()
        else:
            while retries < self._num_refreshes:
                self._checkin()
                if not self._check_for_errors():
                    self._handle_covid_case()
                    self._finish()
                    return True

                retries += 1
                #self._fill_out_form()

        except_str = CheckIn.format_passenger_string(self._passenger) \
                     + ": driver stopping, tried " \
                     + str(retries) + " times"

        if self._time_end:
            except_str += ", reached timeout " + str(self._time_end)

        # Unable to successfully checkin
        raise EndOfTriesException(except_str)

    def _navigate_site(self):
        """
        navigate_site - opens the desired url in the driver
        :return: None
        """
        try:
            self._driver.get(self._url)
        except Exception as e:
            print(CheckIn.format_passenger_string(self._passenger)
                  + ": CheckIn._navigate_site() failed: "
                  + self._url)
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

            WebDriverWait(self._driver, self._long_delay).until(
                ec.visibility_of_element_located((By.ID, "username"))
            )

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
            print(CheckIn.format_passenger_string(self._passenger)
                  + ": CheckIn._log_into_account() failed")
            print(print_exc())
            raise e

    def _fill_out_form(self):
        """
        _fill_out_form - fills out this passengers info
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

        except Exception as e:
            print(print_exc())
            print(CheckIn.format_passenger_string(self._passenger)
                  + ": CheckIn._fill_out_form() failed")
            raise e

    def _checkin(self):
        """
        _checkin - handles the check in process
        :return: None
        """
        try:
            checkin_button = self._driver.find_element_by_id("form-mixin--submit-button")
            checkin_button.click()

        except Exception as e:
            print(print_exc())
            print(CheckIn.format_passenger_string(self._passenger)
                  + ": CheckIn._checkin() failed")
            raise e

    def _check_for_errors(self):
        """
        _check_for_errors - checks the page to see if there are any issues
        :return: bool - True if errors, false otherwise
        """
        try:
            unable_to_retrieve_error = self._driver.find_elements_by_xpath(
                "//h2[contains(text(), 'We are unable to retrieve your reservation')]")

            found_errors = self._driver.find_elements_by_xpath(
                "//h2[contains(text(), 'Sorry, we found some errors')]")

            online_checkin_invalid_time = self._driver.find_elements_by_xpath(
                "//h2[contains(text(), 'Online check-in not valid')]")

            if len(unable_to_retrieve_error) == 0 \
                    and len(found_errors) == 0 \
                    and len(online_checkin_invalid_time) == 0:
                return False

        except Exception as e:
            print(print_exc())
            print(CheckIn.format_passenger_string(self._passenger)
                  + ": CheckIn._check_for_errors() failed")
            raise e

        return True

    def _handle_covid_case(self):
        """
        _handle_covid_case - handles the covid popup
        :return: None
        """
        try:
            confirm_button = self._driver.find_elements_by_xpath(
                "//button[contains(@data-a, 'airCheckInReviewResults_checkIn')]")

            if len(confirm_button) == 0:
                return

            confirm_button[0].click()

        except Exception as e:
            print(print_exc())
            print(CheckIn.format_passenger_string(self._passenger)
                  + ": CheckIn._handle_covid_case() failed")
            raise e

    def _finish(self):
        """
        _finish - handles processing of page after check in has occurred
        :return:
        """
        try:
            pass

        except Exception as e:
            print(print_exc())
            print(CheckIn.format_passenger_string(self._passenger)
                  + ": CheckIn._finish() failed")
            raise e
