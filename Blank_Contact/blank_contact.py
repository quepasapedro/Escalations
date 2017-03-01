__author__ = 'peterking'

import sys
import csv
import random
import datetime
import json


def create_reader(blank_file, args):

    #### SOMEDAY ADD DATE LOGIC HERE

    with open(blank_file) as file:
        reader = csv.DictReader(file, delimiter=',')
        blank_dict = list(reader)

    rand_dict = random.sample(blank_dict, 160)

    return rand_dict #blank_dict


def count_categories(blank_dict):

    category_dict = {}

    for row in blank_dict:
        if row['Category'] in category_dict.keys():
            category_dict[row['Category']] += 1
        elif row['Category'] not in category_dict.keys():
            category_dict[row['Category'].strip()] = 1

    return category_dict


def split_categories(category_dict):

    # def randomize_agents():
    #     agents = ['Peter', 'Kendra', 'Michael', 'Nick']
    #     agent_keys = {1: '', 2: '', 3: '', 4: ''}
    #     nums = list(range(1,5))
    #
    #     for agent in agents:
    #         pick = random.choice(nums)
    #         agent_keys[pick] = agent
    #         nums.remove(pick)
    #
    #     return agents

    agent_list = ['Peter', 'Kendra', 'Michael', 'Nick']
    assignments = {'Peter': [], 'Kendra': [], 'Nick': [], 'Michael': []}
    ticket_count = {'Peter': 0, 'Kendra': 0, 'Nick': 0, 'Michael': 0}

    total = 0
    for value in category_dict.values():
        total += value
    print(total)

    for category in category_dict.keys():

        agent = random.choice(agent_list)
        if ticket_count[agent] >= total/3:
            agent_list.remove(agent)
        elif ticket_count[agent] < total/3:
            append_dict = {category: category_dict[category]}
            assignments[agent].append(append_dict)
            ticket_count[agent] += category_dict[category]

        # DEPRECATED CODE
        # if agent_index < len(agent_dict):
        #     if ticket_count[agent_dict[agent_index]] >= total/4:
        #         del(agent_dict[agent_index])
        #         agent_index += 1
        #     else:
        #         assignments[agent_dict[agent_index]].append(category)
        #         ticket_count[agent_dict[agent_index]] += category_dict[category]
        #         agent_index += 1
        #
        # elif agent_index == len(agent_dict):
        #     if ticket_count[agent_dict[agent_index]] >= total/4:
        #         del(agent_dict[agent_index])
        #         agent_index = 1
        #     else:
        #         assignments[agent_dict[agent_index]].append(category)
        #         ticket_count[agent_dict[agent_index]] += category_dict[category]
        #         agent_index = 1
    json_assignments = json.dumps(assignments, separators=(',', ':'), indent=04)

    print(json_assignments)
    print(ticket_count)


bca_file = "sample_blank_contact.csv"
args = sys.argv

blank_dict = create_reader(bca_file, args)

category_count = count_categories(blank_dict)

split_categories(category_count)
# for item in category_count.keys():
#     print("{}: {}".format(item, category_count[item]))

# split_categories(category_count)