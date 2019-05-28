import lxml.html
import os, re
from lxml import html, etree
from lxml.html.clean import Cleaner
from nltk import word_tokenize

# Base path for extracted documents
base_path = '.' + os.path.sep + 'extracted'

# Get tokens and their respected positions
def tokens_with_positions(raw_text):
    tokens = word_tokenize(raw_text)
    tokens_with_offsets = []
    offset = 0
    i = 0
    while i < len(tokens) and offset < len(raw_text):
        t = tokens[i]
        tl = len(t)
        tp = raw_text.find(t, offset)
        tokens_with_offsets.append( (t.lower(), tp, tp+tl) )
        i += 1
        offset = tp+tl

    return tokens_with_offsets

# Filter out stopwords and tokenize text
def remove_stopwords_and_tokenize(raw_text):
    from StopWords import stop_words_slovene
    stop_words_slovene |= {'.', ',', '!', '-', '+', '(', ')', '[', ']', '{', '}'}
    twps = [twp for twp in tokens_with_positions(raw_text) if twp[0] not in stop_words_slovene]
    return twps

# Extracter of webpage text and cleaner for javascript and style removal
def get_clean_text(filename):
    utf8_parser = html.HTMLParser(encoding='utf-8')
    htmltxt = lxml.html.parse( filename, parser=utf8_parser )
    cleaner = Cleaner()
    cleaner.javascript = True
    cleaner.style = True
    cleaner.html = True
    cleaner.page_structure = False
    cleaner.meta = False
    cleaner.safe_attrs_only = False
    cleaner.links = False
    
    htmltxt = cleaner.clean_html(htmltxt)

    txt = etree.tostring(htmltxt, encoding='unicode')
    txtresub = re.sub(r'<.+?>', ' ', txt)
    txtresub = re.sub(r'(\s|&?(amp;|apos;|quot;|gt;|lt;|nbsp;))+', ' ', txtresub)

    return txtresub
