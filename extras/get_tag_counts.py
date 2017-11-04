'''
Count the number of fics in a list that have a particular tag 
(or any of its alternate tags as defined by AO3's tag wranglers)
'''

import os
from bs4 import BeautifulSoup
import re
import time
import requests
import csv
import sys
import datetime
import argparse


url = ""
input_csv_name = ""
output_csv_name = ""


def get_user_params():
	global url
	global input_csv_name
	global output_csv_name
	

	# e.g. https://archiveofourown.org/tags/Fluff
	parser = argparse.ArgumentParser(description='Extract metadata from a fic csv')
	parser.add_argument(
		'url', metavar='url', 
		help='the name of the url for the tag')
	parser.add_argument(
		'csv', metavar='csv', 
		help='the name of the csv with the base set of metadata')
	parser.add_argument(
		'out_csv', metavar='out_csv', 
		help='the name of the output csv')

	args = parser.parse_args()
	url = args.url
	input_csv_name = args.csv
	output_csv_name = args.out_csv


# work_id,title,author,rating,category,fandom,relationship,character,additional tags,language,published,status,status date,words,chapters,comments,kudos,bookmarks,hits
def contains_tag(row, tags):
	for tag in tags:
		if tag in row[6] or tag in row[7] or tag in row[8]:
			return True
	return False

def get_tag_equivalencies():
	req = requests.get(url)
	soup = BeautifulSoup(req.text, "lxml")
	synonyms = soup.find(class_="synonym listbox group")
	lis = synonyms.find_all("li")
	# get primary tag name
	tags = [soup.find(class_="primary header module").find("h2").string]
	# get all the synonyms
	for l in lis:
		tags.append(l.string)
	return tags

def main():
	csv.field_size_limit(1000000000)  # up the field size because stories are long
	get_user_params()
	
	tags = get_tag_equivalencies()
	count = 0

	with open(input_csv_name, 'rb') as incsv:
		with open(output_csv_name, 'a') as outcsv:
			rd = csv.reader(incsv, delimiter=',', quotechar='"')
			wr = csv.writer(outcsv, delimiter=',', quotechar='"')
			#skip first line
			rd.next()
			for row in rd:
				if contains_tag(row, tags):
					count = count + 1
					wr.writerow(row)

	print count

main()