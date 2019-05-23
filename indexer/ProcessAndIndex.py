import os, re
from collections import defaultdict
from Utilities import remove_stopwords_and_tokenize
from Utilities import get_clean_text
from Utilities import base_path
from database.Models import *

# Get directories and files
walker = os.walk(base_path)
# Skip current directory
next(walker)

# Paths for html files
html_file_names = list()

# Walk through all subdirectories
for walk in walker:
    dir = walk[0].split(os.path.sep)[-1]
    html_file_names += [ dir + os.path.sep + html_file_name for html_file_name in walk[2] if html_file_name.split('.')[-1] == 'html' ]

# Every file clean and retrieve text
html_texts = { html_file_name : get_clean_text(base_path + os.path.sep + html_file_name) for html_file_name in html_file_names }

# Set of all unique tokens
unique_words = set()

# Create sqlite3 Session
sessionII = SessionII()
sessionD  = SessionD()

# Before processing empty the current database
sessionII.query(IndexWord).delete()
sessionII.query(Posting).delete()
sessionII.commit()
sessionII.flush()
sessionD.query(Document).delete()
sessionD.commit()
sessionD.flush()

# Add all processed texts to another database
sessionD.add_all([ Document(documentName=html_name, content=html_content) for (html_name, html_content) in html_texts.items() ])
sessionD.commit()
sessionD.flush()

# For each file
for (html_file_name, html_text) in html_texts.items():
    # Get tokens with positions
    tokens_with_starts_and_ends = remove_stopwords_and_tokenize(html_text)
    
    # Create inverse token index
    token_index = defaultdict(lambda: [0,[]])
    for (token, start, end) in tokens_with_starts_and_ends:
        # Increase count and append token position
        token_index[token][0] += 1
        token_index[token][1].append(start)
    
    # Create a list of Posting
    database_postings = list()
    for (token,(count, positions)) in token_index.items():
        # Add token to set of unique words
        unique_words.add(token)
        database_postings.append(Posting(word=token, documentName=html_file_name, frequency=count, indexes=','.join(str(position) for position in positions)))
        
    # Add Posting list to database
    sessionII.add_all(database_postings)
    sessionII.commit()
    sessionII.flush()

# Add IndexWord list to database
sessionII.add_all([IndexWord(word=word) for word in unique_words])
sessionII.commit()
sessionII.flush()