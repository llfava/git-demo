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

def get_business_id(a_list):
    business_urls = []
    business_names = []
    search = "\u2019"
    for a in a_list:
        if a['class'] == 'biz-name':
            business_urls.append(str(a['href']))
            ###Not sure if I need to correct for unicode or not
            #s = re.search("(.*)" + search + "(.*)", a.text)
            #if s:
            #    b_name = s.group(1) + "'" + s.group(2)
            #    business_name = {'bar_name': b_name}
            #else:
            #    business_name = {'bar_name': a.text}
            business_name = {'bar_name': a.text}
            business_names.append(business_name)
    return (business_urls, business_names)

def get_business_aggregate_rating(i_list):
    business_ratings = []
    search = " star rating"
    for i in i_list:
        if i['class'] == 'star-img stars_5':
            s = re.search("(\S*)" + search, i['title'])
            num_stars = s.group(1)
            business_rating = {'bar_rating':str(num_stars)}
            business_ratings.append(business_rating)
            continue
        if i['class'] == 'star-img stars_4_half':
            s = re.search("(\S*)" + search, i['title'])
            num_stars = s.group(1)
            business_rating = {'bar_rating':str(num_stars)}
            business_ratings.append(business_rating)
            continue
        if i['class'] == 'star-img stars_4':
            s = re.search("(\S*)" + search, i['title'])
            num_stars = s.group(1)
            business_rating = {'bar_rating':str(num_stars)}
            business_ratings.append(business_rating)
            continue
        if i['class'] == 'star-img stars_3_half':
            s = re.search("(\S*)" + search, i['title'])
            num_stars = s.group(1)
            business_rating = {'bar_rating':str(num_stars)}
            business_ratings.append(business_rating)
            continue
        if i['class'] == 'star-img stars_3':
            s = re.search("(\S*)" + search, i['title'])
            num_stars = s.group(1)
            business_rating = {'bar_rating':str(num_stars)}
            business_ratings.append(business_rating)
            continue
        if i['class'] == 'star-img stars_2_half':
            s = re.search("(\S*)" + search, i['title'])
            num_stars = s.group(1)
            business_rating = {'bar_rating':str(num_stars)}
            business_ratings.append(business_rating)
            continue
        if i['class'] == 'star-img stars_2':
            s = re.search("(\S*)" + search, i['title'])
            num_stars = s.group(1)
            business_rating = {'bar_rating':str(num_stars)}
            business_ratings.append(business_rating)
            continue
        if i['class'] == 'star-img stars_1_half':
            s = re.search("(\S*)" + search, i['title'])
            num_stars = s.group(1)
            business_rating = {'bar_rating':str(num_stars)}
            business_ratings.append(business_rating)
            continue
        if i['class'] == 'star-img stars_1':
            s = re.search("(\S*)" + search, i['title'])
            num_stars = s.group(1)
            business_rating = {'bar_rating':str(num_stars)}
            business_ratings.append(business_rating)
            continue
    return business_ratings

def get_num_reviews(span_list):
    num_reviews = []
    search = ' reviews'
    for span in span_list:
        if span['class'] == 'review-count rating-qualifier':
            s = re.search("(\d*)" + search, span.text)
            number_of_reviews =  int(s.group(1))
            num_review = {'bar_num_reviews':str(number_of_reviews)}
            num_reviews.append(num_review)
    return num_reviews

def get_neighborhoods(span_list):
    neighborhood_1 = []
    neighborhood_2 = []
    neighborhood_3 = []
    search = ","
    for span in span_list:
        if span['class'] == 'neighborhood-str-list':
            s1 = re.search("(.*)" + search + "(.*)" + search + "(.*)", span.text)
            s2 = re.search("(.*)" + search + "(.*)", span.text)
            if s1:
                hood_1 = s1.group(1)
                hood_2 = s1.group(2)
                hood_3 = s1.group(3)
            elif s2:
                hood_1 = s2.group(1)
                hood_2 = s2.group(2)
                hood_3 = 'none'
            else:
                hood_1 = span.text
                hood_2 = 'none'
                hood_3 = 'none'
            neighborhood_1.append({'bar_neighborhood_1':hood_1})
            neighborhood_2.append({'bar_neighborhood_2':hood_2})
            neighborhood_3.append({'bar_neighborhood_3':hood_3})
    return (neighborhood_1, neighborhood_2, neighborhood_3)

