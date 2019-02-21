#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 12:26:19 2019

@author: toddbilsborough

Finnish flashcards application with spaced repetition and retrieval of word
forms from the internet
"""

import datetime
from numpy import nan
import os
import pandas as pd
import random
from shutil import copy
from bs4 import BeautifulSoup
from requests_html import HTMLSession

# General settings
# Multiply the interval for a correct answer by this
CORRECT_INTERVAL = 1.4
# Multiply the interval for an incorrect answer by this
INCORRECT_INTERVAL = 0.5
# Lowest possible interval
MINIMUM_INTERVAL = pd.to_timedelta('1 days 00:00:00')
# Highest possible interval
MAXIMUM_INTERVAL = pd.to_timedelta('365 days 00:00:00')
# Highest interval after getting something wrong
MAX_AFTER_WRONG = pd.to_timedelta('6 days 00:00:00')

# Additional columns for nominals
NOMINAL_COLUMNS = [
        "Nominative singular",
        "English"
        ]

# Additional columns for verbs
VERB_COLUMNS = [
        "Infinitive",
        "English present",
        "English simple past",
        "English past participle",
        "English present participle"
        ]

# Columns for invariants
INVARIANT_COLUMNS = [
        "Finnish",
        "English",
        "Pre / Post",
        "Rection"
        ]

# Columns for phrases
PHRASE_COLUMNS = [
        "Finnish",
        "English"
        ]

# Statistics
STATS = [
        "Last reviewed",
        "Next review",
        "Interval",
        "Correct?",
        "Times correct",
        "Times incorrect"
        ]

# Keys: Finnish noun forms
# Values: The HTML tags used to retrieve them
NOMINAL_FORMS = {
    "Nominative plural": "form-of plural-nominative-form-of lang-fi",
    "Partitive singular": "form-of singular-partitive-form-of lang-fi",
    "Partitive plural": "form-of plural-partitive-form-of lang-fi",
    "Genitive singular": "form-of singular-genitive-form-of lang-fi",
    "Genitive plural": "form-of plural-genitive-form-of lang-fi",
    "Illative singular": "form-of singular-illative-form-of lang-fi",
    "Illative plural": "form-of plural-illative-form-of lang-fi",
    "Inessive singular": "form-of singular-inessive-form-of lang-fi",
    "Inessive plural": "form-of plural-inessive-form-of lang-fi",
    "Elative singular": "form-of singular-elative-form-of lang-fi",
    "Elative plural": "form-of plural-elative-form-of lang-fi",
    "Adessive singular": "form-of singular-adessive-form-of lang-fi",
    "Adessive plural": "form-of plural-adessive-form-of lang-fi",
    "Ablative singular": "form-of singular-ablative-form-of lang-fi",
    "Ablative plural": "form-of plural-ablative-form-of lang-fi",
    "Allative singular": "form-of singular-allative-form-of lang-fi",
    "Allative plural": "form-of plural-allative-form-of lang-fi",
    "Essive singular": "form-of singular-essive-form-of lang-fi",
    "Essive plural": "form-of plural-essive-form-of lang-fi",
    "Translative singular": "form-of singular-translative-form-of lang-fi",
    "Translative plural": "form-of plural-translative-form-of lang-fi",
    "Abessive singular": "form-of singular-abessive-form-of lang-fi",
    "Abessive plural": "form-of plural-abessive-form-of lang-fi"
    }

# Keys: Finnish verb forms
# Values: [Their English translation, associated English form]
# English form key:
# 0: Simple present / present participle
# 1: Simple present only
# 2: Simple past
# 3: Past participle
# 4: Present participle only
VERB_FORMS = {
    "First person": ["I / I am", 0],
    "First person negative": ["I don't / I'm not", 0],
    "First person perfect": ["I have", 3],
    "First person perfect negative": ["I haven't", 3],
    "Second person": ["You / You are", 0],
    "Second person negative": ["You don't / You're not", 0],
    "Second person perfect": ["You have", 3],
    "Second person perfect negative": ["You haven't", 3],
    "Third person": ["He / He is", 0],
    "Third person negative": ["She doesn't / She isn't", 0],
    "Third person perfect": ["She has", 3],
    "Third person perfect negative": ["He hasn't", 3],
    "First person plural": ["We / We are", 0],
    "First person plural negative": ["We don't / We're not", 0],
    "First person plural perfect": ["We have", 3],
    "First person plural perfect negative": ["We haven't", 3],
    "Second person plural": ["You all / You all are", 0],
    "Second person plural negative": ["You all don't / You all aren't", 0],
    "Second person plural perfect": ["You all have", 3],
    "Second person plural perfect negative": ["You all haven't", 3],
    "Third person plural": ["They / They are", 0],
    "Third person plural negative": ["They don't / They're not", 0],
    "Third person plural perfect": ["They have", 3],
    "Third person plural perfect negative": ["They haven't", 3],
    "Passive": ["One /  One is", 0],
    "Passive negative": ["One isn't / One doesn't", 0],
    "Passive perfect": ["One has", 3],
    "Passive perfect negative": ["One hasn't", 3],
    "First person past": ["I", 2],
    "First person past negative": ["I didn't", 1],
    "First person pluperfect": ["I had", 3],
    "First person pluperfect negative": ["I hadn't", 3],
    "Second person past": ["You", 2],
    "Second person past negative": ["You didn't", 1],
    "Second person pluperfect": ["You had", 3],
    "Second person pluperfect negative": ["You hadn't", 3],
    "Third person past": ["She", 2],
    "Third person past negative": ["He didn't", 1],
    "Third person pluperfect": ["He had", 3],
    "Third person pluperfect negative": ["She hadn't", 3],
    "First person past plural": ["We", 2],
    "First person past plural negative": ["We didn't", 1],
    "First person pluperfect plural": ["We had", 3],
    "First person pluperfect plural negative": ["We hadn't", 3],
    "Second person past plural": ["You all", 2],
    "Second person past plural negative": ["You all didn't", 1],
    "Second person pluperfect plural": ["You all had", 3],
    "Second person pluperfect plural negative": ["You all hadn't", 3],
    "Third person past plural": ["They", 2],
    "Third person past plural negative": ["They didn't", 1],
    "Third person pluperfect plural": ["They had", 3],
    "Third person pluperfect plural negative": ["They hadn't", 3],
    "Passive past": ["One", 2],
    "Passive past negative": ["One didn't", 1],
    "Passive pluperfect": ["One had", 3],
    "Passive pluperfect negative": ["One hadn't", 3],
    "First person conditional": ["I would", 1],
    "First person conditional negative": ["I wouldn't", 1],
    "First person conditional perfect": ["I would have", 3],
    "First person conditional perfect negative": ["I wouldn't have", 3],
    "Second person conditional": ["You would", 1],
    "Second person conditional negative": ["You wouldn't", 1],
    "Second person conditional perfect": ["You would have", 3],
    "Second person conditional perfect negative": ["You wouldn't have", 3],
    "Third person conditional": ["He would", 1],
    "Third person conditional negative": ["She wouldn't", 1],
    "Third person conditional perfect": ["She would have", 3],
    "Third person conditional perfect negative": ["He wouldn't have", 3],
    "First person conditional plural": ["We would", 1],
    "First person conditional plural negative": ["We wouldn't", 1],
    "First person conditional plural perfect": ["We would have", 3],
    "First person conditional plural perfect negative":
        ["We wouldn't have", 3],
    "Second person conditional plural": ["You all would", 1],
    "Second person conditional plural negative": ["You all wouldn't", 1],
    "Second person conditional plural perfect": ["You all would have", 3],
    "Second person conditional plural perfect negative":
        ["You all wouldn't have", 3],
    "Third person conditional plural": ["They would", 1],
    "Third person conditional plural negative": ["They wouldn't", 1],
    "Third person conditional plural perfect": ["They would have", 3],
    "Third person conditional plural perfect negative":
        ["They wouldn't have", 3],
    "Passive conditional": ["One would", 1],
    "Passive conditional negative": ["One wouldn't", 1],
    "Passive conditional perfect": ["One would have", 3],
    "Passive conditional perfect negative": ["One wouldn't have", 3],
    "Second person imperative": ["(You)", 1],
    "Second person imperative negative": ["Don't", 1],
    "Second person imperative perfect": ["You must have", 3],
    "Second person imperative perfect negative": ["You musn't have", 3],
    "Third person imperative": ["She must", 1],
    "Third person imperative negative": ["He musn't", 1],
    "Third person imperative perfect": ["He must have", 3],
    "Third person imperative perfect negative": ["She musn't have", 3],
    "First person imperative plural": ["Let's", 1],
    "First person imperative plural negative": ["Let's not", 1],
    "First person imperative plural perfect": ["Let's have", 3],
    "First person imperative plural perfect negative": ["Let's not have", 3],
    "Second person imperative plural": ["(You all)", 1],
    "Second person imperative plural negative": ["(You all) don't", 1],
    "Second person imperative plural perfect": ["(You all) have ___ done", 4],
    "Second person imperative plural perfect negative":
        ["(You all) don't have ___ done", 4],
    "Third person imperative plural": ["They must", 1],
    "Third person imperative plural negative": ["They musn't", 1],
    "Third person imperative plural perfect": ["They must have", 3],
    "Third person imperative plural perfect negative":
        ["They musn't have", 3],
    "Passive imperative": ["One must", 1],
    "Passive imperative negative": ["One musn't", 1],
    "Passive imperative perfect": ["One must have", 3],
    "Passive imperative perfect negative": ["One musn't have", 3],
    "First person potential": ["I could", 1],
    "First person potential negative": ["I couldn't", 1],
    "First person potential perfect": ["I could have", 3],
    "First person potential perfect negative": ["I couldn't have", 3],
    "Second person potential": ["You could", 1],
    "Second person potential negative": ["You couldn't", 1],
    "Second person potential perfect": ["You could have", 3],
    "Second person potential perfect negative": ["You couldn't have", 3],
    "Third person potential": ["She could", 1],
    "Third person potential negative": ["He couldn't", 1],
    "Third person potential perfect": ["He could have", 3],
    "Third person potential perfect negative": ["He couldn't have", 3],
    "First person potential plural": ["We could", 1],
    "First person potential plural negative": ["We couldn't", 1],
    "First person potential plural perfect": ["We could have", 3],
    "First person potential plural perfect negative": ["We couldn't have", 3],
    "Second person potential plural": ["You all could", 1],
    "Second person potential plural negative": ["You all couldn't", 1],
    "Second person potential plural perfect": ["You all could have", 3],
    "Second person potential plural perfect negative":
        ["You all couldn't have", 3],
    "Third person potential plural": ["They could", 1],
    "Third person potential plural negative": ["They couldn't", 1],
    "Third person potential plural perfect": ["They could have", 3],
    "Third person potential plural perfect negative":
        ["They couldn't have", 3],
    "Passive potential": ["One could", 1],
    "Passive potential negative": ["One couldn't", 1],
    "Passive potential perfect": ["One could have", 3],
    "Passive potential perfect negative": ["One wouldn't have", 3],
    "1st infinitive": ["[skip]", nan],
    "Present active participle": ["-ing", 4],
    "Present passive participle": ["Which is to be", 3],
    "A infinitive, long form": ["[skip]", nan],
    "Past active participle": ["Did this:", 1],
    "Past passive participle": ["Which is to be done by one:", 0],
    "E infinitive inessive": ["When someone does this:", 0],
    "E infinitive inessive passive": ["When one does this:", 0],
    "Agent participle": ["Past adjectival form:", 0],
    "E infinitive instructive": ["Doing:", 4],
    "Negative participle": ["Without:", 4],
    "MA infinitive inessive": ["Ongoing action or process:", 4],
    "MA infinitive elative": ["From doing this:", 4],
    "MA infinitive illative": ["About to begin", 4],
    "MA infinitive adessive": ["By doing this:", 4],
    "MA infinitive abessive": ["Without doing this: ", 4],
    "MA infinitive instructive": ["Solemn necessity:", 4],
    "MA infinitive instructive passive": ["One's solemn necessity:", 1],
    "MINEN infinitive nominative": ["[skip]", nan],
    "MINEN infinitive partitive": ["[skip]", nan],
    "5th infinitive": ["[skip]", nan]
    }

def backup_files():
    """Backs up data files"""
    ts = datetime.datetime.today()
    day = ts.day if int(ts.day) > 9 else "0{}".format(ts.day)
    month = ts.month if int(ts.month) > 9 else "0{}".format(ts.month)
    timestamp = "_{}{}{}".format(ts.year, month, day)
    newpath = r'backups/backup{}/'.format(timestamp) 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    print(r"Backing up data files to /backups/backup{}".format(timestamp))
    copy('verbs.csv', newpath)
    copy('nominals.csv', newpath)
    copy('invariants.csv', newpath)
    copy('phrases.csv', newpath)
    print("Backup completed")

def load_invariants():
    """Loads the invariants file"""
    invariants = pd.read_csv('invariants.csv',
                            index_col='Finnish',
                            parse_dates=['Last reviewed', 'Next review'],
                            infer_datetime_format=True)
    invariants.sort_index(inplace=True)
    return invariants

def load_nominals():
    """Load the nominals file"""
    nominals = pd.read_csv('nominals.csv',
                        index_col="Nominative singular",
                        parse_dates=["Last reviewed", "Next review"],
                        infer_datetime_format=True)
    nominals.sort_index(inplace=True)
    return nominals

def load_verbs():
    """Loads the verbs file"""
    verbs = pd.read_csv('verbs.csv',
                        index_col="Infinitive",
                        parse_dates=["Last reviewed", "Next review"],
                        infer_datetime_format=True)
    verbs.sort_index(inplace=True)
    return verbs

def load_phrases():
    """Loads the phrases file"""
    phrases = pd.read_csv('phrases.csv', 
                          index_col=0,
                          parse_dates=["Last reviewed", "Next review"],
                          infer_datetime_format=True)
    phrases.sort_index(inplace=True)
    return phrases

def save_invariant(invariant=None, english=None):
    """Save an invariant and at it to the file"""
    if invariant is None:
        invariant = input("Invariant (Finnish): ")
    if english is None:
        english = input("English translation of {}: ".format(invariant))
    last_reviewed = pd.Timestamp(pd.to_datetime(datetime.datetime.now()))
    next_review = pd.Timestamp(pd.to_datetime(datetime.datetime.now()))
    interval = pd.to_timedelta("1 days")
    correct = True
    times_correct = 0
    times_incorrect = 0
    stats = [last_reviewed, next_review, interval, correct, times_correct,
             times_incorrect]
    pre_post = input("Pre or post? ").lower()
    rection = input("Rection: ").lower()
    data = [invariant, english, pre_post, rection] + stats
    columns = INVARIANT_COLUMNS + STATS
    entry = pd.DataFrame(data=[data], columns=columns)
    entry.set_index(keys="Finnish", inplace=True)
    invariants = load_invariants()
    invariants = invariants.append(entry, verify_integrity=True)
    conf = input("Adding {}. Continue? ".format(invariant)).lower()
    if conf == 'y':
        invariants.to_csv('invariants.csv')
        print("File saved")
        return True
    else:
        return None
    
def save_nominal(nominal=None, english=None, forms=None):
    """Save a nominal and its forms to the file"""
    if nominal is None:
        nominal = input("Nominal (Finnish): ")
    if english is None:
        english = input("English translation of {}: ".format(nominal))
    if forms is None:
        forms = retrieve_nominal(nominal, skip_save=True)
    last_reviewed = pd.Timestamp(pd.to_datetime(datetime.datetime.now()))
    next_review = pd.Timestamp(pd.to_datetime(datetime.datetime.now()))
    interval = pd.to_timedelta("1 days")
    correct = True
    times_correct = 0
    times_incorrect = 0
    stats = [last_reviewed, next_review, interval, correct, times_correct,
             times_incorrect]
    data = [nominal, english] + forms + stats
    columns = NOMINAL_COLUMNS + list(NOMINAL_FORMS.keys()) + STATS
    entry = pd.DataFrame(data=[data], columns=columns)
    entry.set_index(keys="Nominative singular", inplace=True)
    nominals = load_nominals()
    nominals = nominals.append(entry, verify_integrity=True)
    conf = input("Adding {}. Continue? ".format(nominal)).lower()
    if conf == 'y':
        nominals.to_csv('nominals.csv')
        print("File saved")
        return True
    else:
        return None
    
def save_verb(verb=None, english=None, forms=None):
    """Save a verb and its forms to the file"""
    if verb is None:
        verb = input("Verb (Finnish): ")
    if english is None:
        e_present = input("English present: ")
        e_simple_past = input("English simple past: ")
        e_past_part = input("English past participle: ")
        e_present_part = input("English present participle: ")
    if (english is not None and not 
        isinstance(english, list) and 
        len(english) != 4):
        print("Wrong number of entries in English list")
        return None
    if english is not None:
        e_present = english[0]
        e_simple_past = english[1]
        e_past_part = english[2]
        e_present_part = english[3]
    if forms is None:
        forms = retrieve_verb(verb, skip_save=True)
    last_reviewed = pd.Timestamp(pd.to_datetime(datetime.datetime.now()))
    next_review = pd.Timestamp(pd.to_datetime(datetime.datetime.now()))
    interval = pd.to_timedelta("1 days")
    correct = True
    times_correct = 0
    times_incorrect = 0
    stats = [last_reviewed, next_review, interval, correct, times_correct,
             times_incorrect]
    data = [verb, e_present, e_simple_past, e_past_part, 
            e_present_part] + forms + stats
    columns = VERB_COLUMNS + list(VERB_FORMS.keys()) + STATS
    entry = pd.DataFrame(data=[data], columns=columns)
    entry.set_index(keys="Infinitive", inplace=True)
    verbs = load_verbs()
    verbs = verbs.append(entry, verify_integrity=True)
    conf = input("Adding {}. Continue? ".format(verb)).lower()
    if conf == 'y':
        verbs.to_csv('verbs.csv')
        print("File saved")
        return True
    else:
        return None
    
def save_phrase(phrase=None, english=None):
    """Save a phrase to the file"""
    if phrase is None:
        finnish = input("Phrase (Finnish): ").lower()
    if english is None:
        english = input("English: ").lower()
    last_reviewed = pd.Timestamp(pd.to_datetime(datetime.datetime.now()))
    next_review = pd.Timestamp(pd.to_datetime(datetime.datetime.now()))
    interval = pd.to_timedelta("1 days")
    correct = True
    times_correct = 0
    times_incorrect = 0
    stats = [last_reviewed, next_review, interval, correct, times_correct,
             times_incorrect]
    data = [finnish, english] + stats
    columns = PHRASE_COLUMNS + STATS
    entry = pd.DataFrame(data=[data], columns=columns)
    phrases = load_phrases()
    phrases = phrases.append(entry)
    phrases.reset_index(drop=True, inplace=True)
    conf = input("Adding phrase. Continue? ").lower()
    if conf == 'y':
        phrases.to_csv('phrases.csv')
        print("File saved")
        return True
    else:
        return None

def retrieve_nominal(nominal, skip_save=False):
    """Get a noun's forms from wiktionary"""
    session = HTMLSession()
    link_string = "https://en.wiktionary.org/wiki/{}".format(nominal)
    try:
        r = session.get(link_string)
    except Exception as ex:
        print("There was a problem getting the web page: {}".format(ex))
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    forms = []
    for key, value in NOMINAL_FORMS.items():
        try:
            span = soup.find(class_=value)
            link = span.find('a')
            form = link['title'].split(" ")[0]
            forms.append(form)
        except Exception as ex:
            print("There was a problem finding {}: {}".format(key, ex))
            forms.append("")
            continue
    print(*forms, sep=', ')
    conf = input("Correct? ").lower()
    if conf != 'y':
        return None
    nominals = load_nominals()
    if not skip_save and nominal not in nominals.index:
        conf = input("No entry for {} in file. Add? ".format(nominal)).lower()
        if conf == 'y':
            save_nominal(nominal, forms=forms)
    return forms

