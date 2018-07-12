Sitemap.py
=================================

Sitemap.py will crawl a site and establish a web / sitemap of the entire site based on what is found on each page. This will leave an xml file in the output directory

# To Run sitemap.py simply do the following
1) open a terminal in linux
2) type cd to the directory it is stored in. (ex: cd ~/scripts/python/QA/site-tools/sitemap)
3) run the sitemap command:

python3 ./sitemap.py --domain <url> --skipext pdf --skipext xml --output <projectname>-sitemap.xml --verbose



Sitemap-parse.py
=================================

Sitemap-parse.py will take the xml output of sitemap and add it to the automation database. This database is used by scouter and other command line tools

# To Run sitemap.py simply do the following
1) open a terminal in linux
2) type cd to the directory it is stored in. (ex: cd ~/scripts/python/QA/site-tools/sitemap)
3) run the sitemap command:

python3 ./sitemap-parse.py -f <project>-sitemap.xml -db <db name>.db -t <project>_<environment>

this will add a <project>_sitemap table to the automation.db database if a project was added under the projects table. It is important to have the project domain specified with a unique project name. ex: http://www.ford.com = project(bsr_prod)

python3 ./sitemap-parse.py -f FOC-fordca-sitemap.xml -db /home/user/WS_Scripts/python/QA/site-tools/database/Sitemaps/FordDirect-FOC.db -t foc_prod

