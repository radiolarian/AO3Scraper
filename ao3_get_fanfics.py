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
# --resume is an optional flag which will skip over IDs in the csv output and error files
# when used in combination with a csv input
#
# --bookmarks is an optional flag which collects the users who have bookmarked a fic.
# Because this is a slow operation, it is excluded by default.
#
# --firstchap is an optional flag which, when set, only pulls the first chapter instead
# of all chapters.
#
# --metadata-only is an optional flag which pulls the metadata but not the content.
# default is off (i.e. default includes the fic contents). This also implies --firstchap
#
# Author: Jingyi Li soundtracknoon [at] gmail
# I wrote this in Python 2.7. 9/23/16
# Updated 2/13/18 (also Python3 compatible)
#
#
# Update 2/3/21
# jack-debug
# I added a new argument that only gets fanfics of a certain language
# --lang
#######
import requests
from bs4 import BeautifulSoup
import argparse
import time
import os
import csv
import sys
from unidecode import unidecode

# seconds to wait between page requests
delay = 5

def get_tag_info(category, meta):
	'''
	given a category and a 'work meta group, returns a list of tags (eg, 'rating' -> 'explicit')
	'''
	try:
		tag_list = meta.find("dd", class_=str(category) + ' tags').find_all(class_="tag")
	except AttributeError as e:
		return []
	return [unidecode(result.text) for result in tag_list] 
	
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
		stats = [unidecode(stat.text) for stat in stats]
	except AttributeError as e: #for some reason, AO3 sometimes miss stat tags (like hits)
		new_stats = []
		for stat in stats:
			if stat: new_stats.append(unidecode(stat.text))
			else: new_stats.append('null')
		stats = new_stats

	stats[0] = stats[0].rstrip().lstrip() #language has weird whitespace characters
	#add a custom completed/updated field
	status  = meta.find("dt", class_="status")
	if not status: status = 'Completed' 
	else: status = status.text.strip(':')
	stats.insert(2, status)

	return stats      

def get_tags(meta):
	'''
	returns a list of lists, of
	rating, category, fandom, pairing, characters, additional_tags
	'''
	tags = ['rating', 'category', 'fandom', 'relationship', 'character', 'freeform']
	return list(map(lambda tag: get_tag_info(tag, meta), tags))

# get kudos
def get_kudos(meta):
	if (meta):
		users = []
		## hunt for kudos' contents
		kudos = meta.contents

		# extract user names
		for kudo in kudos:
			if kudo.name == 'a':
				if 'more users' not in kudo.contents[0] and '(collapse)' not in kudo.contents[0]:
					users.append(kudo.contents[0])
		
		return users
	return []

# get author(s)
def get_authors(meta):
	tags = meta.contents
	authors = []

	for tag in tags:
		if tag.name == 'a':
			authors.append(tag.contents[0])

	return authors

# get bookmarks by page
def get_bookmarks(url, header_info):
	bookmarks = []
	headers = {'user-agent' : header_info}

	req = requests.get(url, headers=headers)
	src = req.text

	time.sleep(delay)
	soup = BeautifulSoup(src, 'html.parser')

	sys.stdout.write('scraping bookmarks ')
	sys.stdout.flush()

	# find all pages
	if (soup.find('ol', class_='pagination actions')):
		pages = soup.find('ol', class_='pagination actions').findChildren("li" , recursive=False)
		max_pages = int(pages[-2].contents[0].contents[0])
		count = 1

		sys.stdout.write('(' + str(max_pages) + ' pages)')
		sys.stdout.flush()

		while count <= max_pages:
			# extract each bookmark per user
			tags = soup.findAll('h5', class_='byline heading')
			bookmarks += get_users(tags)

			# next page
			count+=1
			req = requests.get(url+'?page='+str(count), headers=headers)
			src = req.text
			soup = BeautifulSoup(src, 'html.parser')
			sys.stdout.write('.')
			sys.stdout.flush()
			time.sleep(delay)
	else:
		tags = soup.findAll('h5', class_='byline heading')
		bookmarks += get_users(tags)

	print('')
	return bookmarks

# get users form bookmarks	
def get_users (meta):
	users = []
	for tag in meta:
			user = tag.findChildren("a" , recursive=False)[0].contents[0]
			users.append(user)

	return users
	
def access_denied(soup):
	if (soup.find(class_="flash error")):
		return True
	if (not soup.find(class_="work meta group")):
		return True
	return False

