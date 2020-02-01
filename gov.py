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

def allVotes(hyperlink):
    raw_html = simple_get(hyperlink)
    html = BeautifulSoup(raw_html, 'html.parser')
    votes = html.findAll('span', attrs={'class': 'contenttext'})

def allVotes(hyperlink):
    raw_html = simple_get(hyperlink)
    html = BeautifulSoup(raw_html, 'html.parser')
    links = html.findAll('a')
    li = []
    for l in links:
        link =l.get('href')
        if link != None and link[:16] == '/legislative/LIS':
            li.append('https://www.senate.gov/' + link)
    return li

def voteCounter(hyperlink):
    #Setup
    raw_html = simple_get(hyperlink)
    html = BeautifulSoup(raw_html, 'html.parser')

    #Question Name
    question = html.find('div', attrs={"style": "padding-bottom:10px;"})
    question = question.text.strip()[10:].split()
    ques = ''
    for q in question:
            ques = ques + ' ' + q

    #Measure Number
    measure = html.find('div', attrs={'class': 'contenttext', "style": "padding-bottom:10px;"})
    meas = ''
    if measure:
        measure = measure.text.strip().split()[2:]
        for m in measure:
            meas = meas + ' ' + m
    else:
        meas = "Motion"

    #votes
    votes = html.find('span', attrs={'class': 'contenttext'})
    votes = votes.text.strip().split()
    iter_votes = iter(votes)

    #date
    date = html.findAll('div', attrs={"style": "float:left; min-width:200px; padding-bottom:10px;", 'class': 'contenttext'})
    da = []
    for d in date:
        da.append(d.text.strip())
    date = da[1][11:]

    #writing
    with open('votes.csv', 'a') as csv_file:
        writer = csv.writer(csv_file)
        #for each one write
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
                writer.writerow([name, party, state, ques, meas, date, vote])
            except:
                break
            
if __name__== "__main__":
    links = allVotes('https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_116_2.htm')
    with open('votes.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Name', 'Party', 'State', 'Question', 'Measure', 'Date', 'Vote'])
    for l in links:
        voteCounter(l)
