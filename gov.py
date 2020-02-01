from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import csv

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

#Setup
raw_html = simple_get('https://www.senate.gov/legislative/LIS/roll_call_lists/roll_call_vote_cfm.cfm?congress=116&session=2&vote=00001')
html = BeautifulSoup(raw_html, 'html.parser')

#Measure Number
measure = html.find('div', attrs={'class': 'contenttext', "style": "padding-bottom:10px;"})
measure = measure.text.strip()
measure = measure.split()
measure = measure[2:]
meas = ''
for m in measure:
    meas = meas + ' ' + m

#votes
votes = html.find('span', attrs={'class': 'contenttext'})
votes = votes.text.strip()
votes = votes.split()
iter_votes = iter(votes)

#date
date = html.findAll('div', attrs={"style": "float:left; min-width:200px; padding-bottom:10px;", 'class': 'contenttext'})
da = []
for d in date:
    da.append(d.text.strip())
date = da[1][11:]

#writing
with open('votes.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Name', 'Party', 'State', 'Measure', 'Date', 'Vote'])
    for i in range(len(votes)//3):
        try:
            name = next(iter_votes)
            party = next(iter_votes)
            if party[0] != '(':
                name= name + ' ' + party
                party = next(iter_votes)
            state = party[3:5]
            party = party[1]
            vote = next(iter_votes)
            writer.writerow([name, party, state, meas, date, vote])
        except:
            break
        
