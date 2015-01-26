#!/usr/bin/python
import re
import sys
import json
import time
import glob
import random

import splinter
from splinter import Browser
from bs4 import BeautifulSoup

def parse_bar(url, bar):
    print bar['file_name']
    res = glob.glob("./raw/" + bar['file_name'] + "*.html")
    for fname in res:
        fhandle = open(fname, 'r')
        soup = BeautifulSoup(fhandle)
        # TODO: Parse this bar's reviews
        fhandle.close()

def parse_bars():
    bars = {}
#    res = glob.glob("./raw/bars_nb_*.html")
    res = glob.glob("./raw/bars_nb_0.html")
    for fname in res:
        fhandle = open(fname, 'r')
        soup = BeautifulSoup(fhandle)
        bizes = soup.find_all("a", { "class" : "biz-name" })
        #print bizes
        for biz in bizes:
          # biz.tex is the bar's URL.  Note that this url does not have www.yelp.com. Need to add that in later
          bars[biz['href']] = {'bar_name' : biz.text,
            "bar_rating": None,
            "bar_num_reviews": None,
            "bar_neighborhood_1": None,
            "bar_neighborhood_2": None,
            "bar_neighborhood_3": None,
            "bar_address": None,
            "bar_category_1": None,
            "bar_category_2": None,
            "bar_category_3": None,
            "file_name" : biz['href'][5:]  # Skip the first 5 characters, which are: /biz/
         }

        #Get bar rating
        bar_ratings = []
        search = " star rating"
        bizes = soup.find_all("div", {"class" : "rating-large"})
        for biz in bizes:
            #print biz
            bar_stars = biz.find_all("i")
            if len(bar_stars) > 0:
                for review in bar_stars:
                    s = re.search("(\S*)" + search, review['title'])
                    bar_ratings.append(s.group(1))
        #Need to get this info into the dictionary

        #Get bar num reviews
        bar_num_reviews = []
        search = " reviews"
        bizes = soup.find_all("div", {"class": "biz-rating biz-rating-large clearfix"})
        for biz in bizes:
            bar_n_reviews = biz.find_all("span")
            for review in bar_n_reviews:
                s = re.search("(\d*)" + search, review.text)
                bar_num_reviews.append(s.group(1))
        #Need to get this info into the dictionary

        #Get neighborhoods
        neighborhood_1 = []
        neighborhood_2 = []
        neighborhood_3 = []
        search = ","
        bizes = soup.find_all("span", {"neighborhood-str-list"})
        for biz in bizes:
            print biz.text
            s1 = re.search("(.*)" + search + "(.*)" + search + "(.*)", biz.text)
            s2 = re.search("(.*)" + search + "(.*)", biz.text)
            if s1:
                hood_1 = s1.group(1)
                hood_2 = s1.group(2)
                hood_3 = s1.group(3)
            elif s2:
                hood_1 = s2.group(1)
                hood_2 = s2.group(2)
                hood_3 = 'none'
            else:
                hood_1 = biz.text
                hood_2 = 'none'
                hood_3 = 'none'
            neighborhood_1.append(hood_1)
            neighborhood_2.append(hood_2)
            neighborhood_3.append(hood_3)
        #Need to get this info into the dictionary
        fhandle.close()
    return bars

def crawl_reviews(bars):
    limit = 20
    base_dir = "./raw/"
    for (bar_num,url) in enumerate(bars.keys()):
      start_page = len(glob.glob('./raw/' + bars[url]['file_name'] + '*')) + 1
      if start_page >= limit: # Limit the number of pages of reviews per bar
        print "Limiting %s to %d pages of reviews" % (url, limit)
        continue
      print "Crawling %s starting from page %d" % (url, start_page)
      crawl("./raw/" + bars[url]['file_name'] + "_%d.html", url, 40, start_page=start_page)
      # When we return from crawl, its likely that yelp cut of off, and we haven't gotten all the data yet
      # for a given bar, lets just more onto the next bar

def crawl(base_name, url, increment, start_page=1, num_pages=6):
    # Scrapping yelp is not fun...
    # They often kill the connection, at which point we need to start crawling again from page 1
    # The navigation buttons on the first page look like:
    #     "1 2 3 4 5 6 7 8 9"
    # So, if they killed the connection when we were visiting the 16th page,
    # we need to go back to page "1", then crawl to page "9"
    # At this point, the buttons will look like:
    #     "5 6 7 8 9 10 11 12 13"
    # So we need to then crawl to page "13"
    # At this point, the buttons will look like: 
    #     "9 10 11 12 13 14 15 16 17"
    # At this point, we can resume crawling from 16 on...
    browser = Browser()
    browser.visit('http://www.yelp.com' + url)
    time.sleep(random.uniform(3,5))
    fhandle = open(base_name % 1, 'w')  # Always start from the first page
    fhandle.write(browser.html.encode('utf-8'))
    fhandle.close()

    # This is code that handles the button funkness when we want to resume scraping from a certain page
    click_list = []
    count = 0
    if start_page > 9:
      count += 9
      click_list.append(count)
      while (count + 4) < start_page:
        count += 4
        click_list.append(count)
    for page_num in click_list:
        print "  Clicking through %d" % page_num
        try:
          arrow_link = browser.find_link_by_partial_href(url + '&start=' + str((page_num-1)*increment))
          arrow_link.click()
        except AttributeError:
          arrow_link = browser.find_link_by_partial_href(url + '?start=' + str((page_num-1)*increment))
          arrow_link.click()
        time.sleep(random.uniform(3,5))

    for page_num in range(start_page, start_page+num_pages):
        if page_num == 1:
          continue  # We already processed the first page, no need to do it again
        try:
          arrow_link = browser.find_link_by_partial_href(url + '&start=' + str((page_num-1)*increment))
          arrow_link.click()
        except AttributeError:
          try:
            arrow_link = browser.find_link_by_partial_href(url + '?start=' + str((page_num-1)*increment))
            arrow_link.click()
          except Exception as e:
            print "  Looks like %s only has %d pages of reviews" % (url, page_num-1)
            browser.quit()
            return
            #sys.stderr.write("page_num=%d\n" % page_num)
            #sys.stderr.write("increment=%d\n" % increment)
            #sys.stderr.write("url=%s\n" % url)
            #raise e
        time.sleep(random.uniform(3,5))
        fhandle = open(base_name % page_num, 'w')
        fhandle.write(browser.html.encode('utf-8'))
        fhandle.close()
    browser.quit()

def main():
    if False:  # Set this to True or False depending on whether we want to crawl bars
      url = '/search?find_desc=bars&find_loc=North+Beach%2C+San+Francisco%2C+CA'
      crawl("./raw/bars_nb_%d.html", url, 10)

    bars = parse_bars()
    with open('bars_nb.json', 'w') as outfile:
      json.dump(bars, outfile, indent=2)

    if False:
      crawl_reviews(bars)

    for bar in bars.keys():
      #parse_bar(bar, bars[bar])
      break

if __name__ == "__main__":
    main()
