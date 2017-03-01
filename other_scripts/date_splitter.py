__author__ = 'peterking'

import datetime


def create_datetime(raw_timestamp):

    split = raw_timestamp.split()

    date_list = split[0].split("/")

    month = int(date_list[0])
    day = int(date_list[1])
    year = int(date_list[2])

    time_split = split[1].split(":")

    if split[2] == 'PM':
        time_split[0] = int(time_split[0]) + 12

    hour = int(time_split[0])
    minute = int(time_split[1])
    second = int(time_split[2])

    return year, month, day, hour, minute, second

test_1 = create_datetime("11/20/2016 5:34:00 PM")
test_2 = create_datetime("11/22/2016 11:34:00 PM")

dt_test_1 = datetime.datetime(test_1[0], test_1[1], test_1[2], test_1[3], test_1[4])
dt_test_2 = datetime.datetime(test_2[0], test_2[1], test_2[2], test_2[3], test_2[4])

def create_timedelta(datetime_1, datetime_2):
    delta = datetime_2 - datetime_1
    return delta

delta = create_timedelta(dt_test_1, dt_test_2)

print(type(delta))