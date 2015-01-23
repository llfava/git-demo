#!/usr/bin/python

import splinter
from splinter import Browser
import json
import time
import random
import re

def make_tag_lists(browser):
    a_list = browser.find_by_tag('a')
    i_list = browser.find_by_tag('i')
    span_list = browser.find_by_tag('span')
    address_list = browser.find_by_tag('address')
    return a_list, i_list, span_list, address_list

def get_business_url(a_list):
    business_urls = []
    for a in a_list:
        if a['class'] == 'biz-name':
            business_urls.append(str(a['href']))
    return business_urls

def get_business_name(a_list):
    business_names = []
    for a in a_list:
        if a['class'] == 'biz-name':
            business_names.append(a.text)
    return business_names

def get_business_aggregate_rating(i_list):
    business_ratings = []
    for i in i_list:
        if i['class'] == 'star-img stars_5':
            business_ratings.append(str(i['title']))
            continue
        if i['class'] == 'star-img stars_4':
            business_ratings.append(str(i['title']))
            continue
        if i['class'] == 'star-img stars_4_half':
            business_ratings.append(str(i['title']))
            continue
        if i['class'] == 'star-img stars_3':
            business_ratings.append(str(i['title']))
            continue
        if i['class'] == 'star-img stars_3_half':
            business_ratings.append(str(i['title']))
            continue
        if i['class'] == 'star-img stars_2':
            business_ratings.append(str(i['title']))
            continue
        if i['class'] == 'star-img stars_2_half':
            business_ratings.append(str(i['title']))
            continue
        if i['class'] == 'star-img stars_1':
            business_ratings.append(str(i['title']))
            continue
        if i['class'] == 'star-img stars_1_half':
            business_ratings.append(str(i['title']))
            continue
    return business_ratings

def get_num_reviews(span_list):
    num_reviews = []
    for span in span_list:
        if span['class'] == 'review-count rating-qualifier':
            num_reviews.append(str(span.text))
    return num_reviews

def get_neighborhood(span_list):
    neighborhoods = []
    for span in span_list:
        if span['class'] == 'neighborhood-str-list':
            neighborhoods.append(str(span.text))
    return neighborhoods

def get_business_address(address_list):
    business_addresses = []
    for address in address_list:
        business_addresses.append(str(address.text))
    return business_addresses

def get_business_category(span_list):
    categories = [] 
    for span in span_list:
        if span['class'] == 'category-str-list':
            categories.append(str(span.text))
    return categories

def get_business_attributes(a_list, i_list, span_list, address_list):
    business_urls = get_business_url(a_list)
    business_names = get_business_name(a_list)
    business_ratings = get_business_aggregate_rating(i_list)
    num_reviews = get_num_reviews(span_list)
    neighborhoods = get_neighborhood(span_list)
    business_addresses = get_business_address(address_list)
    categories = get_business_category(span_list)

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

def combine_user_reviews(reviews, user_ids, user_locations):
    for j in range(len(user_ids)):
        reviews.append([user_ids[j], user_locations[j]])
    print reviews
    return (reviews)


def update_bar_dict(bar_dict, business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories):
    keys = business_urls
    values = []
    for j in range(len(business_urls)):                                                                                                              
        values.append([business_names[j], business_ratings[j], num_reviews[j], neighborhoods[j], business_addresses[j], categories[j]])
    bar_dict_iter = dict(zip(keys, values))
    
    bar_dict.update(bar_dict_iter)
    return(bar_dict)

def get_review_list_marker(browser):
    r_list = None
    divs = browser.find_by_tag('div')
    for div in divs:
        if div['class'] == 'review-list':
            r_list = div
            break
    return(r_list)

def get_user_id(r_list):
    user_ids = []
    a_list = r_list.find_by_tag('a')
    for a in a_list:
        if a['class'] == 'user-display-name':
            user_ids.append([str(a['href']),a.text])
    return(user_ids)

def get_user_location(r_list):
    user_locations = []
    reviews_list = r_list.find_by_tag('li')
    for li in reviews_list:
        if li['class'] == 'user-location':
            user_locations.append(li.text)
    return(user_locations)
    
def update_user_dict(user_dict, business_url, reviews):
    return (user_dict)


###TODO (1/22/15)  Write scraper for review rating, date and text
###Possibly also get more business data such as parking, ambience, noise level, etc.