def get_business_address(address_list):
    business_addresses = []
    search = "\n"
    for address in address_list:
        s = re.search("(.*)" + search + "(.*)", address.text)
        formatted_address = s.group(1) + ', ' + s.group(2)
        business_address = {'bar_address':formatted_address}
        business_addresses.append(business_address)
    return business_addresses

def get_business_categories(span_list):
    category_1 = []
    category_2 = []
    category_3 = []
    search = ","
    for span in span_list:
        if span['class'] == 'category-str-list':
            s1 = re.search("(.*)" + search + "(.*)" + search + "(.*)", span.text)
            s2 = re.search("(.*)" + search + "(.*)", span.text)
            if s1:
                cat_1 = s1.group(1)
                cat_2 = s1.group(2)
                cat_3 = s1.group(3)
            elif s2:
                cat_1 = s2.group(1)
                cat_2 = s2.group(2)
                cat_3 = 'none'
            else:
                cat_1 = span.text
                cat_2 = 'none'
                cat_3 = 'none'
            category_1.append({'bar_category_1':cat_1})
            category_2.append({'bar_category_2':cat_2})
            category_3.append({'bar_category_3':cat_3})
    return (category_1, category_2, category_3)

def get_business_attributes(a_list, i_list, span_list, address_list):
    business_urls, business_names = get_business_id(a_list)
    business_ratings = get_business_aggregate_rating(i_list)
    num_reviews = get_num_reviews(span_list)
    neighborhood_1, neighborhood_2, neighborhood_3 = get_neighborhoods(span_list)
    business_addresses = get_business_address(address_list)
    category_1, category_2, category_3 = get_business_categories(span_list)

    return(business_urls,
           business_names,
           business_ratings,
           num_reviews,
           neighborhood_1,
           neighborhood_2,
           neighborhood_3,
           business_addresses,
           category_1,
           category_2,
           category_3)

def make_bar_dict(business_urls, business_names, 
                  business_ratings, num_reviews, 
                  neighborhood_1, neighborhood_2, neighborhood_3, 
                  business_addresses, 
                  category_1, category_2, category_3):
    keys = business_urls
    values = []
    for j in range(len(business_urls)):                                                                                                              
        values.append([business_names[j], business_ratings[j], num_reviews[j], neighborhood_1[j], neighborhood_2[j], neighborhood_3[j], business_addresses[j], category_1[j], category_2[j], category_3[j]])

    bar_dict = dict(zip(keys, values))
    return(bar_dict)

def combine_user_reviews(reviews, user_ids, user_locations):
    for j in range(len(user_ids)):
        reviews.append([user_ids[j], user_locations[j]])
    #print reviews
    return (reviews)

#Need to update arguments 1/25 12pm
def update_bar_dict(bar_dict, business_urls, business_names, business_ratings, num_reviews, neighborhoods, business_addresses, categories):
    keys = business_urls
    values = []
    for j in range(len(business_urls)):                                                                                                              
        values.append([business_names[j], business_ratings[j], num_reviews[j], neighborhood_1[j], neighborhood_2[j], neighborhood_3[j], business_addresses[j], category_1[j], category_2[j], category_3[j]])
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
    user_names = []
    a_list = r_list.find_by_tag('a')
    for a in a_list:
        if a['class'] == 'user-display-name':
            user_id = {'user_id':str(a['href'])}
            user_name = {'user_name':a.text}
            user_ids.append(user_id)
            user_names.append(user_name)
    return(user_ids, user_names)

def get_user_location(r_list):
    user_locations = []
    reviews_list = r_list.find_by_tag('li')
    for li in reviews_list:
        if li['class'] == 'user-location':
            user_location = {'user_location':li.text}
            user_locations.append(user_location)
    return(user_locations)
    

###TODO (1/22/15)  Write scraper for review rating, date and text
###Possibly also get more business data such as parking, ambience, noise level, etc.


