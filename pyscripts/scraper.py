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

def parse_reviews(url, bar):
    bar_reviews= {}
    ghost_id = 0
#    res = glob.glob("../raw/the-boardroom-francisco_9.html")
    res = glob.glob("../raw/" + bar['file_name'] + "_*.html")
    for fname in res:
        print 'Now parsing ' + fname
        fhandle = open(fname, 'r')
        soup = BeautifulSoup(fhandle)
        #check to make sure this won't capture ad reviews - 1/27 As far as I can tell, it does not
        user_reviews = soup.find_all("div", {"class": "review review--with-sidebar"})
        for review in user_reviews:
            user_info = review.find_all("a", {"class": "user-display-name"})
            try:
                user_id =  user_info[0]['href'][21:] #Skip the first 14 characters, which are: /user_details?
                user_name = user_info[0].text
            except IndexError:
                ghost_id += 1
                user_id = 'ghost_id_%d' % (ghost_id) 
                user_name = 'ghost_user'
            user_location = review.find_all("li", {"class": "user-location"})
            
            review_content = review.find_all("div", {"class": "review-content"})
            user_review = review_content[0].find_all('p', {"itemprop": "description"})
            review_text = ("%s" % user_review[0]).replace('<br/>', ' ').replace('<p itemprop=\"description\" lang=\"en\">', '').replace('</p>', '').strip()

            date = review_content[0].find_all("meta", {"itemprop": "datePublished"})
            review_date = date[0]['content']

            search = " star rating"
            user_stars = review_content[0].find("i")#, {"class" : "rating-very-large"})
            s = re.search("(\S*)" + search, user_stars['title'])
            user_rating = float(s.group(1))
           
            bar_reviews[user_id] = {'user_name' : user_name,
                                    "user_location": user_location[0].text.strip(),
                                    "user_rating": user_rating,
                                    "review_date": review_date,
                                    "review_text": review_text 
                                    }
        fhandle.close()
    with open('../processed/%s.json' % bar['file_name'], 'w') as outfile:
        json.dump(bar_reviews, outfile, indent=2)
    print 'saved ' + bar['file_name']+ '.json file'

    return bar_reviews

def parse_bars(bars, neighborhood): ###Some space and /n issues in the neighborhoods and categories fields - is this an issue? LF 1/26 8:30PM
    res = glob.glob("../raw/bars_%s_*.html" % neighborhood)

    for fname in res:
        fhandle = open(fname, 'r')
        soup = BeautifulSoup(fhandle)
        search_results = soup.find_all("div", {"class": "search-result natural-search-result"})
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
            if biz_hoods == []:
              # There are some bars that don't have a "neighborhood-str-list" even though they are clearly associated with a neighborhood
              hood_1 = 'none'
              hood_2 = 'none'
              hood_3 = 'none'
                    
            search = "/n"
            biz_address = result.find_all("address")
            try:
              bar_address =  ("%s" % biz_address[0]).replace('<br/>', ', ').replace('<address>', '').replace('</address>', '').strip()
            except Exception as e:
              # There has been an instance of a bar that doesn't have an address on yelp
              # So we'll skipt it
              #print "Bar %s w/o name in %s" % (biz_id.text, fname)
              continue
              #raise e

            search = ","
            biz_cats = result.find_all("span", {"category-str-list"})
            for cat in biz_cats:
                s1 = re.search("(.*)" + search + "(.*)" + search + "(.*)", cat.text)
                s2 = re.search("(.*)" + search + "(.*)", cat.text)
                if s1:
                    cat_1 = s1.group(1).strip()
                    cat_2 = s1.group(2).strip()
                    cat_3 = s1.group(3).strip()
                elif s2:
                    cat_1 = s2.group(1).strip()
                    cat_2 = s2.group(2).strip()
                    cat_3 = 'none'
                else:
                    cat_1 = cat.text.strip()
                    cat_2 = 'none'
                    cat_3 = 'none'

            try:
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
            except Exception as e:
              print biz_id.text
              print fname
              raise e

        fhandle.close()

def crawl_reviews(bar, url):
    limit = 50
    raw_base_dir = "../raw/"
    start_page = len(glob.glob('../raw/' + bar['file_name'] + '*')) + 1
    if start_page >= limit: # Limit the number of pages of reviews per bar
      print "Limiting %s to %d pages of reviews" % (url, limit)
      return
    print "Crawling %s starting from page %d" % (url, start_page)
    try:
      crawl("../raw/" + bar['file_name'] + "_%d.html", url, 40, start_page=start_page)
    except ValueError:
      sys.stdout.write("Problem parsing bar name.  Skipping")        
    # When we return from crawl, its likely that yelp cut of off, and we haven't gotten all the data yet
    # for a given bar, so move onto the next bar

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
        fhandle = open(base_name % page_num, 'w')
        fhandle.write(browser.html.encode('utf-8'))
        fhandle.close()
        time.sleep(random.uniform(3,5))
    browser.quit()

def get_reviews_in_json(bar):
  processed_base_dir = "../processed/"
  try:
    reviews = json.load(open(processed_base_dir + bar['file_name'] + '.json'))
  except IOError:
    return {}
  return reviews