def retrieve_verb(verb, skip_save=False):
    """Get a verb's forms from wiktionary"""
    session = HTMLSession()
    link_string = "https://en.wiktionary.org/wiki/{}".format(verb)
    try:
        r = session.get(link_string)
    except Exception as ex:
        print("There was a problem getting the web page: {}".format(ex))
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    spans=soup.find_all(lang='fi')
    adding = False
    forms = []
    for span in spans:
        # First valid entry will be first person singular 
        # which will always end in an 'n'
        if span.text[-1] == 'n' and span.parent.name == 'td':
            adding = True
        if adding:
            forms.append(span.text)
    # There are extraneous entries at the end
    forms = forms[:157]
    print(*forms, sep=', ')
    conf = input("Correct? ").lower()
    if conf != 'y':
        return None
    verbs = load_verbs()
    if not skip_save and verb not in verbs.index:
        conf = input("No entry for {} in file. Add? ".format(verb)).lower()
        if conf == 'y':
            save_verb(verb, forms=forms)
    return forms

def add_words():
    """Looping function for adding words"""
    running = True
    while running:
        word = input("Word: ").lower()
        if word == 'q':
            return None
        cat = ""
        while cat not in ['invariant', 'nominal', 'verb']:
            cat = input("Category: ").lower()
        if cat == 'invariant':
            save_invariant(invariant=word)
        elif cat == 'nominal':
            save_nominal(nominal=word)
        elif cat == 'verb':
            save_verb(verb=word)

