from bs4 import BeautifulSoup
import requests
import smtplib
import sys
from email.mime.text import MIMEText
from vars import *

if len(sys.argv) != 2:
    print('Usage: python DealScraper.py search_term_set')
    print('Current search_term_sets available:\n')
    for term in terms.keys():
        print(term)
    print('all - for all search terms')
    quit()
elif sys.argv[1] == 'all':
    terms['all'] = sum(terms.values(), [])
    print('Using all sets: ' + ', '.join(terms.keys()) + ', ' + str(terms.get(sys.argv[1])))
elif not terms.get(sys.argv[1]):
    print('Search term set "' + sys.argv[1] + '" not found.')
    print('Current sets: ' + ', '.join(terms.keys()))
    quit()
else:
    print('Using set: ' + sys.argv[1] + ', ' + str(terms.get(sys.argv[1])))

page = 1
base = 'https://forums.redflagdeals.com'
prependUrl = 'https://forums.redflagdeals.com/hot-deals-f9/'
url = prependUrl + str(page)
matches = []
pages = []

maxPagesRequest = requests.get(url, headers={"User-Agent": "Mozilla Firefox"})
maxPagesSoup = BeautifulSoup(maxPagesRequest.text, 'html5lib')
maxPages = int(maxPagesSoup.find(class_='pagination_menu_trigger').text.split()[-1])

while page <= maxPages:
    print('Parsing page ' + str(page) + '...')
    response = requests.get(url, headers={"User-Agent": "Mozilla Firefox"})
    if response.status_code != 200:
        print('Error! Response status ' + str(response.status_code))
        break

    soup = BeautifulSoup(response.text, 'html5lib')
    links = soup.findAll(class_='topic_title_link')

    for term in terms.get(sys.argv[1]):
        for link in links:
            if term in link.text.strip():
                if link.text.strip() not in matches:
                    matches.append(link.text.strip())
                    pages.append({"text": link.text.strip(), "url": base + link['href']})
        
    page += 1
    url = prependUrl + str(page)

print('Pages scraped: ' + str(page) + ", " + str(len(matches)) + " matches\n")

if len(matches) > 0:
    print('Creating Server')
    server = smtplib.SMTP_SSL('smtp.gmail.com')
    print('Logging in...')
    server.login(sender, password)
    print('Constructing Message...')

    htmlList = """\
    <ul>
    """
    for page in pages:
        htmlList += """\
            <li>
                <a href="$(url)">$(text)</a>
            </li>
        """
        htmlList = htmlList.replace("$(url)", page['url'])
        htmlList = htmlList.replace("$(text)", page['text'])

    htmlList += """\
    </ul>
    """

    body = """\
    <html>
        <body>
            <p>Here's a list of interesting deals</p>
            $(htmlList)
        </body>
    </html>
    """

    body = body.replace("$(htmlList)", htmlList)
    msg = MIMEText(body, 'HTML')

    msg['Subject'] = "Found some Deals!"
    msg['From'] = sender
    msg['To'] = receiver

    print('Sending Message...')
    server.sendmail(sender, [receiver], msg.as_string())
    print('Message Sent!')
    server.quit()
else:
    print('No matches today :(')    

print('Program terminated.')