def main():

    start = time.time()

    browser = Browser()

    #Go to first page of search results for bars+SF on yelp
    url = 'http://www.yelp.com/search?find_desc=bars&find_loc=San+Francisco%2C+CA&ns=1'
    browser.visit(url)

    a_list, i_list, span_list, address_list = make_tag_lists(browser)
    business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories = get_business_attributes(a_list, i_list, span_list, address_list)
    bar_dict = make_bar_dict(business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories)
    #print json.dumps(bar_dict, sort_keys=True, indent=2)

    #Go to second page of search results
    arrow_link = browser.find_link_by_partial_href('/search?find_desc=bars&find_loc=San+Francisco%2C+CA&start=')
    arrow_link.click()

    time.sleep(3) ## Must have time delay here or doesn't work!!!

    a_list, i_list, span_list, address_list = make_tag_lists(browser)
    business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories = get_business_attributes(a_list, i_list, span_list, address_list)
    bar_dict = update_bar_dict(bar_dict, business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories)

    #Go to third and subsequent pages of search results
#    for a in range(2, 3):
#        print a

#        arrow_link = browser.find_link_by_partial_href('/search?find_desc=bars&find_loc=San+Francisco%2C+CA&start=' + str(a))
#        arrow_link.click()

#        delay = random.uniform(3,5)
#        time.sleep(delay)

#        a_list, i_list, span_list, address_list = make_tag_lists(browser)
#        business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories = get_business_attributes(a_list, i_list, span_list, address_list)
#        bar_dict = update_bar_dict(bar_dict, business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories)
        #print json.dumps(bar_dict, sort_keys=True, indent=2)

    with open('bars.json', 'w') as outfile:
        json.dump(bar_dict, outfile, indent=2)

    browser.quit()
    ### End scraping bar + SF search results

    ### Begin scraping review-level data

    user_dict = {}
    i=0
    for key in bar_dict.keys():
        print key

        #Check how many reviews there are
        num_of_reviews = bar_dict[key][2]
        search = ' reviews'
        s = re.search("(\d*)" + search, num_of_reviews)
        number_of_reviews =  int(s.group(1))
        
        print 'Number of reviews for ' + key + 'is ' + str(number_of_reviews)

        reviews = []

        browser = Browser()
        browser.visit(key)

        r_list = get_review_list_marker(browser)
        user_ids = get_user_id(r_list)
        user_locations = get_user_location(r_list)
        reviews = combine_user_reviews(reviews, user_ids, user_locations)
        user_dict[key] = reviews
        with open('user_reviews.json', 'w') as outfile:
            json.dump(user_dict, outfile, indent=2)

        num_reviews_page = len(user_ids)
        print 'Number of reviews on this page is ' + str(num_reviews_page)
        num_reviews_remaining = number_of_reviews - num_reviews_page
        print 'Number of reviews remaining after this page is ' + str(num_reviews_remaining)
        
        #Go to second page of search results

        if num_reviews_remaining > 0: 
            arrow_link = browser.find_link_by_partial_href(key + '?start=')
            arrow_link.click()

            time.sleep(3) ## Must have time delay here or doesn't work!!!

            r_list = get_review_list_marker(browser)
            user_ids = get_user_id(r_list)
            user_locations = get_user_location(r_list)
            reviews = combine_user_reviews(reviews, user_ids, user_locations)
            print 'number of reviews in list is ' + str(len(reviews))
            user_dict[key] = reviews
            with open('user_reviews.json', 'w') as outfile:
                json.dump(user_dict, outfile, indent=2)

            num_reviews_page = len(user_ids)
            print 'Number of reviews on this page is ' + str(num_reviews_page)
            num_reviews_remaining = num_reviews_remaining - num_reviews_page
            print 'Number of reviews remaining after this page is ' + str(num_reviews_remaining)

            
            #Go to third and subsequent pages of search results
            if num_reviews_remaining > 0:
                for a in range(2, 3):
                    print a
                    start_num = 40*a
                    arrow_link = browser.find_link_by_partial_href(key + '?start=' + str(start_num))
                    arrow_link.click()

                    delay = random.uniform(3,5)
                    time.sleep(delay)
        
                    r_list = get_review_list_marker(browser)
                    user_ids = get_user_id(r_list)
                    user_locations = get_user_location(r_list)
                    reviews = combine_user_reviews(reviews, user_ids, user_locations)
                    print 'number of reviews in list is ' + str(len(reviews))
                    user_dict[key] = reviews

                    with open('user_reviews.json', 'w') as outfile:
                        json.dump(user_dict, outfile, indent=2)

            else:
                i=i+1
                browser.quit()
        else:
            i=i+1
            browser.quit()

        if i > 6:
            break




    end = time.time()
    runtime = end - start
    print "runtime in minutes: " + str(runtime/60)

    return 0

if __name__ == "__main__":
    main()
