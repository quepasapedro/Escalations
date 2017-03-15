__author__ = 'peterking'

import datetime
import statistics
import api_caller
import click


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


def create_reader(raw_rows, start_date, end_date):

    utf_values = []
    for row in raw_rows:
        temp_list = []
        for item in row:
            temp_list.append(item.encode('utf-8'))
        utf_values.append(temp_list)

    key_list = []
    for item in utf_values[0]:
        key_list.append(item)

    del(utf_values[0])

    parsed_dict = []
    for row in utf_values:
        key_index = 0
        row_dict = {}
        for item in row:
            row_dict[key_list[key_index]] = item
            key_index += 1

        filed_dt = create_datetime(row_dict['FullFiled'])
        filed = datetime.datetime(filed_dt[0], filed_dt[1], filed_dt[2])

        if end_date >= filed >= start_date:
            parsed_dict.append(row_dict)
        else:
            continue

    return parsed_dict


def agent_counter(metrics_file):
    agent_dict = {}
    for row in metrics_file:
        if row['Agent'] in agent_dict.keys():
            agent_dict[row['Agent']] += 1
        else:
            agent_dict[row['Agent']] = 1

    agent_write_list = [['Escalations Agent', 'Ticket Count']]
    for key in agent_dict:
        agent_write_list.append([key, agent_dict[key]])

    return agent_dict, agent_write_list


def author_counter(metrics_file):
    author_dict = {}
    for row in metrics_file:
        if row['Author'] in author_dict.keys():
            author_dict[row['Author']] += 1
        else:
            author_dict[row['Author']] = 1

    author_write_list = [['Frontend Agent', 'Ticket Count']]
    for key in author_dict:
        author_write_list.append([key, author_dict[key]])

    return author_dict, author_write_list


def category_counter(metrics_file):
    category_dict = {}
    for row in metrics_file:
        if row['Category'] in category_dict.keys():
            category_dict[row['Category']] += 1
        else:
            category_dict[row['Category'].strip()] = 1

    catcount_write_list = [['Category', 'Tickets']]
    for key in category_dict.keys():
        catcount_write_list.append([key, category_dict[key]])

    return category_dict, catcount_write_list


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

    catavg_write_list = [['Category', 'Average SLA']]
    for key in category_averages.keys():
        catavg_write_list.append([key, category_averages[key]])

    return category_averages, catavg_write_list

def write(to_write):
    api_caller.write(to_write)
    pass

def flags(raw_file, author, agent, catcount, cataverage, date_start, date_end, write_flag):

    if date_start:
        start_date_split = date_start.split("/")
        start_date = datetime.datetime(int(start_date_split[2]), int(start_date_split[0]), int(start_date_split[1]))
    else:
        print("Using 01/01/2016 as the Start Date.")
        start_date = datetime.datetime(2016, 01, 01)

    if date_end:
        end_date_split = date_start.split("/")
        end_date = datetime.datetime(int(end_date_split[2]), int(end_date_split[0]), int(end_date_split[1]))
    else:
        print("Using today's date as the End Date.\n")
        end_date_arg = datetime.datetime.today()
        end_date = datetime.datetime(end_date_arg.year, end_date_arg.month, end_date_arg.day)

    metrics_dict = create_reader(raw_file, start_date, end_date)

    if agent:
        agent_dict, agent_write = agent_counter(metrics_dict)

        print("Agent frequencies:")
        for key in agent_dict:
            print("{}: {}".format(key, agent_dict[key]))

        if write_flag:
            write(agent_write)  # add "range" value
            pass

    if author:
        author_dict, author_write = author_counter(metrics_dict)

        print("Agent frequencies:")
        for key in author_dict:
            print("{}: {}".format(key, author_dict[key]))

        if write_flag:
            write(author_write)  # add "range" value

    if catcount:
        category_dict, category_write = category_counter(metrics_dict)

        print("Category frequencies:\n")
        for key in category_dict.keys():
            print("{}: {}".format(key, category_dict[key]))

        if write_flag:
            write(category_write)   # add "range" value

    if cataverage:
        category_averages, catavg_write = category_average(metrics_dict)

        print("Category averages:\n")
        for item in category_averages.keys():
            print("{}: {}".format(item, category_averages[item]))

        if write_flag:
            write(catavg_write)  # add "range" value

@click.command()
@click.option('--author', help='Author Counter: count tickets filed by CRCS agents.', is_flag=True)
@click.option('--agent', help='Agent Counter: count tickets answered by Escalations agents.', is_flag=True)
@click.option('--catcount', help='Category Counter: count tickets in each category.', is_flag=True)
@click.option('--cataverage', help='Category Average: calculate average time-to-response per category.', is_flag=True)
@click.option('--date_start', help='Start Date (format: MM/DD/YYY)', nargs=1)
@click.option('--date_end', help='End Date (format: MM/DD/YYY)', nargs=1)
@click.option('--write_flag', help='Boolean: write to Google Sheets?', is_flag=True)
def metrics(author, agent, catcount, cataverage, date_start, date_end, write_flag):
    raw_file = api_caller.read()
    flags(raw_file, author, agent, catcount, cataverage, date_start, date_end, write_flag)

metrics()