def edit_word(word=None, cat=None):
    """Edit an word entry"""
    if word is None:
        word = input("Word (Finnish): ").lower()
    if cat is None:
        cat = ""
        while cat not in ['invariant', 'nominal', 'verb']:
            cat = input("Category: ").lower()
    if cat == 'invariant':
        words = load_invariants()
        save_string = 'invariants.csv'
    elif cat == 'nominal':
        words = load_nominals()
        save_string = 'nominals.csv'
    elif cat == 'verb':
        words = load_verbs()
        save_string = 'verbs.csv'
    if word not in words.index():
        print("No entry for {}".format(word))
        return None
    current_english = words.loc[word, 'english']
    print("{}: {}".format(word, current_english))
    new_english = input("New value: ").lower()
    print("{}: {}".format(word, new_english))
    conf = input("Update entry?: ").lower()
    if conf == 'y':
        words.loc[word, 'english'] = new_english
        words.to_csv(save_string)
        print("File saved")
        return True

def edit_phrase(search=None, cat=None):
    """Edit a phrase entry"""
    if search is None:
        search = input("Search (English): ").lower()
    phrases = load_phrases()
    english_list = list(phrases['English'])
    matches = []
    for english in english_list:
        if search in english:
            matches.append(english)
            finnish = list(phrases[phrases['English'] == 
                                   english]['Finnish'])[0]
            print("{}. {}: {}".format(len(matches), english, finnish))
    selection = -1
    while selection not in range(1, len(matches)+1):
        selection = int(input("Selection: "))
    english = matches[selection-1]
    new_finnish = input("New Finnish: ").lower()
    index = phrases[phrases['English'] == english].index.values[0]
    print("{}: {}".format(english, new_finnish))
    conf = input("Update entry?: ").lower()
    if conf == 'y':
        phrases.loc[index, 'Finnish'] = new_finnish
        phrases.to_csv('phrases.csv')
        print("File saved")
        return True

