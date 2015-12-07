import sqlite3
from selenium import webdriver
import datetime as dt
import time
import re
import os


def _get_credentials():
    conn = sqlite3.connect('main')

    res = conn.execute('select * from logins where site == "Google"')
    info = res.fetchone()
    email, password = info[1:]

    return email, password


def _login(email, password):
    driver.find_element_by_id('Email').send_keys(email)
    driver.find_element_by_id('next').click()
    time.sleep(1)
    driver.find_element_by_id('Passwd').send_keys(password)
    driver.find_element_by_id('signIn').click()
    time.sleep(1)


def _query():
    driver.find_element_by_id('gbqfq').send_keys('subject:spiritual cyber-vitamin')
    driver.find_element_by_id('gbqfb').click()
    time.sleep(1)


def _open_last_email():
    tables = driver.find_elements_by_tag_name('tbody')

    for table in tables:
        first_row = table.find_element_by_tag_name('tr')
        if 'Greater Fort Wayne' in first_row.text:
            first_row.click()
            time.sleep(1)
            return


def _find_room():
    ulists = driver.find_elements_by_tag_name('ul')

    for ul in ulists:
        if 'Student Leaders Meeting' in ul.text:
            # found it!!!
            meeting_pattern = '[Ss]tudent [Ll]eaders? [Mm]eeting:.+[Rr]oom [Gg]?\d{2}\d?'
            matches = re.findall(meeting_pattern, ul.text)
            if matches:
                match = matches[0]
            else:
                return None
            room_pattern = '[Rr]oom [Gg]?\d{2}\d?'
            matches = re.findall(room_pattern, match)
            if matches:
                # ['Room 226'] -> '226'
                room = matches[0].split()[1]
                return room
            else:
                return None


def _find_date():
    spans = driver.find_elements_by_tag_name('span')

    for span in spans:
        date_pattern = '.+day, .+ \d\d?, \d{4}'
        matches = re.findall(date_pattern, span.text)
        if matches:
            # ['Monday, December 7, 2015'], ... -> ['December', '7']
            date = matches[0].split(', ')[1].split()
            if len(date[1]) == 1:
                date[1] = '0' + str(date[1])
            return date


def _verify_date(ext_date):
    today_day = dt.datetime.today().strftime('%d')
    today_month = dt.datetime.today().strftime('%B')
    today = [today_month, today_day]
    if today == ext_date:
        return True
    return False


def find_room():
    # initialize driver and set to url
    url = 'https://mail.google.com/mail/u/0/#inbox'
    driver.get(url)

    email, password = _get_credentials()

    _login(email, password)

    _query()

    _open_last_email()

    room = _find_room()

    date = _find_date()

    if _verify_date(date):
        return room


driver = webdriver.PhantomJS(service_log_path=os.path.devnull)
if __name__ == '__main__':
    find_room()
