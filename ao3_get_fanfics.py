######
#
# This script takes in (a list or csv of) fic IDs and
# writes a csv containing the fic itself, as well as the 
# metadata.
#
# Usage - python ao3_get_fanfics.py ID [--header header] [--csv csvoutfilename] 
#
# ID is a required argument. It is either a single number, 
# multiple numbers seperated by spaces, or a csv filename where
# the IDs are the first column.
# (It is suggested you run ao3_work_ids.py first to get this csv.)
#
# --header is an optional string which specifies your HTTP header
# for ethical scraping. For example, the author's would be 
# 'Chrome/52 (Macintosh; Intel Mac OS X 10_10_5); Jingyi Li/UC Berkeley/email@address.com'
# If left blank, no header will be sent with your GET requests.
# 
# --csv is an optional string which specifies the name of your
# csv output file. If left blank, it will be called "fanfics.csv"
# Note that by default, the script appends to existing csvs instead of overwriting them.
#
# Author: Jingyi Li soundtracknoon [at] gmail
# I wrote this in Python 2.7. 9/23/16
#
#######

import requests
from bs4 import BeautifulSoup
import argparse
import time
import os
import csv

def get_tag_info(category, meta):
	'''
	given a category and a 'work meta group, returns a list of tags (eg, 'rating' -> 'explicit')
	'''
	try:
		tag_list = meta.find("dd", class_=str(category) + ' tags').find_all(class_="tag")
	except AttributeError as e:
		return []
	return [result.text.encode('ascii', 'ignore') for result in tag_list] 
	
def get_stats(meta):
	'''
	returns a list of  
	language, published, status, date status, words, chapters, comments, kudos, bookmarks, hits
	'''
	categories = ['language', 'published', 'status', 'words', 'chapters', 'comments', 'kudos', 'bookmarks', 'hits'] 

	stats = list(map(lambda category: meta.find("dd", class_=category), categories))

	if not stats[2]:
		stats[2] = stats[1] #no explicit completed field -- one shot
	try:		
		stats = [stat.text for stat in stats]
	except AttributeError as e: #for some reason, AO3 sometimes miss stat tags (like hits)
		new_stats = []
		for stat in stats:
			if stat: new_stats.append(stat.text)
			else: new_stats.append('null')
		stats = new_stats

	stats[0] = stats[0].rstrip().lstrip() #language has weird whitespace characters
	#add a custom completed/updated field
	status  = meta.find("dt", class_="status")
	if not status: status = 'Completed' 
	else: status = status.text.strip(':')
	stats.insert(2, status)
	stats = list(map(lambda s: s.encode('ascii', 'ignore'), stats))
	
	return stats      

def get_tags(meta):
	'''
	returns a list of lists, of
	rating, category, fandom, pairing, characters, additional_tags
	'''
	tags = ['rating', 'category', 'fandom', 'relationship', 'character', 'freeform']
	return list(map(lambda tag: get_tag_info(tag, meta), tags))

def write_fic_to_csv(fic_id, writer, header_info=''):
	'''
	fic_id is the AO3 ID of a fic, found every URL /works/[id].
	writer is a csv writer object
	the output of this program is a row in the CSV file containing all metadata 
	and the fic content itself.
	header_info should be the header info to encourage ethical scraping.
	'''
	print('Scraping ', fic_id)
	url = 'http://archiveofourown.org/works/'+str(fic_id)+'?view_adult=true&amp;view_full_work=true'
	headers = {'user-agent' : header_info}
	req = requests.get(url, headers=headers)
	src = req.text
	soup = BeautifulSoup(src, 'html.parser')
	meta = soup.find("dl", class_="work meta group")
	tags = get_tags(meta)
	stats = get_stats(meta)
	#get the fic itself
	content = soup.find("div", id= "chapters")
	chapters = content.select('p')
	chaptertext = '\n\n'.join([chapter.text for chapter in chapters]).encode('ascii', 'ignore')
	row = list(map(lambda x: ', '.join(x), tags)) + stats + [chaptertext]
	writer.writerow(row)
	print('Done.')
	
def get_args(): 
	parser = argparse.ArgumentParser(description='Scrape and save some fanfic, given their AO3 IDs.')
	parser.add_argument(
		'ids', metavar='IDS', nargs='+',
		help='a single id, a space seperated list of ids, or a csv input filename')
	parser.add_argument(
		'--csv', default='fanfics.csv',
		help='csv output file name')
	parser.add_argument(
		'--header', default='',
		help='user http header')
	args = parser.parse_args()
	fic_ids = args.ids
	is_csv = (len(fic_ids) == 1 and '.csv' in fic_ids[0]) 
	csv_out = str(args.csv)
	headers = str(args.header)
	return fic_ids, csv_out, headers, is_csv

def main():
	fic_ids, csv_out, headers, is_csv = get_args()
	os.chdir(os.getcwd())
	with open(csv_out, 'a') as f_out:
		writer = csv.writer(f_out)
		#does the csv already exist? if not, let's write a header row.
		if os.stat(csv_out).st_size == 0:
			print('Writing a header.')
			header = ['rating', 'category', 'fandom', 'relationship', 'character', 'additional tags', 'language', 'published', 'status', 'status date', 'words', 'chapters', 'comments', 'kudos', 'bookmarks', 'hits', 'body']
			writer.writerow(header)

		if is_csv:
			csv_fname = fic_ids[0]
			with open(csv_fname, 'r+') as f_in:
				reader = csv.reader(f_in)
				for row in reader:
					write_fic_to_csv(row[0], writer)
					time.sleep(1)
		else:
			for fic_id in fic_ids:
				write_fic_to_csv(fic_id, writer)
				time.sleep(1)

main()