def generate_words_list(load_all=True):
    """Generate a list of words to review"""
    invariants = load_invariants()
    nominals = load_nominals()
    verbs = load_verbs()
    now = pd.to_datetime(datetime.datetime.now())
    invariants_to_review = [[word, 'invariant'] for
                            word in list(invariants.index) if
                            now > invariants.loc[word, 'Next review']]
    nominals_to_review = [[word, 'nominal'] for
                          word in list(nominals.index) if
                          now > nominals.loc[word, 'Next review']]
    verbs_to_review = [[word, 'verb'] for
                       word in list(verbs.index) if
                       now > verbs.loc[word, 'Next review']]
    words = invariants_to_review + nominals_to_review + verbs_to_review
    if load_all:
        return words, invariants, nominals, verbs
    else:
        return words
    
def generate_phrases_list():
    """Generate a list of phrases to review"""
    phrases = load_phrases()
    now = pd.to_datetime(datetime.datetime.now())
    phrases_to_review = [phrase_i for phrase_i in list(phrases.index) if
                            now > phrases.loc[phrase_i, 'Next review']]
    return phrases_to_review

def process_correct(word, words_df, cat):
    """Process a correct answer"""
    print("Correct")
    words_df.loc[word, 'Last reviewed'] = pd.to_datetime(datetime
                  .datetime.now())
    # Do not increase the interval if the word was previously incorrect
    if words_df.loc[word, 'Correct?']:
        words_df.loc[word, 'Interval'] = (pd.to_timedelta(words_df.loc[word, 
                    'Interval']) * CORRECT_INTERVAL)
        # Make sure the interval doesn't exceed the max
        if pd.to_timedelta(words_df.loc[word, 'Interval']) > MAXIMUM_INTERVAL:
            words_df.loc[word, 'Interval'] = MAXIMUM_INTERVAL
    words_df.loc[word, 'Next review'] = (
            pd.to_datetime(datetime.datetime.now() + 
                           pd.to_timedelta(words_df.loc[word, 'Interval'])))
    words_df.loc[word, 'Correct?'] = True
    words_df.loc[word, 'Times correct'] += 1
    if cat == 'invariant':
        words_df.to_csv('invariants.csv')
    elif cat == 'nominal':
        words_df.to_csv('nominals.csv')
    elif cat == 'verb':
        words_df.to_csv('verbs.csv')
    elif cat == 'phrase':
        words_df.to_csv('phrases.csv')
    return True