def write_fic_to_csv(fic_id, only_first_chap, lang, include_bookmarks, metadata_only, writer, errorwriter, header_info=''):
	'''
	fic_id is the AO3 ID of a fic, found every URL /works/[id].
	writer is a csv writer object
	the output of this program is a row in the CSV file containing all metadata
	and the fic content itself (excludes content if metadata_only=True).
	header_info should be the header info to encourage ethical scraping.
	'''
	print('Scraping ', fic_id)
	url = 'http://archiveofourown.org/works/'+str(fic_id)+'?view_adult=true'
	if not (only_first_chap or metadata_only):
		url = url + '&amp;view_full_work=true'
	headers = {'user-agent' : header_info}
	status = 429
	while 429 == status:
		req = requests.get(url, headers=headers)
		status = req.status_code
		if 429 == status:
			error_row = [fic_id] + ["Status: 429"]
			errorwriter.writerow(error_row)
			print("Request answered with Status-Code 429")
			print("Trying again in 1 minute...")
			time.sleep(60)

	if 400 <= status:
		print("Error scraping ", fic_id, "Status ", str(status))
		error_row = [fic_id] + [status]
		errorwriter.writerow(error_row)
		return

	src = req.text
	soup = BeautifulSoup(src, 'html.parser')
	if (access_denied(soup)):
		print('Access Denied')
		error_row = [fic_id] + ['Access Denied']
		errorwriter.writerow(error_row)
	else:
		meta = soup.find("dl", class_="work meta group")
		author = get_authors(soup.find("h3", class_="byline heading"))
		tags = get_tags(meta)
		stats = get_stats(meta)
		title = unidecode(soup.find("h2", class_="title heading").string).strip()
		visible_kudos = get_kudos(soup.find('p', class_='kudos'))
		hidden_kudos = get_kudos(soup.find('span', class_='kudos_expanded hidden'))
		all_kudos = visible_kudos + hidden_kudos

		if lang != False and lang != stats[0]:
			print('Fic is not in ' + lang + ', skipping...')
		else:
			#get bookmarks
			if (include_bookmarks):
				bookmark_url = 'http://archiveofourown.org/works/'+str(fic_id)+'/bookmarks'
				all_bookmarks = get_bookmarks(bookmark_url, header_info)
			else:
				all_bookmarks = []
			#get the fic itself
			if not metadata_only:
				content = soup.find("div", id= "chapters")
				chapters = content.select('p')
				chaptertext = '\n\n'.join([unidecode(chapter.text) for chapter in chapters])
			else:
				chaptertext = ""
			row = [fic_id] + [title] + [author] + list(map(lambda x: ', '.join(x), tags)) + stats + [all_kudos] + [all_bookmarks] + [chaptertext]
			try:
				writer.writerow(row)
			except:
				print('Unexpected error: ', sys.exc_info()[0])
				error_row = [fic_id] +  [sys.exc_info()[0]]
				errorwriter.writerow(error_row)
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
	parser.add_argument(
		'--resume', action='store_true',
		help='resume script and skip over already processed fics')
	parser.add_argument(
		'--firstchap', default='', 
		help='only retrieve first chapter of multichapter fics')
	parser.add_argument(
		'--lang', default='', 
		help='only retrieves fics of certain language (e.g English), make sure you use correct spelling and capitalization or this argument will not work')
	parser.add_argument(
		'--bookmarks', action='store_true',
		help='retrieve bookmarks; ')
	parser.add_argument(
		'--metadata-only', action='store_true',
		help='only retrieve metadata')
	args = parser.parse_args()
	fic_ids = args.ids
	csv_out = str(args.csv)
	headers = str(args.header)
	resume = args.resume
	ofc = str(args.firstchap)
	lang = str(args.lang)
	include_bookmarks = args.bookmarks
	metadata_only = args.metadata_only
	if ofc != "":
		ofc = True
	else:
		ofc = False
	if lang == "":
		lang = False
	return fic_ids, csv_out, headers, resume, ofc, lang, include_bookmarks, metadata_only

'''

'''
def generate_fic_ids(fic_ids, resume, csv_out, errors_out):
	# check csv_out and errors_out for any processed IDs.
	# technically this will also add the header row, but it's not like that will match any actual fic ID.
	# CAUTION: a little wonky because we're using these files as input after we've already opened them
	# for output. But we're reading the whole file (and closing it) before we generate any IDs to fetch.
	seen_ids = set()
	if resume:
		for filename in (csv_out, errors_out):
			if os.path.exists(filename):
				print("skipping fic IDs in", filename)
				with open(filename, 'r') as csvfile:
					id_reader = csv.reader(csvfile)
					for row in id_reader:
						seen_ids.add(row[0])

	# check if we got a CSV file. If so, open it and yield each ID.
	if (len(fic_ids) == 1 and '.csv' in fic_ids[0]):
		csv_fname = fic_ids[0]
		with open(csv_fname, 'r+') as f_in:
			reader = csv.reader(f_in)
			for row in reader:
				if not row:
					continue
				if row[0] not in seen_ids:
					yield row[0]
	else:
		# this is a little bit strange, but since yielding from the CSV is cleaner,
		# this also needs to yield rather than returning the list.
		for fic_id in fic_ids:
			yield fic_id

def main():
	fic_ids, csv_out, headers, resume, only_first_chap, lang, include_bookmarks, metadata_only = get_args()
	os.chdir(os.getcwd())
	# if the output pathname includes a folder, make sure it exists.  if not, create it.
	output_directory = os.path.dirname(csv_out)
	print(output_directory)
	if (output_directory and not os.path.isdir(output_directory)):
		print("Creating output directory " + output_directory)
		os.mkdir(output_directory)

	errors_out = os.path.join(os.path.dirname(csv_out), "errors_" + os.path.basename(csv_out))
	with open(csv_out, 'a', newline="") as f_out:
		writer = csv.writer(f_out)
		with open(errors_out, 'a', newline="") as e_out:
			errorwriter = csv.writer(e_out)
			#does the csv already exist? if not, let's write a header row.
			if os.stat(csv_out).st_size == 0:
				print('Writing a header row for the csv.')
				header = ['work_id', 'title', 'author', 'rating', 'category', 'fandom', 'relationship', 'character', 'additional tags', 'language', 'published', 'status', 'status date', 'words', 'chapters', 'comments', 'kudos', 'bookmarks', 'hits', 'all_kudos', 'all_bookmarks', 'body']
				writer.writerow(header)
				f_out.flush()

			for fic_id in generate_fic_ids(fic_ids, resume, csv_out, errors_out):
				write_fic_to_csv(fic_id, only_first_chap, lang, include_bookmarks, metadata_only, writer, errorwriter, headers)
				time.sleep(delay)

main()
