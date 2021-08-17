from jira import JIRA
import os
from dotenv import load_dotenv
from datetime import date


def dotloader():
    load_dotenv()
    jira_user = os.getenv('JIRA_USER')
    jira_pass = os.getenv('JIRA_PASS')
    if sys.argv[1] == True: 
        #slack_add1 = os.getenv('JOW_HOOK')
        #slack_add2 = os.getenv('CUR_HOOK')
        slack_add3 = os.getenv('DAM_HOOK')
    return jira_user, jira_pass, slack_add


def authorise(user, password):
    jira = "https://grit-jira.sanger.ac.uk"
    auth_jira = JIRA(jira, basic_auth=(user, password))
    projects = auth_jira.search_issues(f'project IN ("GRIT","RC") AND status NOT IN ("Submitted", "Done", "Cancelled")',
                                       maxResults=10000)
    result_list = ''
    if len(projects) >= 1:
        for i in projects:
            issue = auth_jira.issue(f'{i}')
            level = issue.fields.priority
            if str(issue).startswith('R'):
                issuen = str(issue) + ' \t'
            else:
                issuen = str(issue)
            if not str(issue.fields.status) == 'Decontamination':
                stat = str(issue.fields.status) + '\t\t\t\t'
            else:
                stat = str(issue.fields.status)
            if str(level) in 'High':
                result_list += f'| {issuen} |' \
                               f' {str(issue.fields.priority)} \t  |' \
                               f' {stat} |' \
                               f' {str(issue.fields.assignee)} |\n'
            elif str(level) in 'Highest':
                result_list += f'| {issuen} |' \
                               f' {str(issue.fields.priority)} |' \
                               f' {stat} |' \
                               f' {str(issue.fields.assignee)} |\n'

    return result_list


def make_json(result_list):

    message_package = '{"text":"\n' + \
                      f'|-------- Rovers Priority Report for {date.today()} --------|\n' + \
                      f'|========================================|\n' + \
                      f'{result_list}\n' + \
                      f'|========================================|\n' + \
                      f'|--------------- END Report for {date.today()} -------------|\n' + \
                      '"}'
    return message_package


def post_it(json, hook):
    os.popen(f"curl -X POST -H 'Content-type: application/json' --data '{json}' {hook}").read()


def main():
    user, passw, slack_add = dotloader()
    message = authorise(user, passw)
    new_message = make_json(message)
    post_it(new_message, slack_add)


if __name__ == '__main__':
    main()
