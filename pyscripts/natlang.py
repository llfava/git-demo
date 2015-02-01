#!/usr/bin/python
import sys
import nltk
import json

from sklearn.feature_extraction.text import TfidfVectorizer

def text2pos(string):
    """
    Convert text input to part of speech tags.
    """
    pos_tags = []

    # Split string into sentences and operate on each sentence
    sentences = nltk.sent_tokenize(string)
    for sentence in sentences:
        tokens = nltk.word_tokenize(sentence)
        tokens = [x.lower() for x in tokens]
        pos_tags.extend(nltk.pos_tag(tokens))

    return pos_tags


def pos2lemmas(pos_tags):
    """
    Return list of word, pos-tags in which each word has been lemmatized.
    pos_tags is a list of word, pos-tag pairs returned by text2pos.
    """

    from nltk.corpus import wordnet as wn

    # Lemmatizer to use
    wnl = nltk.stem.WordNetLemmatizer()

    # mapping of PennTreebank part of speech tags to input for lemmatizer
    pos_mapper = {'NN':wn.NOUN,'VB':wn.VERB,'JJ':wn.ADJ,'RB':wn.ADV}

    lemmas = []
    pos    = []
    for pair in pos_tags:

        # Include pos tags when lemmatizing nouns, verbs, adjectives, and adverbs
        if pair[1][0:2] in pos_mapper.keys():
            thispos = pos_mapper[pair[1][0:2]]
            thislemma = wnl.lemmatize(pair[0],thispos)
        else:
            thispos = pair[1]
            thislemma = wnl.lemmatize(pair[0])
        lemmas.append(thislemma)
        pos.append(thispos)

    return (lemmas, pos)


def handle_negation(lemmas,pos):
    """
    If "not" or "n't" occurs immediately before a verb or adjective,
    replace the verb or adjective with not_verb or not_adjective
    """

    from nltk.corpus import wordnet as wn

    # Prepend "not_" to words following "not" or "n't"
    not_index = []
    for ii in range(1,len(lemmas)):
        if (lemmas[ii-1].lower() in ["not","n't"]) & (pos[ii] in [wn.VERB,wn.ADJ]):
            lemmas[ii] = 'not_' + lemmas[ii]
            not_index.append(ii-1)
    
    # Remove instances of "not" and "n't"
    lemmas = [value for index,value in enumerate(lemmas) if index not in not_index]
    pos    = [value for index,value in enumerate(pos) if index not in not_index]

    return lemmas,pos


def addNgrams(lemmas,pos,N_gram,N_return=20,min_occur=3):
    """
    Adds N_return most common N-grams to the lemmas already created.
    N-grams must occur at least min_occur times.

    lemmas - list of lemmas as returned by pos2lemmas or handle_negation
    pos - list of parts of speech as returned by pos2lemmas or handle_negation
    N_gram - integer (2 or 3 currently supported). return N-grams
    N_return - Return N_return most common N-grams
    min_occur - Filter out N-grams that occur less than min_occur times
    """

    from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
    from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures

    # Determine whether finding bi or tri grams
    if N_gram==2: 
        finder = BigramCollocationFinder.from_words(lemmas)
        test   = BigramAssocMeasures.chi_sq
    if N_gram==3: 
        finder = TrigramCollocationFinder.from_words(lemmas)
        test   = TrigramAssocMeasures.chi_sq

    # Find N-grams
    finder.apply_freq_filter(min_occur)
    try:
        ngrams = finder.nbest(test,N_return)
    except:
        ngrams = []

    # Add N grams to list of lemmas, replacing the adjacent terms that form the N grams
    for gram in ngrams:
        lemmas.append('_'.join(gram))
        pos.append(str(N_gram)+'gram')

    return lemmas, pos


def remove_pos(lemmas,pos,keep=[]):
    """
    Remove lemmas with parts of speech in the list remove.
    
    lemmas - list of lemmas as returned by pos2lemmas, 
             handle_negation, or addNgrams
    pos - list of parts of speech as returned by pos2lemmas, 
          handle_negation, or addNgrams
    keep - list of parts of speech to keep from the list of lemmas
    """

    temp = [(l,p) for l,p in zip(lemmas,pos) if p in keep]
    if len(temp)!=0: 
        new_lemmas, new_pos = zip(*temp)
    else:
        new_lemmas = lemmas
        new_pos = pos
    return new_lemmas, new_pos

