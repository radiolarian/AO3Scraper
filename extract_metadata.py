'''
Sometimes the resulting files are huge.  To extract the metadata without the fics, use this. 
'''

import csv
import os

def main():
	csv.field_size_limit(1000000000)  # up the field size because stories are long
	csv_name = raw_input("What is the csv called?  ")
	
	# clean extension
	if ".csv" not in csv_name:
		csv_name = csv_name + ".csv"

	ids_seen = []

	with open(csv_name, 'rb') as csvfile:
		with open(csv_name[:-4] + "_metadata.csv", 'a') as metacsv:
			rd = csv.reader(csvfile, delimiter=',', quotechar='"')
			wr = csv.writer(metacsv, delimiter=',', quotechar='"')
			for row in rd:
				work_id = row[0]
				if work_id not in ids_seen:
					wr.writerow(row[:-1])
					ids_seen.append(work_id)

main()