def main():

    start = time.time()

    browser = Browser()

    #Go to first page of search results for bars+SF on yelp
    #url = 'http://www.yelp.com/search?find_desc=bars&find_loc=San+Francisco%2C+CA&ns=1'  #General SF bars search
    url = 'http://www.yelp.com/search?find_desc=bars&find_loc=North+Beach%2C+San+Francisco%2C+CA&ns=1#' #North Beach, SF search
    browser.visit(url)

    a_list, i_list, span_list, address_list = make_tag_lists(browser)
    business_urls, business_names, business_ratings, num_reviews, neighborhood_1, neighborhood_2, neighborhood_3, business_addresses, category_1, category_2, category_3 = get_business_attributes(a_list, i_list, span_list, address_list)
    bar_dict = make_bar_dict(business_urls, business_names, business_ratings, num_reviews, neighborhood_1, neighborhood_2, neighborhood_3, business_addresses, category_1, category_2, category_3)
    #print json.dumps(bar_dict, sort_keys=True, indent=2)

    #Go to second page of search results
#        arrow_link = browser.find_link_by_partial_href('/search?find_desc=bars&find_loc=San+Francisco%2C+CA&start=') # for general search
    arrow_link = browser.find_link_by_partial_href('/search?find_desc=bars&find_loc=North+Beach%2C+San+Francisco%2C+CA&start') #for north beach
    arrow_link.click()

    time.sleep(3) ## Must have time delay here or doesn't work!!!

    a_list, i_list, span_list, address_list = make_tag_lists(browser)
    business_urls, business_names, business_ratings, num_reviews, neighborhood_1, neighborhood_2, neighborhood_3, business_addresses, category_1, category_2, category_3 = get_business_attributes(a_list, i_list, span_list, address_list)
    bar_dict = update_bar_dict(bar_dict, business_urls, business_names, business_ratings, num_reviews, neighborhood_1, neighborhood_2, neighborhood_3, business_addresses, category_1, category_2, category_3)

    #Go to third and subsequent pages of search results
#    for a in range(2, 3):
#        print a

#        arrow_link = browser.find_link_by_partial_href('/search?find_desc=bars&find_loc=San+Francisco%2C+CA&start=' + str(a))
#        arrow_link.click()

#        delay = random.uniform(3,5)
#        time.sleep(delay)

#        a_list, i_list, span_list, address_list = make_tag_lists(browser)
    #business_urls, business_names, business_ratings, num_reviews, neighborhood_1, neighborhood_2, neighborhood_3, business_addresses, category_1, category_2, category_3 = get_business_attributes(a_list, i_list, span_list, address_list)
    #bar_dict = make_bar_dict(business_urls, business_names, business_ratings, num_reviews, neighborhood_1, neighborhood_2, neighborhood_3, business_addresses, category_1, category_2, category_3)
        #print json.dumps(bar_dict, sort_keys=True, indent=2)

    with open('bars_nb_test.json', 'w') as outfile:
        json.dump(bar_dict, outfile, indent=2)

    browser.quit()
    ### End scraping bar + SF search results

    ### Begin scraping review-level data

    user_dict = {}
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
        user_ids, user_names = get_user_id(r_list)
        user_locations = get_user_location(r_list)
        reviews = combine_user_reviews(reviews, user_ids, user_locations)
        user_dict[key] = reviews
        with open('user_reviews_nb_test.json', 'w') as outfile:
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
            with open('user_reviews_nb_test.json', 'w') as outfile:
                json.dump(user_dict, outfile, indent=2)

            num_reviews_page = len(user_ids)
            print 'Number of reviews on this page is ' + str(num_reviews_page)
            num_reviews_remaining = num_reviews_remaining - num_reviews_page
            print 'Number of reviews remaining after this page is ' + str(num_reviews_remaining)

            num_pages = int(round(float(num_reviews_remaining)/40 + 0.5))

            #Go to third and subsequent pages of search results
            if num_reviews_remaining > 0:
                for a in range(2, (num_pages + 2)):
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

                    with open('user_reviews_nb_test.json', 'w') as outfile:
                        json.dump(user_dict, outfile, indent=2)

            else:
                browser.quit()
        else:
            browser.quit()


    end = time.time()
    runtime = end - start
    print "runtime in minutes: " + str(runtime/60)

    return 0

if __name__ == "__main__":
    main()