def remove_punctuation(lemmas,pos):
    """
    Return lemma and pos lists with all items removed that contain 
    punctuation (other than an apostraphe and underscore).
    """

    import string
    import re

    table = string.maketrans("","")
    punct = string.punctuation
    keep = ["'","_"]
    for k in keep:
        punct = punct.replace(k,'')

    regex = re.compile('[%s]' % re.escape(punct))
    newlemmas = [regex.sub('',l) for l in lemmas]

    # Remove empty strings
    try:
        temp = [(l,p) for l,p in zip(newlemmas,pos) if l!=""]
        newlemmas, newpos = zip(*temp)
        newlemmas = list(newlemmas)
        newpos = list(newpos)
    except:
        nostrings_here = True
        newlemmas = []
        newpos = []

    return newlemmas, newpos

def text2lemmas(string):
    """
    Converts a string of text into a list of lemmas extracted from the text.
    """
    from nltk.corpus import wordnet as wn

    # Array to hold lemmas for output
    lemmas = []

    # Calculate pos_tag for each word in the string
    pos_tags = text2pos(string)

    # Lemmatize each word in the string
    lemmas, pos = pos2lemmas(pos_tags)

    # Remove lemmas with punctuation
    lemmas, pos = remove_punctuation(lemmas,pos)

    # Negation handling
    #   If "not" or "n't" occurs immediately before a verb or adjective,
    #   replace the verb or adjective with not_verb or not_adjective
    lemmas,pos = handle_negation(lemmas,pos)

    # N-gram identification
    lemmas, pos = addNgrams(lemmas,pos,2)   # bigrams
    lemmas, pos = addNgrams(lemmas,pos,3)   # trigrams

    # Remove parts of speech that are not noun, verb, adjective, adverb, or Ngram
    lemmas, pos = remove_pos(lemmas,pos,keep=[wn.NOUN,wn.VERB,wn.ADJ,wn.ADV,'2gram','3gram'])

    return lemmas

def create_corpus(bars):
  root = "../processed/"
  total_reviews = 0
  local_reviews = 0
  tourist_reviews = 0
  fh_local = open(root + 'corpus_local.txt', 'w')
  fh_tourist = open(root + 'corpus_tourist.txt', 'w')
  for bar in bars:
    print bar
    reviews = json.loads(open(root + bars[bar]['file_name'] + '_nb.json').read())
    for reviewer in reviews:
      if reviews[reviewer]['user_location'] == 'San Francisco, CA':
        local_reviews += 1
        try:
          fh_local.write(reviews[reviewer]['review_text'].encode('utf8') + '\n')
        except UnicodeEncodeError:
          print bar
          print reviewer
      else:
        tourist_reviews += 1
        try:
          fh_tourist.write(reviews[reviewer]['review_text'].encode('utf8') + '\n')
        except UnicodeEncodeError:
          print bar
          print reviewer
      #print reviews[reviewer]['review_text']
      total_reviews += 1
      #print reviewer
  fh_local.close()
  fh_tourist.close()
  print total_reviews
  print local_reviews
  print tourist_reviews

def main(argv):
  root = "../processed/"

  json_bars = root + 'bars_nb_rated_prelim.json'
  bars = json.loads(open(json_bars).read())
  if False:
    create_corpus(bars) 

  fh_local = open(root + 'corpus_local_tiny.txt', 'r')
  fh_tourist = open(root + 'corpus_tourist_tiny.txt', 'r')
  tfidf = TfidfVectorizer(tokenizer=text2lemmas)
  tfs = tfidf.fit_transform(fh_local)
  response = tfidf.transform(fh_tourist)
  print response
  print
  print response.nonzero()
  feature_names = tfidf.get_feature_names()
  #print feature_names
  #for col in response.nonzero()[1]:
  #  print feature_names[col], ' - ', response[0, col]
  
  return 0

  reviews = { 'local' : [], 'tourist' : [] }
  lemmas_per_review = { 'local' : [], 'tourist' : [] }

  reviews['local'].append("""Pros: This little neighborhood cafe has great snacks and it's usually empty enough for the wifi to seem fast and for it to be quiet :)

Cons: The lighting is not that appropriate for working on the laptop for a long time, but you can easily fix that by sitting close to the windows!""")

  reviews['tourist'].append("""We wanted to sit down for a cup off coffee walking away from pier 39 and walking towards Chinatown we found this small coffee shop, which is hard now to find

Wonderful service and nice variety of coffee and espresso.""")

  for location in reviews.keys():
    for review in reviews[location]:
      lemmas_per_review[location].append(text2lemmas(review))
  #print lemmas

  location_word = []
  for location in lemmas_per_review.keys():
    for lemmas in lemmas_per_review[location]:
      for lemma in lemmas:
        location_word.append( (location, lemma) )
  print location_word 

  cfd = nltk.ConditionalFreqDist(location_word) 
  print cfd.conditions()

  

if __name__ == "__main__":
  sys.exit(main(sys.argv))