def process_incorrect(word, words_df, cat):
    """Process an incorrect answer"""
    if cat == 'invariant' or cat == 'nominal':
        print("Incorrect. {} is {}".format(words_df.loc[word,
              'English'], word))
    elif cat == 'verb':
        print("Incorrect. {} is {}".format(words_df.loc[word,
              'English present'], word))
    elif cat == 'phrase':
        print("Incorrect. {}\nis\n{}".format(words_df.loc[word, 'English'],
              words_df.loc[word, 'Finnish']))
    words_df.loc[word, 'Last reviewed'] = pd.to_datetime(datetime
                  .datetime.now())
    if (pd.to_timedelta(words_df.loc[word, 'Interval']) > 
        pd.to_timedelta('1 days')):
        words_df.loc[word, 'Interval'] = (pd.to_timedelta(words_df.loc[word, 
                    'Interval']) * INCORRECT_INTERVAL)
        # Make sure interval is not less than the minimum
        if pd.to_timedelta(words_df.loc[word, 'Interval']) < MINIMUM_INTERVAL:
            words_df.loc[word, 'Interval'] = MINIMUM_INTERVAL
        # Make sure interval is not greater than the maximum after wrong
        if pd.to_timedelta(words_df.loc[word, 'Interval']) > MAX_AFTER_WRONG:
            words_df.loc[word, 'Interval'] = MAX_AFTER_WRONG
    words_df.loc[word, 'Correct?'] = False
    words_df.loc[word, 'Times incorrect'] += 1
    if cat == 'invariant':
        words_df.to_csv('invariants.csv')
    elif cat == 'nominal':
        words_df.to_csv('nominals.csv')
    elif cat == 'verb':
        words_df.to_csv('verbs.csv')
    elif cat == 'phrase':
        words_df.to_csv('phrases.csv')
    return True
        
