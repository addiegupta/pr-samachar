import os

from date_utils import get_utc_now, get_date_from_string, subtract_hours_from_date

dirname = os.path.dirname(__file__)


def get_last_eod_file(mode='r'):
    eod_file_path = os.path.join(dirname, 'last_eod.txt')

    # create eod file if it doesnt exist
    if not os.path.exists(eod_file_path):
        open(eod_file_path, 'w+').close()

    eod_file = open(eod_file_path, mode)
    return eod_file


def get_last_eod_script_date():
    eod_file = get_last_eod_file()

    last_eod_string = str(eod_file.read())
    eod_file.close()

    last_eod_date = get_date_from_string(last_eod_string)

    # return date from 1 day ago if eod file is empty
    if not last_eod_date:
        last_eod_date = subtract_hours_from_date(get_utc_now(), 24)

    return last_eod_date


def write_to_eod_file(file_content):
    eod_file = get_last_eod_file('w')
    eod_file.write(file_content)
    eod_file.close()
