import os

dirname = os.path.dirname(__file__)


def get_last_eod_file(mode='r'):
    eod_file_name = os.path.join(dirname, 'last_eod.txt')
    eod_file = open(eod_file_name, mode)
    return eod_file


def get_last_eod_script_date():
    eod_file = get_last_eod_file()

    last_eod_date = str(eod_file.read())
    eod_file.close()
    return last_eod_date


def write_to_eod_file(file_content):
    eod_file = get_last_eod_file('w')
    eod_file.write(file_content)
    eod_file.close()