def flash_invariant(word, invariants):
    """Do an invariant flashcard"""
    english = invariants.loc[word, 'English']
    print(english)
    answer = input("Soumeksi: ").lower()
    if answer == 'q':
        return False
    correct = True if answer == word else False
    if correct:
        process_correct(word, invariants, cat='invariant')
    else:
        process_incorrect(word, invariants, cat='invariant')
    answer = input("Use in a sentence:\n")
    if answer == 'q':
        return False
    return True

def flash_nominal(word, nominals):
    """Do a nominal flashcard"""
    english = nominals.loc[word, 'English']
    print(english)
    answer = input("Suomeksi: ").lower()
    if answer == 'q':
        return False
    correct = True if answer == word else False
    if correct:
        process_correct(word, nominals, cat='nominal')
    else:
        process_incorrect(word, nominals, cat='nominal')
    form_name = random.choice(list(NOMINAL_FORMS.keys()))
    form_value = nominals.loc[word, form_name]
    answer = input("{}: ".format(form_name)).lower()
    if answer == 'q':
        return False
    if answer == form_value:
        print("Correct")
    else:
        print("Incorrect. {} of {} is {}".format(form_name, word, form_value))
    answer = input("Use in a sentence:\n")
    if answer == 'q':
        return False
    return True
        
