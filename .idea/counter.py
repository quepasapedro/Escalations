__author__ = 'peterking'

__author__ = 'peterking'

import csv
import datetime
import statistics
import sys


def create_reader(metrics_file):
    with open(metrics_file) as metrics_file:
        reader = csv.DictReader(metrics_file, delimiter=",")
        rows = list(reader)
        return_rows = []
        for row in rows:
            if row['Blob'] == '':
                continue
            else:
                return_rows.append(row)
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
    print("Agent frequencies: {}".format(agent_dict))
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
    print("Author frequencies: {}".format(author_dict))
    return author_dict


def category_counter(metrics_file):
    category_dict = {}
    for row in metrics_file:
        if row['Category'] == '':
            continue
        elif row['Category'] in category_dict.keys():
            category_dict[row['Category']] += 1
        else:
            category_dict[row['Category']] = 1
    print("Category frequencies: {}".format(category_dict))
    return category_dict


def category_average(metrics_file):

    category_sla_dict = {}

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


def flags(args, metrics_dict):
    if "--help" in args or '-h' in args:
        print("\nWelcome to the Escalations Team metrics script.\n"
              "Syntax: 'python metrics_script.py [flags]'.\n\n"
              ""
              "Flag options:\n"
              "Agent Counter: --agent\n"
              "Author Counter: --author\n"
              "Category Counter: --catcount\n"
              "Category Average: --cataverage\n"
              "Help: --help or -h\n")

    elif '--agent' in args:
        agent_counter(metrics_dict)

    elif '--author' in args:
        author_counter(metrics_dict)

    elif '--catcount' in args:
        category_counter(metrics_dict)

    elif '--cataverage' in args:
        category_average(metrics_dict)

    elif args is False:
        print("Please enter arguments!")

    else:
        print("\nWhoops! Didn't recognize your flag. Please type '-h' or '--help' to see flag options.")

metrics_dict = create_reader("escalations_metrics_1.csv")
args = sys.argv
flags(args, metrics_dict)