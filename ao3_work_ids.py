# Retrieve fic ids from an AO3 search
# Will return in searched order
# Saves ids to a csv for later use e.g. to retrieve fic text
# this is for python 2.7 

from bs4 import BeautifulSoup
import re
import time
import requests
import csv
import sys
import datetime

url = ""
num_requested_fic = 0
num_recorded_fic = 0
csv_name = ""

# 
# Ask the user for:
# a url of a works listed page
# e.g. 
# https://archiveofourown.org/works?utf8=%E2%9C%93&work_search%5Bsort_column%5D=word_count&work_search%5Bother_tag_names%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=&work_search%5Bcomplete%5D=0&commit=Sort+and+Filter&tag_id=Harry+Potter+-+J*d*+K*d*+Rowling
# https://archiveofourown.org/tags/Harry%20Potter%20-%20J*d*%20K*d*%20Rowling/works?commit=Sort+and+Filter&page=2&utf8=%E2%9C%93&work_search%5Bcomplete%5D=0&work_search%5Blanguage_id%5D=&work_search%5Bother_tag_names%5D=&work_search%5Bquery%5D=&work_search%5Bsort_column%5D=word_count
# how many fics they want
# what to call the output csv
# 
def get_user_params():
    global url
    global csv_name
    global num_requested_fic
    # user input the url
    while (url == ""):
        url = raw_input("What URL should we scrape? ")

    # how many fic?
    nqf = ""
    while (nqf == ""):
        nqf = raw_input("How many fic do you want? (for all, enter 'a')  " )

    if nqf == "a":
        num_requested_fic = -1
    else:
        num_requested_fic = int(nqf)

    while (csv_name == ""):
        csv_name = raw_input("What should we call the output csv? ")

# 
# navigate to a works listed page,
# then extract all work ids
# 
def get_ids():
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    # some responsiveness in the "UI"
    sys.stdout.write('.')
    sys.stdout.flush()
    works = soup.find_all(class_="work blurb group")
    ids = []
    for tag in works:
        t = tag.get('id')
        t = t[5:]
        ids.append(t)
    return ids

# 
# update the url to move to the next page
# note that if you go too far, ao3 won't error, 
# but there will be no works listed
# 
def update_url_to_next_page():
    global url
    key = "page="
    start = url.find(key)

    # there is already a page indicator in the url
    if (start is not -1):
        # find where in the url the page indicator starts and ends
        page_start_index = start + len(key)
        page_end_index = url.find("&", page_start_index)
        # if it's in the middle of the url
        if (page_end_index is not -1):
            page = int(url[page_start_index:page_end_index]) + 1
            url = url[:page_start_index] + str(page) + url[page_end_index:]
        # if it's at the end of the url
        else:
            page = int(url[page_start_index:]) + 1
            url = url[:page_start_index] + str(page)

    # there is no page indicator, so we are on page 1
    else:
        # there are other modifiers
        if (url.find("?") is not -1):
            url = url + "&page=2"
        # there an no modifiers yet
        else:
            url = url + "?page=2"


# 
# after every page, write the gathered ids
# to the csv, so a crash doesn't lose everything.
# include the url where it was found,
# so an interrupted search can be restarted
# 
def write_ids_to_csv(ids):
    global num_recorded_fic
    with open(csv_name + ".csv", 'a') as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        for id in ids:
            if (not_finished()):
                wr.writerow([id, url])
                num_recorded_fic = num_recorded_fic + 1
            else:
                break

# 
# if you want everything, you're not done
# otherwise compare recorded against requested.
# recorded doesn't update until it's actually written to the csv
# 
def not_finished():
    if (num_requested_fic == -1):
        return True
    else:
        if (num_recorded_fic < num_requested_fic):
            return True
        else:
            return False

# 
# include a text file with the starting url,
# and the number of requested fics
# 
def make_readme():
    with open(csv_name + "_readme.txt", "w") as text_file:
        text_file.write("url: " + url + "\n" + "num_requested_fic: " + str(num_requested_fic) + "\n" + "retreived on: " + str(datetime.datetime.now()))


def main():
    get_user_params()
    make_readme()
    while(not_finished()):
        # 5 second delay between requests as per AO3's terms of service
        time.sleep(5)
        ids = get_ids()
        # if the current page is empty, you've run out of fic
        if (len(ids) is 0):
            break
        write_ids_to_csv(ids)
        update_url_to_next_page()
    print "That's all, folks"


main()