def flash_verb(word, verbs):
    """Do a verb flashcard"""
    english = verbs.loc[word, 'English present']
    print("To {}".format(english))
    answer = input("Soumeksi: ").lower()
    if answer == 'q':
        return False
    correct = True if answer == word else False
    if correct:
        process_correct(word, verbs, cat='verb')
    else:
        process_incorrect(word, verbs, cat='verb')
    form_choices = [form for form in VERB_FORMS.keys() if 
                    VERB_FORMS[form] != "[skip]"]
    form_name = random.choice(form_choices)
    form_value = verbs.loc[word, form_name]
    if VERB_FORMS[form_name][1] == 0:
        verb_phrase_subjects = VERB_FORMS[form_name][0].split(" / ")
        english_verb_phrase = "{} - \"{} {} / {} {}\"".format(form_name,
                               verb_phrase_subjects[0],
                               verbs.loc[word, 'English present'],
                               verb_phrase_subjects[1],
                               verbs.loc[word, 'English present participle'])
    elif VERB_FORMS[form_name][1] == 1:
        english_verb_phrase = "{} - \"{} {}\"".format(form_name,
                               VERB_FORMS[form_name][0],
                               verbs.loc[word, 'English present'])
    elif VERB_FORMS[form_name][1] == 2:
        english_verb_phrase = "{} - \"{} {}\"".format(form_name,
                               VERB_FORMS[form_name][0],
                               verbs.loc[word, 'English simple past'])
    elif VERB_FORMS[form_name][1] == 3:
        english_verb_phrase = "{} - \"{} {}\"".format(form_name,
                               VERB_FORMS[form_name][0],
                               verbs.loc[word, 'English past participle'])
    elif VERB_FORMS[form_name][1] == 4:
        english_verb_phrase = "{} - \"{} {}\"".format(form_name,
                               VERB_FORMS[form_name][0],
                               verbs.loc[word, 'English present participle'])
    answer = input("{}: ".format(english_verb_phrase)).lower()
    if answer == 'q':
        return False
    if answer == form_value:
        print("Correct")
    else:
        print("Incorect. {} of {} is {}".format(form_name, word,
              form_value))
    answer = input("Use in a sentence:\n")
    if answer == 'q':
        return False
    return True

