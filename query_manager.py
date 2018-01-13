import read
import json
from bs4 import BeautifulSoup

# frontend should make sure that only directors and organizers can run aggregation queries - other events should just include hacker info to query based on

def run_query(event, context):
    table_data = [[cell.text for cell in row('td')] for row in BeautifulSoup(event['html_data'])('tr')]

    return read.read_info(json.dumps(dict(table_data)), context['role'])

