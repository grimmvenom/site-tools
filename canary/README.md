# Canary Summary
canary is a command line tool to scrape html elements, test availability of links and images, and build an easy to read report

# Disclaimer:
Be careful about the number of urls being verified / scraped. <br />
If you are doing this regularly against a website or domain without the owner's permission, it is likely to generate
a lot of network traffic / requests to the website and potentially block your IP address.
To the target, this may look like an attack / Denial of Service (DoS).


# canary Commands:
### List all available options (help)
python canary.py -h

### Output in excel format
python canary.py --excel <br />

### Define Urls to test: <br />
python canary.py -u "http://www.google.com" -u "https://www.yahoo.com"

#### Test with a .txt containing a list of urls: <br />
python canary.py -f "filepath.txt"

#### Prepend domain to urls if url does not contain http(s):// or start with domain: <br />

python canary.py -f "filepath.txt" -base "https://www.mydomain.com"

filepath.txt:<br />
  /home.html<br />
  /sitemap.html<br />

 would test: <br />
 https://www.mydomain.com/home.html <br />
 https://www.mydomain.com/sitemap.html <br />

 ### Scrape webpage and build report: <br />
 Report will contain all anchor links <a>, images <img>, and forms / input fields in an easy to read json / tsv report

 python canary.py -u "https://www.google.com" -scrape

 ### Scrape webpage, Verify images / links, and build report: <br />
 Report will contain:<br />
 * all anchor links <a>, status code, status code message, and page title,<br />
 * images <img>,status code, status code message, and page title,<br />
 * forms / input fields in an easy to read json / tsv report <br />

 python canary.py -u "https://www.google.com" -verify

 ### Request using basic authentication: <br />
 You will be prompted for password. This is to help maintain security and hide password from cmdline history. <br />
 **Warning:** You may still be able to see password sent in clear text if capturing network packets or monitoring the network <br />

 python canary.py -u "https://www.google.com" -verify -webuser "grimm" <br />

 ### Limit requests to only url's in the specified domain: <br />
 It is sometimes common to see links to facebook, twitter, and other sites when scraping. This will limit the results to
 what you care about. <br />

 python canary.py -u "https://www.mydomain.com" -verify --limit "https://www.mydomain.com" <br />

 ### Exclude specified domains when testing: <br />
 Exclude urls that have the specified domain <br />

 python canary.py -u "https://www.google.com" -verify --exclude "https://www.facebook.com" <br />

 Output is saved in the current directory of the script / executable under a Results directory