def flash_phrase(phrase_i, phrases):
    """Do a phrase flashcard"""
    english = phrases.loc[phrase_i, 'English']
    print(english)
    answer = input("Soumeksi: ").lower()
    if answer == 'q':
        return False
    if answer == phrases.loc[phrase_i, 'Finnish']:
        process_correct(phrase_i, phrases, cat='phrase')
    else:
        process_incorrect(phrase_i, phrases, cat='phrase')
    return True

def flashcards():
    """The core flashcards function"""
    words, invariants, nominals, verbs = generate_words_list()
    random.shuffle(words)
    for word in words:
        if word[1] == 'invariant':
            if not flash_invariant(word[0], invariants):
                print("Quitting")
                return None
        elif word[1] == 'nominal':
            if not flash_nominal(word[0], nominals):
                print("Quitting")
                return None
        elif word[1] == 'verb':
            if not flash_verb(word[0], verbs):
                print("Quitting")
                return None
    print("No more flashcards")
    
def phrasecards():
    """Flashcards for phrases"""
    phrase_indices = generate_phrases_list()
    phrases = load_phrases()
    random.shuffle(phrase_indices)
    for phrase_i in phrase_indices:
        if not flash_phrase(phrase_i, phrases):
            print("Quitting")
            return None
    print("No more flashcards")