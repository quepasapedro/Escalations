__author__ = 'peterking'

import csv
import datetime
import statistics
import sys
import test_quickstart

def create_datetime(raw_timestamp):

    split_raw = list(raw_timestamp.split())

    date_list = list(split_raw[0].split("/"))

    month = int(date_list[0])
    day = int(date_list[1])
    year = int(date_list[2])

    time_split = split_raw[1].split(":")

    hour = int(time_split[0])
    minute = int(time_split[1])
    second = int(time_split[2])

    if split_raw[2] == 'PM' and hour > 12:
        hour += 12

    return year, month, day, hour, minute, second


def create_reader(metrics_file, args):

    def date_parse(args):
        if '--date_start' in args:
            start_date_arg = args[args.index('--date_start') + 1]
            start_date_split = start_date_arg.split("/")

            start_date = datetime.datetime(int(start_date_split[2]), int(start_date_split[0]), int(start_date_split[1]))

        elif '--date_start' not in args:
            print("Using 01/01/2016 as the Start Date.")
            start_date = datetime.datetime(2016, 01, 01)

        if '--date_end' in args:
            end_date_arg = args[args.index('--date_end') + 1]
            end_date_split = end_date_arg.split("/")

            end_date = datetime.datetime(int(end_date_split[2]), int(end_date_split[0]), int(end_date_split[1]))

        elif '--date_end' not in args:
            print("Using today's date as the End Date.\n")
            end_date_arg = datetime.datetime.today()

            end_date = datetime.datetime(end_date_arg.year, end_date_arg.month, end_date_arg.day)

        return start_date, end_date

    dates = date_parse(args)
    start_date = dates[0]
    end_date = dates[1]

    # with open(metrics_file) as metrics_file:
    # reader = csv.DictReader(metrics_file, delimiter=",")
    rows = list(metrics_file)
    return_rows = []

    for row in rows:
        filed_dt = create_datetime(row['FullFiled'])
        filed = datetime.datetime(filed_dt[0], filed_dt[1], filed_dt[2])

        # if row['Blob'] == '':
        #     continue

        if filed >= start_date and filed <= end_date:
            return_rows.append(row)
        else:
            continue

    return return_rows


def agent_counter(metrics_file):
    agent_dict = {}
    for row in metrics_file:
        if row['Agent'] == '':
            continue
        elif row['Agent'] in agent_dict.keys():
            agent_dict[row['Agent']] += 1
        else:
            agent_dict[row['Agent']] = 1

    print("Agent frequencies:")
    for key in agent_dict:
        print("{}: {}".format(key, agent_dict[key]))

    return agent_dict


def author_counter(metrics_file):
    author_dict = {}
    for row in metrics_file:
        if row['Author'] == '':
            continue
        elif row['Author'] in author_dict.keys():
            author_dict[row['Author']] += 1
        else:
            author_dict[row['Author']] = 1

    print("Agent frequencies:")
    for key in author_dict:
        print("{}: {}".format(key, author_dict[key]))

    return author_dict


def category_counter(metrics_file):
    category_dict = {}
    for row in metrics_file:
        if row['Category'] == '':
            continue
        elif row['Category'] in category_dict.keys():
            category_dict[row['Category']] += 1
        else:
            category_dict[row['Category'].strip()] = 1

    print("Category frequencies:\n")
    for key in category_dict.keys():
        print("{}: {}".format(key, category_dict[key]))
    return category_dict


def category_average(metrics_file):

    category_sla_dict = {}

    def create_time_delta(filed, replied):

        filed_dt = datetime.datetime(filed[0], filed[1], filed[2], filed[3], filed[4])
        replied_dt = datetime.datetime(replied[0], replied[1], replied[2], replied[3], replied[4])

        sla = replied_dt - filed_dt

        return sla

    for row in metrics_file:

        if row['Category'] == '':
            continue
        elif row['Category'] in category_sla_dict.keys():
            filed = create_datetime(row['FullFiled'])
            replied = create_datetime(row['FullResponse'])

            sla = create_time_delta(filed, replied)

            category_sla_dict[row['Category']].append(sla.seconds)
        else:
            filed = create_datetime(row['FullFiled'])
            replied = create_datetime(row['FullResponse'])

            sla = create_time_delta(filed, replied)

            category_sla_dict[row['Category']] = [sla.seconds]

    category_averages = {}

    for key in category_sla_dict.keys():
        category_averages[key] = statistics.mean(category_sla_dict[key])

    for item in category_averages.keys():
        print("{}: {}".format(item, category_averages[item]))


def flags(args, metrics_file):

    metrics_dict = create_reader(metrics_file, args)

    if "--help" in args or '-h' in args:
        print("\nWelcome to the Escalations Team metrics script.\n"
              "Syntax: 'python metrics_script.py [flags]'.\n\n"
              ""
              "Flag options:\n"
              "Agent Counter: --agent\n"
              "Author Counter: --author\n"
              "Category Counter: --catcount\n"
              "Category Average: --cataverage\n"
              "Start Date ('MM/DD/YYYY'): --date_start\n"
              "End Date ('MM/DD/YYYY'): --date_end\n"
              "Help: --help or -h\n")

    if '--agent' in args:
        agent_counter(metrics_dict)

    if '--author' in args:
        author_counter(metrics_dict)

    if '--catcount' in args:
        category_counter(metrics_dict)

    if '--cataverage' in args:
        category_average(metrics_dict)

    # else:
    #     print("\nWhoops! Didn't recognize your flag. Please type '-h' or '--help' to see flag options.")

args = sys.argv
raw_file = test_quickstart.run()
flags(args, raw_file)