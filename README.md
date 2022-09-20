# AO3Scraper

In collaboration with [@ssterman](https://github.com/ssterman). A simple Python [Archive of Our Own](https://archiveofourown.org/) scraper. Now with HASTAC 2017 [presentation slides](https://docs.google.com/presentation/d/1GrpMYw25Bz_m0r2hv0Orgp-uxSIi4HdrHpzL6deCopc)!

Features:
- Given a fandom URL and amount of fic you want, returns a list of the fic IDs. (ao3_work_ids.py)
- Given a (list of) fic ID(s), saves a CSV of all the fic metadata and content. (ao3_get_fanfics.py)
- Given the CSV of fic metadata and content created by ao3_get_fanfics.py, saves a new CSV of only the metadata. (extract_metadata.py)
- Given the CSV of fic metadata and content created by ao3_get_fanfics.py, creates a folder of individual text files containing the body of each fic (csv_to_txts.py)
- Given the CSV of fic metadata and content created by ao3_get_fanfics.py, uses an AO3 tag URL to count the number of works using that tag or its wrangled synonyms (get_tag_counts.py)
- (new!) Scrape users who have authored, kudos-ed, bookmarked (``get_authors, get_kudos, get_bookmarks`` functions)
- (new!) Scrape fics of only a certain language

## Dependencies
- pip install bs4
- pip install requests
- pip install unidecode
- pip install datetime
- pip install argparse
- pip install lxml


## Example Usage

Let's say you wanted to collect data from the first 100 English completed fics, ordered by kudos, in the Sherlock (TV) fandom. The first thing to do is use AO3's nice search feature on their website.

We get this URL as a result: http://archiveofourown.org/works?utf8=%E2%9C%93&work_search%5Bsort_column%5D=kudos_count&work_search%5Bother_tag_names%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=1&work_search%5Bcomplete%5D=0&work_search%5Bcomplete%5D=1&commit=Sort+and+Filter&tag_id=Sherlock+%28TV%29 

Run `python ao3_work_ids.py <url>`. You can optionally add some flags: 
- `--out_csv output.csv` (the name of the output csv file, default work_ids.csv)
- `--num_to_retrieve 10` (how many work ids you want, defaults to all)
- `--multichapter_only 1` (restricts output to only works with more than one chapter, defaults to false)
- `--tag_csv name_of_csv.csv` (provide an optional list of tags; the retrieved fics must have one or more such tags. default ignores this functionality)

The only required input is the search URL.  

For our example, we might say: 

`python ao3_work_ids.py "http://archiveofourown.org/works?utf8=%E2%9C%93&work_search%5Bsort_column%5D=kudos_count&work_search%5Bother_tag_names%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=1&work_search%5Bcomplete%5D=0&work_search%5Bcomplete%5D=1&commit=Sort+and+Filter&tag_id=Sherlock+%28TV%29" --num_to_retrieve 100 --out_csv sherlock`

Now, to actually get the fics, run `python ao3_get_fanfics.py sherlock.csv`. You can optionally add some flags: 
- `--csv output.csv` (the name of the output csv file, default fanfic.csv)
- `--header 'Chrome/52 (Macintosh; Intel Mac OS X 10_10_5); Jingyi Li/UC Berkeley/email@address.com'` (an optional http header for ethical scraping)
- `--lang English` (scrapes fics of only a specific language, this argument will not work if you use incorrect spelling and/or capitalization, if this argument is not used the program will scrape all fics regadless of language) Note: if the desired language is not English, then you will have to input the name of that language as it appears on AO3, for example if you want your fics to be in French the argument after `--lang` should be 'Francais' not 'French', including any accents in the input language will also not work.
- `--bookmarks` includes the users who have bookmarked a fic.  For fics with many bookmarks, this is a slow operation. 
- `--firstchap 1` will retrieve only the first chapter of multi-chapter fics. By default, we save all chapters are saved.
- `--metadata-only` will skip retrieving any fic contents and only stores the metadata for fics.

If you don't want to give it a .csv file name, you can also query a single fic id, `python ao3_get_fanfics.py 5937274`, or enter an arbitrarily sized list of them, `python ao3_get_fanfics.py 5937274 7170752`.

If you stop a scrape from a csv partway through (or it crashes), you can restart from the last uncollected work_id using the flag `--restart 012345` (the work_id).  The scraper will skip all ids up to that point in the csv, then begin again from the given id. 

We cannot scrape fics that are locked (for registered users only), but submit a pull request if you want to build authentication! 

**Note that the 5 second delays before requesting from AO3's server are in compliance with the AO3 terms of service.  Please do not remove these delays.**

Happy scraping! 

## Improvements

We love pull requests!

## FF.net

Want to scrape fanfiction.net? Check out my friend [@smilli](https://github.com/smilli/)'s [ff.net scraper](https://github.com/smilli/fanfiction)! 

## License
This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0). Feel free to use it and adapt it however you want, but don't make money off of it!
