__author__ = 'peterking'

import datetime
import statistics
import api_caller
import click
import operator


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

    agent_write_list = []
    header_row = ['Escalations Agent', 'Ticket Count']
    for key in agent_dict:
        agent_write_list.append([key, agent_dict[key]])

    agent_write_list = sorted(agent_write_list, key=operator.itemgetter(1), reverse=True)
    agent_write_list.insert(0, header_row)

    # print(agent_write_list)
    return agent_dict, agent_write_list


def author_counter(metrics_file):
    author_dict = {}
    for row in metrics_file:
        if row['Author'] in author_dict.keys():
            author_dict[row['Author']] += 1
        else:
            author_dict[row['Author']] = 1

    author_write_list = []
    header_row = ['Frontend Agent', 'Ticket Count']
    for key in author_dict:
        author_write_list.append([key, author_dict[key]])

    author_write_list = sorted(author_write_list, key=operator.itemgetter(1), reverse=True)
    author_write_list.insert(0, header_row)
    print(author_write_list)
    return author_dict, author_write_list


def category_counter(metrics_file):
    category_dict = {}
    for row in metrics_file:
        if row['Category'] in category_dict.keys():
            category_dict[row['Category']] += 1
        else:
            category_dict[row['Category'].strip()] = 1

    catcount_write_list = []
    header_row = ['Category', 'Tickets']
    for key in category_dict.keys():
        catcount_write_list.append([key, category_dict[key]])

    catcount_write_list = sorted(catcount_write_list, key=operator.itemgetter(1), reverse=True)
    catcount_write_list.insert(0, header_row)
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
        category_averages[key] = (statistics.mean(category_sla_dict[key])/60.0)


    catavg_write_list = []
    header_row = ['Category', 'Average SLA']
    for key in category_averages.keys():
        catavg_write_list.append([key, category_averages[key]])

    catavg_write_list = sorted(catavg_write_list, key=operator.itemgetter(1), reverse=True)
    catavg_write_list.insert(0, header_row)
    return category_averages, catavg_write_list


def find_weeks(start_date):
    # if 6 > start_date.weekday() > 0:
    week_start_day = start_date.day - start_date.weekday()
    # print(week_start_day)
    week_start = datetime.date(start_date.year, start_date.month, week_start_day)
    week_end = week_start + datetime.timedelta(days=6)

    print(week_start, week_end)
    return week_start, week_end


def week_trends(metrics_file, date_start, end_date, num_weeks):
    week_list = []
    i = 0
    while i < num_weeks:
        year, month, day = [int(chunk.strip()) for chunk in date_start.split("/")]
        start_date = datetime.datetime(year, month, day)
        start, end = find_weeks(start_date)
        week_list.append([start, end])

        start_date = end + datetime.timedelta(days=1)
        i += 1

    week_trend_list = {}
    for row in metrics_file:
        filed_dt = create_datetime(row['FullFiled'])
        filed = datetime.datetime(filed_dt[0], filed_dt[1], filed_dt[2])

        for week in week_list:
            if start <= filed <= end:
                if week_trend_list[week_list.index(week)] in week_trend_list.keys():
                    week_trend_list[week_list.index(week)] += 1
                else:
                    week_trend_list[week_list.index(week)] = 1
            else:
                continue

    print(week_trend_list)


    #  return week_trend_list -> [{'week_num':INT, 'week_range': 'mm/dd/yyyy - mm/dd/yyyy', 'count':INT}, ... ]



def write(to_write, write_range):
    api_caller.write(to_write, write_range)


def flags(raw_file, author, agent, catcount, cataverage, date_start, date_end, write_flag, weeks):

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
        for row in agent_write:
            print("{}: {}".format(row[0], row[1]))

        if write_flag:
            write_range = "Graphs!A:B"
            write(agent_write, write_range)  # add "range" value
            pass

    if author:
        author_dict, author_write = author_counter(metrics_dict)

        # print("Agent frequencies:")
        # for key in author_dict:
        #     print("{}: {}".format(key, author_dict[key]))

        if write_flag:
            write_range = "Graphs!D:E"
            write(author_write, write_range)  # add "range" value

    if catcount:
        category_dict, category_write = category_counter(metrics_dict)

        # print("Category frequencies:\n")
        # for key in category_dict.keys():
        #     print("{}: {}".format(key, category_dict[key]))

        if write_flag:
            write_range = "Graphs!G:H"
            write(category_write, write_range)   # add "range" value

    if cataverage:
        category_averages, catavg_write = category_average(metrics_dict)

        # print("Category averages:\n")
        # for item in category_averages.keys():
        #     print("{}: {}".format(item, category_averages[item]))

        if write_flag:
            write_range = "Graphs!J:K"
            write(catavg_write, write_range)  # add "range" value

    if weeks:
        # call week_trends to calculate weekly contact numbers
        #
        week_trends(metrics_dict, start_date, end_date, weeks)

@click.command()
@click.option('--author', help='Author Counter: count tickets filed by CRCS agents.', is_flag=True)
@click.option('--agent', help='Agent Counter: count tickets answered by Escalations agents.', is_flag=True)
@click.option('--catcount', help='Category Counter: count tickets in each category.', is_flag=True)
@click.option('--cataverage', help='Category Average: calculate average time-to-response per category.', is_flag=True)
@click.option('--weeks', help='Calculate week-over-week contact numbers? Requires INT '
                                    'for number of weeks to calculate.', nargs=1)
@click.option('--date_start', help='Start Date (format: MM/DD/YYY)', nargs=1)
@click.option('--date_end', help='End Date (format: MM/DD/YYY)', nargs=1)
@click.option('--write_flag', help='Boolean: write to Google Sheets?', is_flag=True)
def metrics(author, agent, catcount, cataverage, date_start, date_end, write_flag, weeks):
    raw_file = api_caller.read()
    flags(raw_file, author, agent, catcount, cataverage, date_start, date_end, write_flag, weeks)

metrics()