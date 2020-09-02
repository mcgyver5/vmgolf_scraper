# visit vimgolf.com
# open each challenge, read the dates in the column on the right.  pick the earliest date.  That is the date of the challenge
# record the link to the challenge (https://www.vimgolf.com/challenges/5c645526fa8ae200061757ad)
# record #1 top golfer
# record number of active golfers and number of entries
# record number of keystrokes
# record user who submitted it.
# put recorded data into SQL Table
# at bottom of page use number links to go to next page
# feature +  allow me to see the challenges I haven't tried yet
# + allow me to see the challenges I have tried but haven't finished
# option to filter out those who have used <C-LEFT> or LEFT or <S-LEFT> in their answers.
import sqlite3

import requests
import time
from bs4 import BeautifulSoup

def is_done(vimgolf_user):
    # returns a list of challenge IDs that vimgolf_user has participated in
    url = "https://vimgolf.com/{}".format(vimgolf_user)
    response = requests.get(url)
    soup = BeautifulSoup(response.content,"html.parser")
    h5s = soup.find_all("h5", {"class": "challenge"})
    url_set = []
    for h5 in h5s:
        anchor = h5.find("a")
        url_address = anchor['href']

        hash12 = url_address[12:]
        url_set.append(hash12)

    return url_set

def dig_date(soup_bone):
    notice_divs = soup_bone.find_all("div", {"class": "notice clearfix"})
    winner = notice_divs[0]
    date_em = winner.find_all("em")
    challenge_date = date_em[0].text
    date_parts = challenge_date.split(" ")
    date_string = date_parts[0]
    parts = date_string.split("/")
    form_date = parts[2] + "-" + parts[0] + "-" + parts[1]
    return form_date

def dig_winner(winner):
    anchors = winner.find_all("a")
    user = anchors[1].text
    return user

def dig_creator(some_html):
    h5_tags = soup.find_all("h5")
    for h5 in h5_tags:
        if "Created by: " in h5:
            anchor = h5.find("a")
            return anchor.text

def dig_min(soup):
    notice_divs = soup.find_all("div", {"class": "notice clearfix"})
    winner = notice_divs[0]
    score_tag = winner.find("b")
    return score_tag.text
    
def dig_max(some_html):
    success_divs = soup.find_all("div", {"class":"success clearfix"})
    nonwinner = success_divs[-1]
    b_tags = nonwinner.find_all("b")
    score_tag = b_tags[1]
    score_split = score_tag.text.split(" ")
    score = score_split[1]
    return score

def get_headers():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    referrer = "http://www.vimgolf.com"
    headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'referer': 'https://www.vimgolf.com/',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'accept-language': 'en-US,en;q=0.9'
    }
    return headers
def dig_entries(some_html):
    stats = soup.findAll("b", {"class": "stat"})
    golfers = stats[0].text
    entries = stats[1].text
    return entries

def get_href_dict(soup):
    
    href_dict = {}
    h5_tags = soup.find_all('h5')
    for h5_tag in h5_tags:
        anchors = h5_tag.find_all('a')
        first_anchor = anchors[0]
        link_text = first_anchor.text
        link_address = first_anchor['href']
        hash12 = link_address[12:]
        href_dict[hash12] = link_text
    return href_dict

def get_pages(start_url, soup):
    page_list = []
    pages = soup.find_all("span", {"class": "page"})
    for page in pages:
        anchor = page.find('a')
        if anchor == None:
            print("none")
        else:
            page_url = anchor['href']
            page_list.append(start_url + page_url)
    return page_list

def capture_challenges(soup):

    try:
        conn = sqlite3.connect("vimgolf.db")
        c = conn.cursor()
        href_dict = get_href_dict(soup)
        done = 0
        for h in href_dict:
            full_url = "https://www.vimgolf.com/challenges/" + h
            resp = requests.get(full_url, headers=req_headers)
            time.sleep(0.05)
            soup1 = BeautifulSoup(resp.content, 'html.parser')
            if h in finished_challs:
                print("{} is in finished challenges".format(h))
                done = 1
            notice_divs = soup1.find_all("div", {"class": "notice clearfix"})
            winner = notice_divs[0]
            entries = dig_entries(soup1)
            winner = dig_winner(winner)
            creator = dig_creator(soup1)
            title = href_dict[h]
            min_keys = dig_min(soup1)
        #    max_keys = dig_max(soup)
            max_keys = 100
            ch_date = dig_date(soup1)
            sql = "insert into vg_challenges values (:h, :entries, :create_date, :winner, :min_keys, :max_keys, :creator, :title, :done)"
            c.execute(sql, {'h':h, 'entries':entries, 'create_date':ch_date,'winner':winner,'min_keys':min_keys, 'max_keys':max_keys, 'creator':creator, 'title':title, 'done':done})
            conn.commit()
            done = 0
        c.close()
        conn.close()
    except Exception as e:
        print("error")
        print(e)
                                                             
                                                                                    
start_url = "https://www.vimgolf.com"
finished_challs = is_done("mcguire")
req_headers = get_headers()
response = requests.get(start_url, headers=req_headers)

soup = BeautifulSoup(response.content, 'html.parser')
capture_challenges(soup)
all_pages = get_pages(start_url,soup)
count = 0
done = 0
for page_url in all_pages:
    count = count + 1
    print(page_url)
    response = requests.get(page_url, headers=req_headers)
    soup = BeautifulSoup(response.content, 'html.parser') 
    capture_challenges(soup)
    if count > 2:
        break
