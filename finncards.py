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
from shutil import copy
from bs4 import BeautifulSoup
from requests_html import HTMLSession

# Additional columns for nouns
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

# Statistics
STATS = [
        "Last reviewed",
        "Next review",
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
# Values: Their English translation
VERB_FORMS = {
    "First person": "I / I am",
    "First person negative": "I don't / I'm not",
    "First person perfect": "I have",
    "First person perfect negative": "I haven't",
    "Second person": " You / You are",
    "Second person negative": "You don't / You're not",
    "Second person perfect": "You have",
    "Second person perfect negative": "You haven't",
    "Third person": "He / He is",
    "Third person negative": "She doesn't / She isn't",
    "Third person perfect": "She has",
    "Third person perfect negative": "He hasn't",
    "First person plural": "We / We are",
    "First person plural negative": "We don't / We're not",
    "First person plural perfect": "We have",
    "First person plural perfect negative": "We haven't",
    "Second person plural": "You all / You all are",
    "Second person plural negative": "You all don't / You all aren't",
    "Second person plural perfect": "You all have",
    "Second person plural perfect negative": "You all haven't",
    "Third person plural": "They / They are",
    "Third person plural negative": "They don't / They're not",
    "Third person plural perfect": "They have",
    "Third person plural perfect negative": "They haven't",
    "Passive": "One /  One is",
    "Passive negative": "One isn't / One doesn't",
    "Passive perfect": "One has",
    "Passive perfect negative": "One hasn't",
    "First person past": "I",
    "First person past negative": "I didn't",
    "First person pluperfect": "I had",
    "First person pluperfect negative": "I hadn't",
    "Second person past": "You",
    "Second person past negative": "You didn't",
    "Second person pluperfect": "You had",
    "Second person pluperfect negative": "You hadn't",
    "Third person past": "She",
    "Third person past negative": "He didn't",
    "Third person pluperfect": "He had",
    "Third person pluperfect negative": "She hadn't",
    "First person past plural": "We",
    "First person past plural negative": "We didn't",
    "First person pluperfect plural": "We had",
    "First person pluperfect plural negative": "We hadn't",
    "Second person past plural": "You all",
    "Second person past plural negative": "You all didn't",
    "Second person pluperfect plural": "You all had",
    "Second person pluperfect plural negative": "You all hadn't",
    "Third person past plural": "They",
    "Third person past plural negative": "They didn't",
    "Third person pluperfect plural": "They had",
    "Third person pluperfect plural negative": "They hadn't",
    "Passive past": "One",
    "Passive past negative": "One didn't",
    "Passive pluperfect": "One had",
    "Passive pluperfect negative": "One hadn't",
    "First person conditional": "I would",
    "First person conditional negative": "I wouldn't",
    "First person conditional perfect": "I would have",
    "First person conditional perfect negative": "I wouldn't have",
    "Second person conditional": "You would",
    "Second person conditional negative": "You wouldn't",
    "Second person conditional perfect": "You would have",
    "Second person conditional perfect negative": "You wouldn't have",
    "Third person conditional": "He would",
    "Third person conditional negative": "She wouldn't",
    "Third person conditional perfect": "She would have",
    "Third person conditional perfect negative": "He wouldn't have",
    "First person conditional plural": "We would",
    "First person conditional plural negative": "We wouldn't",
    "First person conditional plural perfect": "We would have",
    "First person conditional plural perfect negative": "We wouldn't have",
    "Second person conditional plural": "You all would",
    "Second person conditional plural negative": "You all wouldn't",
    "Second person conditional plural perfect": "You all would have",
    "Second person conditional plural perfect negative":
        "You all wouldn't have",
    "Third person conditional plural": "They would",
    "Third person conditional plural negative": "They wouldn't",
    "Third person conditional plural perfect": "They would have",
    "Third person conditional plural perfect negative": "They wouldn't have",
    "Passive conditional": "One would",
    "Passive conditional negative": "One wouldn't",
    "Passive conditional perfect": "One would have",
    "Passive conditional perfect negative": "One wouldn't have",
    "Second person imperative": "(You)",
    "Second person imperative negative": "Don't",
    "Second person imperative perfect": "You must have",
    "Second person imperative perfect negative": "You musn't have",
    "Third person imperative": "She must",
    "Third person imperative negative": "He musn't",
    "Third person imperative perfect": "He must have",
    "Third person imperative perfect negative": "She musn't have",
    "First person imperative plural": "Let's",
    "First person imperative plural negative": "Let's not",
    "First person imperative plural perfect": "Let's have",
    "First person imperative plural perfect negative": "Let's not have",
    "Second person imperative plural": "(You all)",
    "Second person imperative plural negative": "(You all) don't",
    "Second person imperative plural perfect": "(You all) have ___ done",
    "Second person imperative plural perfect negative":
        "(You all) don't have ___ done",
    "Third person imperative plural": "They must",
    "Third person imperative plural negative": "They musn't",
    "Third person imperative plural perfect": "They must have",
    "Third person imperative plural perfect negative": "They musn't have",
    "Passive imperative": "One must",
    "Passive imperative negative": "One musn't",
    "Passive imperative perfect": "One must have",
    "Passive imperative perfect negative": "One musn't have",
    "First person potential": "I could",
    "First person potential negative": "I couldn't",
    "First person potential perfect": "I could have",
    "First person potential perfect negative": "I couldn't have",
    "Second person potential": "You could",
    "Second person potential negative": "You couldnt'",
    "Second person potential perfect": "You could have",
    "Second person potential perfect negative": "You couldn't have",
    "Third person potential": "She could",
    "Third person potential negative": "He couldn't",
    "Third person potential perfect": "He could have",
    "Third person potential perfect negative": "He couldn't have",
    "First person potential plural": "We could",
    "First person potential plural negative": "We couldn't",
    "First person potential plural perfect": "We could have",
    "First person potential plural perfect negative": "We couldn't have",
    "Second person potential plural": "You all could",
    "Second person potential plural negative": "You all couldn't",
    "Second person potential plural perfect": "You all could have",
    "Second person potential plural perfect negative":
        "You all couldn't have",
    "Third person potential plural": "They could",
    "Third person potential plural negative": "They couldn't",
    "Third person potential plural perfect": "They could have",
    "Third person potential plural perfect negative": "They couldn't have",
    "Passive potential": "One could",
    "Passive potential negative": "One couldn't",
    "Passive potential perfect": "One could have",
    "Passive potential perfect negative": "One wouldn't have",
    "1st infinitive": "[skip]",
    "Present active participle": "-ing",
    "Present passive participle": "Which is to be",
    "A infinitive, long form": "[skip]",
    "Past active participle": "(did this)",
    "Past passive participle": "(which is to be done by one)",
    "E infinitive inessive": "(when someone does this)",
    "E infinitive inessive passive": "(when one does this)",
    "Agent participle": "(past adjectival form)",
    "E infinitive instructive": "(doing this)",
    "Negative participle": "(without this)",
    "MA infinitive inessive": "(ongoing action or process)",
    "MA infinitive elative": "(from doing this)",
    "MA infinitive illative": "(about to begin)",
    "MA infinitive adessive": "(by doing this)",
    "MA infinitive abessive": "(without doing this)",
    "MA infinitive instructive": "(solemn necessity)",
    "MA infinitive instructive passive": "(one's solemn necessity)",
    "MINEN infinitive nominative": "[skip]",
    "MINEN infinitive partitive": "[skip]",
    "5th infinitive": "[skip]"
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
    copy('nouns.csv', newpath)
    print("Backup completed")

def load_invariants():
    """Loads the invariants file"""
    invariants = pd.ead_csv('invariants.csv',
                            index_col='Finnish',
                            parse_dates=['Last reviewed', 'Next review'],
                            infer_datetime_format=True)
    invariants.sort_index(inplace=True)
    return invariants

def load_nominals():
    """Load the nouns file"""
    nouns = pd.read_csv('nominals.csv',
                        index_col="Nominative singular",
                        parse_dates=["Last reviewed", "Next review"],
                        infer_datetime_format=True)
    nouns.sort_index(inplace=True)
    return nouns

def load_verbs():
    """Loads the verbs file"""
    verbs= pd.read_csv('verbs.csv',
                        index_col="Infinitive",
                        parse_dates=["Last reviewed", "Next review"],
                        infer_datetime_format=True)
    verbs.sort_index(inplace=True)
    return verbs

def save_invariant(invariant=None, english=None):
    """Save an invariant and at it to the file"""
    if invariant is None:
        invariant = input("Invariant (Finnish): ")
    if english is None:
        english = input("English translation of {}: ".format(invariant))
    last_reviewed = pd.Timestamp(pd.NaT)
    next_review = pd.Timestamp(pd.to_datetime(datetime.datetime.now()))
    correct = nan
    times_correct = 0
    times_incorrect = 0
    stats = [last_reviewed, next_review, correct, times_correct,
             times_incorrect]
    data = [invariant, english] + stats
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
    last_reviewed = pd.Timestamp(pd.NaT)
    next_review = pd.Timestamp(pd.to_datetime(datetime.datetime.now()))
    correct = nan
    times_correct = 0
    times_incorrect = 0
    stats = [last_reviewed, next_review, correct, times_correct,
             times_incorrect]
    data = [nominal, english] + forms + stats
    columns = NOMINAL_COLUMNS + list(NOMINAL_FORMS.keys()) + STATS
    entry = pd.DataFrame(data=[data], columns=columns)
    entry.set_index(keys="Nominative singular", inplace=True)
    nouns = load_nominals()
    nouns = nouns.append(entry, verify_integrity=True)
    conf = input("Adding {}. Continue? ".format(nominal)).lower()
    if conf == 'y':
        nouns.to_csv('nouns.csv')
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
    last_reviewed = pd.Timestamp(pd.NaT)
    next_review = pd.Timestamp(pd.to_datetime(datetime.datetime.now()))
    correct = nan
    times_correct = 0
    times_incorrect = 0
    stats = [last_reviewed, next_review, correct, times_correct,
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
    
def retrieve_nominal(nominal, skip_save=False):
    """Get a noun's forms from wiktionary"""
    session = HTMLSession()
    link_string = "https://en.wiktionary.org/wiki/{}".format(nominal)
    r = session.get(link_string)
    soup = BeautifulSoup(r.text, 'html.parser')
    forms = []
    for key, value in NOMINAL_FORMS.items():
        span = soup.find(class_=value)
        link = span.find('a')
        form = link['title'].split(" ")[0]
        forms.append(form)
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
    r = session.get(link_string)
    soup = BeautifulSoup(r.text, 'html.parser')
    spans=soup.find_all(lang='fi')
    adding = False
    forms = []
    for span in spans:
        # First valid entry will be first person singular 
        # which will always end in an 'n'
        if span.text[-1] == 'n':
            adding = True
        if adding:
            forms.append(span.text)
    # There are extraneous entries at the end
    forms = forms[:157]
    verbs = load_verbs()
    if not skip_save and verb not in verbs.index:
        conf = input("No entry for {} in file. Add? ".format(verb)).lower()
        if conf == 'y':
            save_verb(verb, forms=forms)
    return forms
