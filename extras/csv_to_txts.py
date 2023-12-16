import csv
import os
import argparse

def main():
    csv.field_size_limit(1000000000)  # up the field size because stories are long

    parser = argparse.ArgumentParser(description='convert fic text in a csv into txt files')
    parser.add_argument(
        'csv', metavar='csv',
        help='the name of the csv with the original data')

    args = parser.parse_args()
    csv_name = args.csv

    # clean extension
    if ".csv" not in csv_name:
        csv_name = csv_name + ".csv"

    with open(csv_name, 'rt', encoding='utf-8') as csvfile:
        folder_name = csv_name + "_text_files"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        rd = csv.reader(csvfile, delimiter=',', quotechar='"')
        headers = next(rd)  # get the header row
        for row in rd:
            if len(row):
                # Extracting the required data from the row
                work_id = row[0]
                title = row[1]
                author = row[2].strip("[]'")  # Assuming author's name is in the 3rd column
                rating = row[3]  # Assuming rating is in the 4th column
                relationship = row[6]  # Assuming relationship is in the 7th column
                additional_tags = row[8]  # Assuming additional tags are in the 9th column
                language = row[9]  # Assuming language is in the 10th column
                status = row[11]  # Assuming status is in the 12th column
                chapters = row[14]  # Assuming chapters is in the 15th column
                story_content = row[-1]  # Assuming story content is the last column

                # Cleaning title to make it a valid filename
                cleaned_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                file_name = f"{cleaned_title}.txt"

                with open(os.path.join(folder_name, file_name), "w", encoding='utf-8') as text_file:
                    # Writing the metadata and story content to the file
                    text_file.write(f"Title: {title}\n")
                    text_file.write(f"Work ID: {work_id}\n")
                    text_file.write(f"Author: {author}\n")
                    text_file.write(f"Rating: {rating}\n")
                    text_file.write(f"Relationship: {relationship}\n")
                    text_file.write(f"Additional Tags: {additional_tags}\n")
                    text_file.write(f"Language: {language}\n")
                    text_file.write(f"Status: {status}\n")
                    text_file.write(f"Chapters: {chapters}\n\n")
                    text_file.write(story_content)

main()
