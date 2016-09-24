# AO3Scraper

In collaboration with [@ssterman](https://github.com/ssterman). A simple Python [Archive of Our Own](https://archiveofourown.org/) scraper.

Features:
- Given a fandom URL and amount of fic you want, returns a list of the fic IDs. (ao3_work_ids.py)
- Given a (list of) fic ID(s), saves a CSV of all the fic metadata and content. (ao3_get_fanfics.py)

## Dependencies
- pip install bs4
- pip install requests

## Example Usage

Let's say you wanted to collect data from the first 100 English completed fics, ordered by kudos, in the Sherlock (TV) fandom. The first thing to do is use AO3's nice search feature on their website.

We get this URL as a result: http://archiveofourown.org/works?utf8=%E2%9C%93&work_search%5Bsort_column%5D=kudos_count&work_search%5Bother_tag_names%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=1&work_search%5Bcomplete%5D=0&work_search%5Bcomplete%5D=1&commit=Sort+and+Filter&tag_id=Sherlock+%28TV%29 

Run `python ao3_work_ids.py`. The command line interface will ask you for this URL, and a .csv output file (let's call it sherlock.csv).

Now, to actually get the fics, run `python ao3_get_fanfics.py sherlock.csv`. You can optionally add some flags: 
- `--csv output.csv` (the name of the output csv file, default fanfic.csv)
- `--header 'Chrome/52 (Macintosh; Intel Mac OS X 10_10_5); Jingyi Li/UC Berkeley/email@address.com'` (an optional http header for ethical scraping)

If you don't want to give it a .csv file name, you can also query a single fic id, `python ao3_get_fanfics.py 5937274`, or enter an arbitrarily sized list of them, `python ao3_get_fanfics.py 5937274 7170752`.

By default, we save all chapters of multi-chapter fics. We cannot scrape fics that are locked (for registered users only), but submit a pull request if you want to do authentication! 

Happy scraping! 

##Improvements

We love pull requests. Some known issues, all around data clean-up / CSV saving:
- All fic content is converted to ASCII, which strips quotations if they're curly (’ instead of '). CSV writer should be able to support unicode.
- Viewing the csv in Excel causes some weird line break issues in fic content. (Viewing it in the Mac preview viewer is fine).
