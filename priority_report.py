from jira import JIRA
import os
import sys
from dotenv import load_dotenv
from datetime import date
import pandas as pd
from tabulate import tabulate
import requests
import numpy as np

def dotloader():
    load_dotenv()
    jira_user = os.getenv('JIRA_USER')
    jira_pass = os.getenv('JIRA_PASS')
    slack_add = os.getenv('PRI_SLACK')
    
    return jira_user, jira_pass, slack_add

def authorise(user, password):
    data_dict = {}

    jira = "https://grit-jira.sanger.ac.uk"
    auth_jira = JIRA(jira, basic_auth=(user, password))
    projects = auth_jira.search_issues(f'project IN ("GRIT","RC") AND status NOT IN ("Submitted", "Done", "Cancelled")',
                                        maxResults=10000)
    result_list = ''
    if len(projects) >= 1:
        for i in projects:
            issue = auth_jira.issue(f'{i}')
            level = issue.fields.priority
            issuen = str(issue)
            stat = str(issue.fields.status)
            if str(level) in 'High' or str(level) in 'Highest':
                key = str(issue.fields.customfield_10201)
                data_dict[key] = {'Ticket_id':issuen,
                                    'Priority Level': str(issue.fields.priority),
                                    'Status': stat,
                                    'Assignee': str(issue.fields.assignee)}

    return data_dict

def convert_to_df(ticket_dict):
    return pd.DataFrame.from_dict(ticket_dict).T

def tabulate_df(df):
    return tabulate(df, tablefmt = "grid", headers=['Organism', 'Ticket ID', 'Priority Level', 'Status', 'Assignee'])

def post_it(p_df, token, counter):
    headers = {
        'Content-Type': 'application/json',
            }

    data = '{"text":' + "'Report **" + str(counter) + "** for: " + str(date.today().strftime('%d-%b-%Y')) + " \n ```" + str(p_df) + "```'" + '}'

    res = requests.post(token, headers=headers, data=data)
    print(res)

def main():
    user, passw, slack_add = dotloader()
    message = authorise(user, passw)
    df = convert_to_df(message)

    df['Assignee'].replace('None', 'Waiting on Assignment', inplace=True)
    df.sort_values(['Assignee'], axis=0, inplace=True)
    
    counter = 0
    df_list = np.vsplit(df, round(len(df) / 15))
    for i in df_list:
        counter += 1
        prettier_df = tabulate_df(i)
        post_it(prettier_df, slack_add, counter)

if __name__ == '__main__':
    main()