def do_all_for_a_bar(url):
  bars = json.load(open('../processed/bars.json', 'r'))
  bar = bars[url]
  total_num_reviews = bar['bar_num_reviews']
  reviews = get_reviews_in_json(bar)
  num_reviews_in_json = len(reviews)
  print "The current json has %d reviews out of %d total reviews for %s" % (num_reviews_in_json, total_num_reviews, url)
  if total_num_reviews > num_reviews_in_json:
    parse_reviews(url, bars[url])
    reviews = get_reviews_in_json(bar)
    num_reviews_in_json = len(reviews)
    if total_num_reviews > num_reviews_in_json:
      crawl_reviews(bar, url)

def neighborhood_to_filename(neighborhood):
  return neighborhood.replace('+', '_').replace('%2F', '__').replace('%27', "'")

def filename_to_neighborhood(filename):
  return filename.replace("'", '%27').replace('__', '%2F').replace('_', '+')

def main():
  neighborhoods = ["Alamo+Square", "Anza+Vista", "Ashbury+Heights", "Balboa+Terrace", "Bayview-Hunters+Point", "Bernal+Heights", "Castro", "Chinatown", "Civic+Center", "Cole+Valley", "Corona+Heights", "Crocker-Amazon", "Diamond+Heights", "Dogpatch", "Duboce+Triangle", "Embarcadero", "Excelsior", "Fillmore", "Financial+District", "Fisherman%27s+Wharf", "Forest+Hill", "Glen+Park", "Hayes+Valley", "Ingleside", "Ingleside+Heights", "Ingleside+Terraces", "Inner+Richmond", "Inner+Sunset", "Japantown", "Lakeshore", "Lakeside", "Laurel+Heights", "Lower+Haight", "Lower+Nob+Hill", "Lower+Pacific+Heights", "Marina%2FCow+Hollow", "Merced+Heights", "Merced+Manor", "Miraloma+Park", "Mission", "Mission+Bay", "Mission+Terrace", "Monterey+Heights", "Mount+Davidson+Manor", "Nob+Hill", "Noe+Valley", "NoPa", "North+Beach%2FTelegraph+Hill", "Oceanview", "Outer+Mission", "Outer+Richmond", "Outer+Sunset", "Pacific+Heights", "Parkmerced", "Parkside", "Portola", "Potrero+Hill", "Presidio", "Presidio+Heights", "Russian+Hill", "Sea+Cliff", "Sherwood+Forest", "SoMa", "South+Beach", "St+Francis+Wood", "Stonestown", "Sunnyside", "Tenderloin", "The+Haight", "Twin+Peaks", "Union+Square", "Visitacion+Valley", "West+Portal", "Western+Addition", "Westwood+Highlands", "Westwood+Park"]

  if False:
    sys.stdout.write("Crawling bars for neighborhood: ")
    sys.stdout.flush()
    for neighborhood in neighborhoods:
      res = glob.glob("../raw/bars_" + neighborhood_to_filename(neighborhood) + "_*.html")
      if len(res) > 0:
        sys.stdout.write("(skipping %s) " % (neighborhood_to_filename(neighborhood)))
        continue
      url = '/search?find_desc=bars&find_loc=' + neighborhood + '%2C+San+Francisco%2C+CA'
      neighborhood = neighborhood_to_filename(neighborhood)
      sys.stdout.write("%s, " % neighborhood)
      sys.stdout.flush()
      filenames = "../raw/bars_" + neighborhood + "_%d.html"
      crawl(filenames, url, 10)
    sys.stdout.write("Done!\n")

  if True:
    sys.stdout.write("Parsing bars for neighborhood: ")
    sys.stdout.flush()
    outfile = open('../processed/bars.json', 'w')
    bars = {}
    for neighborhood in neighborhoods:
      neighborhood = neighborhood_to_filename(neighborhood)
      sys.stdout.write("%s, " % neighborhood)
      sys.stdout.flush()
      parse_bars(bars, neighborhood)
    json.dump(bars, outfile, indent=2)
    sys.stdout.write("Done!\n")
    outfile.close()
    print "We have %d bars" % len(bars)
  return 0

  if True:
    sys.stdout.write("Parsing reviews\n")
    for url in bars:
      bar = bars[url]
      num_reviews_in_json = len(get_reviews_in_json(bar))
      total_num_reviews = bar['bar_num_reviews']
      if total_num_reviews > num_reviews_in_json:
        parse_reviews(url, bars[url])

  if True:
    bars = json.load(open('../processed/bars.json'))
    for (bar_num,url) in enumerate(bars.keys()):
      bar = bars[url]
      num_reviews_in_json = len(get_reviews_in_json(bar))
      total_num_reviews = bar['bar_num_reviews']
      if total_num_reviews > num_reviews_in_json:
        print "We have %d out of %d reviews for %s" % (num_reviews_in_json, total_num_reviews, url)
        crawl_reviews(bar, url)
      else:
        print "We have all %d reviews for %s" % (num_reviews_in_json, url)

  #Need to loop over pages
  if True:
    for url in bars:
      reviews = parse_reviews(url, bars[url])

if __name__ == "__main__":
    main()
