'''
Sometimes the resulting files are huge.  To extract the metadata without the fics, use this. 
'''

import csv
import os
import argparse

def main():
	csv.field_size_limit(1000000000)  # up the field size because stories are long

	parser = argparse.ArgumentParser(description='Extract metadata from a fic csv')
	parser.add_argument(
		'csv', metavar='csv',
		help='the name of the csv with the original data')

	args = parser.parse_args()
	csv_name = args.csv

	# clean extension
	if ".csv" not in csv_name:
		csv_name = csv_name + ".csv"

	ids_seen = []

	with open(csv_name, 'rt') as csvfile:
		with open(csv_name[:-4] + "_metadata.csv", 'a') as metacsv:
			rd = csv.reader(csvfile, dialect=csv.excel_tab, delimiter=',', quotechar='"')
			wr = csv.writer(metacsv, delimiter=',', quotechar='"')
			for row in rd:
				if (row != []):
					work_id = row[0]
					if work_id not in ids_seen:
						wr.writerow(row[:-3])
						ids_seen.append(work_id)

main()