from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import csv
import time

buffer = []

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

def runPage(hyperlink):
    raw_html = simple_get(hyperlink)
    soup = BeautifulSoup(raw_html, 'html.parser')
    topnum = soup.find('span', attrs={"style": "display:none"})
    topnum = topnum.text.strip()
    topnum = int(topnum[1:-1])
    return topnum

def runSingleVote(hyperlink):
    #Setup
    print(hyperlink)
    t = 0
    raw_html = 0
    soup = 0
    try:
        raw_html = simple_get(hyperlink)
        soup = BeautifulSoup(raw_html, 'html.parser')

        #Question Name
        question = soup.find('div', attrs={"style": "padding-bottom:10px;"})
        question = question.text.strip()[10:].split()
        ques = ''
        for q in question:
                ques = ques + ' ' + q
        if hyperlink in buffer:
            buffer.remove(hyperlink)
    except:
        print('no')
        buffer.append(hyperlink)
        return

    #Measure Number
    measure = soup.find('div', attrs={'class': 'contenttext', "style": "padding-bottom:10px;"})
    meas = ''
    if measure:
        measure = measure.text.strip().split()[2:]
        for m in measure:
            meas = meas + ' ' + m
        meas = meas.strip()
    else:
        meas = "Motion"

    #Measure URL
    urls = soup.findAll('a')
    url = ''
    for l in urls:
        u =l.get('href')
        if u != None and u[:4] == 'http':
            url = u
            break
    if url == '':
        url = "Motion"

    #find policy area
    policy = 'Motion'
    soupy = ''
    if url != 'Motion':
        soupy = BeautifulSoup(simple_get(url), 'html.parser')
        policy_area = soupy.findAll('div', attrs={'class': 'tertiary_section'})
        poli = []
        for p in policy_area:
            poli.append(p.text.strip())
        poli = poli[-1].split()
        poli = poli[4:-2]
        policy = ''
        for p in poli:
            policy = policy + ' ' + p
        policy = policy.strip()
    
    #title
    title = meas
    if url != "Motion":
        title = soupy.find('h1', attrs={'class': 'legDetail'})
        title = title.text.strip().split()
        titl = ''
        for t in range(len(title)):
            if title[t] == 'Congress':
                titl = title[:t]
                titl[t-1]= titl[t-1][:-5]
        title = ''
        for t in titl:
            title = title + ' ' + t
        title = title.strip()
    
        
    #votes
    votes = soup.find('span', attrs={'class': 'contenttext'})
    votes = votes.text.strip().split()
    iter_votes = iter(votes)

    #date
    date = soup.findAll('div', attrs={"style": "float:left; min-width:200px; padding-bottom:10px;", 'class': 'contenttext'})
    da = []
    for d in date:
        da.append(d.text.strip())
    date = da[1][11:]

    #category
    resTitle = title
    policyArea = policy
    category = ''
    if meas[:2] == 'PN':
        category = 'Presidential Nomination'
    elif resTitle.lower().find('impeachment') > 0:
        category = 'Impeachment of the President'
    else:
        category = policyArea

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
                writer.writerow([name, party, state, ques, meas, url, date, vote, category])
            except:
                break
            
def runYear(year):
    congress = (year - 1787)/2.0
    session = 1
    if congress != round(congress):
        session = 2
    congress = int(congress)
    senate_link = 'https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_' + str(congress) + '_' + str(session) + '.htm'
    largest_num = runPage(senate_link)
    with open('votes.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Name', 'Party', 'State', 'Question', 'Measure', 'URL', 'Date', 'Vote', 'Category'])
    for i in range(largest_num):
        num = str(i+1)
        time.sleep(2)
        while len(num) < 5:
            num = '0' + num
        runSingleVote("https://www.senate.gov//legislative/LIS/roll_call_lists/roll_call_vote_cfm.cfm?congress=" + str(congress) + "&session=" + str(session) + "&vote=" + num)
    while buffer:
        time.sleep(120)
        for hyperlink in buffer:
            runSingleVote(hyperlink)
            time.sleep(30)


def searchRep(state):
    with open('votes.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        info = [[] for i in range(8)]
        for row in csv_reader:
            if row[2] == state:
                for i in range(8):
                    info[i].append(row[i])
    with open('' + state + '_votes.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Name', 'Party', 'State', 'Question', 'Measure', 'URL', 'Date', 'Vote', 'Category'])
        for i in range(len(info[0])):
            r = []
            for j in info:
                r.append(j[i])
            writer.writerow(r)

if __name__== "__main__":
    runYear(2020)
