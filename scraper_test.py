#!/usr/bin/python

import splinter
from splinter import Browser
import json
import time
import random


def get_business_url(browser):
    business_urls = []
    a_list = browser.find_by_tag('a')
    for a in a_list:
        if a['class'] == 'biz-name':
            business_urls.append(str(a['href']))
    return business_urls

def get_business_name(browser):
    business_names = []
    a_list = browser.find_by_tag('a')
    for a in a_list:
        if a['class'] == 'biz-name':
            business_names.append(a.text)
    return business_names

def get_business_aggregate_rating(browser):
    business_ratings = []
    i_list = browser.find_by_tag('i')
    for i in i_list:
        if i['class'] == 'star-img stars_5':
            business_ratings.append(str(i['title']))
        if i['class'] == 'star-img stars_5_half':
            business_ratings.append(str(i['title']))
        if i['class'] == 'star-img stars_4':
            business_ratings.append(str(i['title']))
        if i['class'] == 'star-img stars_4_half':
            business_ratings.append(str(i['title']))
        if i['class'] == 'star-img stars_3':
            business_ratings.append(str(i['title']))
        if i['class'] == 'star-img stars_3_half':
            business_ratings.append(str(i['title']))
        if i['class'] == 'star-img stars_2':
            business_ratings.append(str(i['title']))
        if i['class'] == 'star-img stars_2_half':
            business_ratings.append(str(i['title']))
        if i['class'] == 'star-img stars_1':
            business_ratings.append(str(i['title']))
        if i['class'] == 'star-img stars_1_half':
            business_ratings.append(str(i['title']))
    return business_ratings

def get_num_reviews(browser):
    num_reviews = []
    span_list = browser.find_by_tag('span')
    for span in span_list:
        if span['class'] == 'review-count rating-qualifier':
            num_reviews.append(str(span.text))
    return num_reviews

def get_neighborhood(browser):
    neighborhoods = []
    span_list = browser.find_by_tag('span')
    for span in span_list:
        if span['class'] == 'neighborhood-str-list':
            neighborhoods.append(str(span.text))
    return neighborhoods

def get_business_address(browser):
    business_addresses = []
    address_list = browser.find_by_tag('address')
    for address in address_list:
        business_addresses.append(str(address.text))
    return business_addresses

def get_business_category(browser):
    categories = []
    span_list = browser.find_by_tag('span')
    for span in span_list:
        if span['class'] == 'category-str-list':
            categories.append(str(span.text))
    return categories

def get_business_attributes(browser):
    business_urls = get_business_url(browser)
    business_names = get_business_name(browser)
    business_ratings = get_business_aggregate_rating(browser)
    num_reviews = get_num_reviews(browser)
    neighborhoods = get_neighborhood(browser)
    business_addresses = get_business_address(browser)
    categories = get_business_category(browser)

    return(business_urls,
           business_names,
           business_ratings,
           num_reviews,
           neighborhoods,
           business_addresses,
           categories)

def make_bar_dict(business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories):
    keys = business_urls
    values = []
    for j in range(len(business_urls)):                                                                                                              
        values.append([business_names[j], business_ratings[j], num_reviews[j], neighborhoods[j], business_addresses[j], categories[j]])

    bar_dict = dict(zip(keys, values))
    return(bar_dict)

def update_bar_dict(bar_dict, business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories):
    keys = business_urls
    values = []
    for j in range(len(business_urls)):                                                                                                              
        values.append([business_names[j], business_ratings[j], num_reviews[j], neighborhoods[j], business_addresses[j], categories[j]])
    bar_dict_iter = dict(zip(keys, values))
    
    bar_dict.update(bar_dict_iter)
    return(bar_dict)

def get_userid(browser):
    ##Will need to get rid of duplicates due to review highlights etc, problem with properly aligning users to their reviews
    userids = []
    a_list = browser.find_by_tag('a')
    for a in a_list:
        if a['class'] == 'user-display-name':
            userids.append(str(a['href']))
    return userids

    




def main():

    start = time.time()

    browser = Browser()

    #Go to first page of search results for bars+SF on yelp
    url = 'http://www.yelp.com/search?find_desc=bars&find_loc=San+Francisco%2C+CA&ns=1'
    browser.visit(url)

    business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories = get_business_attributes(browser)
    bar_dict = make_bar_dict(business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories)
    #print json.dumps(bar_dict, sort_keys=True, indent=2)

    #Go to second page of search results
    arrow_link = browser.find_link_by_partial_href('/search?find_desc=bars&find_loc=San+Francisco%2C+CA&start=')
    arrow_link.click()

    time.sleep(3) ## Must have time delay here or doesn't work!!!

    business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories = get_business_attributes(browser)
    bar_dict = update_bar_dict(bar_dict, business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories)

    #Go to third and subsequent pages of search results
    for a in range(2, 5):
        print a

        arrow_link = browser.find_link_by_partial_href('/search?find_desc=bars&find_loc=San+Francisco%2C+CA&start=' + str(a))
        arrow_link.click()

        delay = random.uniform(3,5)
        time.sleep(delay)

        business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories = get_business_attributes(browser)
        bar_dict = update_bar_dict(bar_dict, business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories)
        print json.dumps(bar_dict, sort_keys=True, indent=2)

    with open('bars.json', 'w') as outfile:
        json.dump(bar_dict, outfile, indent=2)

    browser.quit()
    ### End scraping bar + SF search results

    ### Begin scraping review-level data
    urls = bar_dict.keys()
    
    
    browser = Browser()
    browser.visit(str(urls[0]))

    ##TODO: Go to bar_yelp website and scrape review level data: user id, user location, review date, review text, 
    ## review rating
    ##Add to file



    end = time.time()
    runtime = end - start
    print "runtime in minutes: " + str(runtime/60)

    return 0

if __name__ == "__main__":
    main()
