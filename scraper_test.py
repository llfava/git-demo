#!/usr/bin/python

import splinter
from splinter import Browser
import time
import random

def get_business_url(browser):
    a_list = browser.find_by_tag('a')
    for a in a_list:
        if a['class'] == 'biz-name':
            print a['href']
    return 0

def get_business_name(browser):
    a_list = browser.find_by_tag('a')
    for a in a_list:
        if a['class'] == 'biz-name':
            print a.text
    return 0

def get_business_aggregate_rating(browser):
    i_list = browser.find_by_tag('i')
    for i in i_list:
        if i['class'] == 'star-img stars_5':
            print i['title']
        if i['class'] == 'star-img stars_5_half':
            print i['title']
        if i['class'] == 'star-img stars_4':
            print i['title']
        if i['class'] == 'star-img stars_4_half':
            print i['title']
        if i['class'] == 'star-img stars_3':
            print i['title']
        if i['class'] == 'star-img stars_3_half':
            print i['title']
        if i['class'] == 'star-img stars_2':
            print i['title']
        if i['class'] == 'star-img stars_2_half':
            print i['title']
        if i['class'] == 'star-img stars_1':
            print i['title']
        if i['class'] == 'star-img stars_1_half':
            print i['title']
    return 0

def get_num_reviews(browser):
    span_list = browser.find_by_tag('span')
    for span in span_list:
        if span['class'] == 'review-count rating-qualifier':
            print span.text
    return 0

def get_neighborhood(browser):
    span_list = browser.find_by_tag('span')
    for span in span_list:
        if span['class'] == 'neighborhood-str-list':
            print span.text
    return 0

def get_business_address(browser):
    address_list = browser.find_by_tag('address')
    for address in address_list:
        print address.text
    return 0

def get_business_category(browser):
    span_list = browser.find_by_tag('span')
    for span in span_list:
        if span['class'] == 'category-str-list':
            print span.text
    return 0

def get_business_attributes(browser):
    get_business_url(browser)
    get_business_name(browser)
    get_business_aggregate_rating(browser)
    get_num_reviews(browser)
    get_neighborhood(browser)
    get_business_address(browser)
    get_business_category(browser)
    return 0

def main():

    browser = Browser()

    #Go to first page of search results for bars+SF on yelp
    url = 'http://www.yelp.com/search?find_desc=bars&find_loc=San+Francisco%2C+CA&ns=1'
    browser.visit(url)

    get_business_attributes(browser)

    #Go to second page of search results
    arrow_link = browser.find_link_by_partial_href('/search?find_desc=bars&find_loc=San+Francisco%2C+CA&start=')
    arrow_link.click()

    time.sleep(3) ## Must have time delay here or doesn't work!!!

    get_business_attributes(browser)


    for a in range(2, 5):
        print a

        arrow_link = browser.find_link_by_partial_href('/search?find_desc=bars&find_loc=San+Francisco%2C+CA&start=' + str(a))
        arrow_link.click()

        delay = random.uniform(3,5)
        time.sleep(delay)

        get_business_attributes(browser)


    ##TODO: Go to bar_yelp website and scrape review level data: user id, user location, review date, review text, 
    ## review rating
    ##Add to file


#    browser.quit()
    return 0

if __name__ == "__main__":
    main()
