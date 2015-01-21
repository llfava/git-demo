#!/usr/bin/python

import splinter
from splinter import Browser
import time
import random



def main():

    browser = Browser()

    url = 'http://www.yelp.com/search?find_desc=bars&find_loc=San+Francisco%2C+CA&ns=1'
    browser.visit(url)

    a_lst = browser.find_by_tag('a')
    for a in a_lst:
      if a['class'] == 'biz-name':
        print a['href']

    return
    ##TODO: Need to scrape here
    ##Want to get Business name, yelp url associated with business, number of reviews, aggregate rating, address
    ##Add to file
    arrow_link = browser.find_link_by_partial_href('/search?find_desc=bars&find_loc=San+Francisco%2C+CA&start=')
    arrow_link.click()

    ##TODO: Need to scrape here

    for a in range(2, 10):
        print a
        delay = random.uniform(3,5)
        print delay
        time.sleep(delay)

        arrow_link = browser.find_link_by_partial_href('/search?find_desc=bars&find_loc=San+Francisco%2C+CA&start=' + str(a))
        arrow_link.click()

        ##TODO: Need to scrape here

    ##TODO: Go to bar_yelp website and scrape review level data: user id, user location, review date, review text, 
    ## review rating
    ##Add to file

    return 0

if __name__ == "__main__":
    main()
