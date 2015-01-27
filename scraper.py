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

#def parse_reviews(url, bar):
def parse_reviews():
    bar_reviews= {}
#    print bar['file_name']
#    print bar['the-boardroom-san-francisco']
#    res = glob.glob("./raw/" + bar['file_name'] + "_*.html")
    filename = 'the-boardroom-san-francisco'
    res = glob.glob("./raw/" + filename + "_1.html")
    for fname in res:
        fhandle = open(fname, 'r')
        soup = BeautifulSoup(fhandle)
        user_reviews = soup.find_all("div", {"class": "review review--with-sidebar"})
        for review in user_reviews:
            user_info = review.find_all("a", {"class": "user-display-name"})
            user_id =  user_info[0]['href'][14:] #Skip the first 14 characters, which are: /user_details?
            user_name = user_info[0].text
        #TODO 1/26 9:48 This is giving a key error
        bar_reviews['/biz/' + filename]['user_id'] = {'user_name' : user_name,
                                                      "user_location": None,
                                                      "user_rating": None,
                                                      "review_date": None,
                                                      "review_text": None,
                                                      }
        print bar_reviews

        fhandle.close()

def parse_bars(): ###Some space and /n issues in the neighborhoods and categories fields - is this an issue? LF 1/26 8:30PM
    bars = {}
    res = glob.glob("./raw/bars_nb_*.html")
#    res = glob.glob("./raw/bars_nb_1.html") # for testing

    for fname in res:
        fhandle = open(fname, 'r')
        soup = BeautifulSoup(fhandle)
        search_results = soup.find_all("div", {"class": "search-result natural-search-result"})
        #print search_results[0]['data-key']
        for result in search_results:
            biz_id = result.find("a", { "class" : "biz-name" })
                #biz.tex is the bar's URL.  Note that this url does not have www.yelp.com. Need to add that in later

            search = " star rating"
            biz_stars = result.find_all("div", {"class" : "rating-large"})
            for biz_star in biz_stars:
                bar_star = biz_star.find("i")
                s = re.search("(\S*)" + search, bar_star['title'])
                bar_rating = float(s.group(1))

            search = " review"
            biz_num_reviews = result.find_all("div", {"class": "biz-rating biz-rating-large clearfix"})
            for biz_num in biz_num_reviews:
                bar_n_review = biz_num.find_all("span")
                s = re.search("(\d*)" + search, bar_n_review[0].text)
                bar_num_reviews = int(s.group(1))

            search = ","
            biz_hoods = result.find_all("span", {"neighborhood-str-list"})
            for hood in biz_hoods:
                s1 = re.search("(.*)" + search + "(.*)" + search + "(.*)", hood.text)
                s2 = re.search("(.*)" + search + "(.*)", hood.text)
                if s1:
                    hood_1 = s1.group(1).strip()
                    hood_2 = s1.group(2).strip()
                    hood_3 = s1.group(3).strip()
                elif s2:
                    hood_1 = s2.group(1).strip()
                    hood_2 = s2.group(2).strip()
                    hood_3 = 'none'
                else:
                    hood_1 = hood.text.strip()
                    hood_2 = 'none'
                    hood_3 = 'none'
                    
            search = "/n"
            biz_address = result.find_all("address")
            bar_address =  ("%s" % biz_address[0]).replace('<br/>', ', ').replace('<address>', '').replace('</address>', '').strip()

            search = ","
            biz_cats = result.find_all("span", {"category-str-list"})
            for cat in biz_cats:
                s1 = re.search("(.*)" + search + "(.*)" + search + "(.*)", cat.text)
                s2 = re.search("(.*)" + search + "(.*)", cat.text)
                if s1:
                    cat_1 = s1.group(1)
                    cat_2 = s1.group(2)
                    cat_3 = s1.group(3)
                elif s2:
                    cat_1 = s2.group(1)
                    cat_2 = s2.group(2)
                    cat_3 = 'none'
                else:
                    cat_1 = cat.text.strip()
                    cat_2 = 'none'
                    cat_3 = 'none'

            bars[biz_id['href']] = {'bar_name' : biz_id.text,
                                     "bar_rating": bar_rating,
                                     "bar_num_reviews": bar_num_reviews,
                                     "bar_neighborhood_1": hood_1,
                                     "bar_neighborhood_2": hood_2,
                                     "bar_neighborhood_3": hood_3,
                                     "bar_address": bar_address,
                                     "bar_category_1": cat_1,
                                     "bar_category_2": cat_2,
                                     "bar_category_3": cat_3,
                                     "file_name" : biz_id['href'][5:]  # Skip the first 5 characters, which are: /biz/
                                     }

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

    if False:
        bars = parse_bars()
        with open('bars_nb.json', 'w') as outfile:
            json.dump(bars, outfile, indent=2)

    if False:
        crawl_reviews(bars)

    if True:
        reviews = parse_reviews()
        with open('user_reviews_nb.json', 'w') as outfile:
            json.dump(reviews, outfile, indent=2)



#    for bar in bars.keys():
      #parse_bar(bar, bars[bar])
#      break

if __name__ == "__main__":
    main()
