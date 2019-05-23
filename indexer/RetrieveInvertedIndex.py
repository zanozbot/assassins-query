import os, sys, argparse, collections, time
from Utilities import tokens_with_positions
from Utilities import get_clean_text
from Utilities import base_path
from database.Models import *

# Check if atleast query given
if len(sys.argv) <= 1:
    sys.argv.append('--help')
else:
    params = sys.argv[-1]
    if not params.startswith('-'):
        sys.argv = sys.argv[:len(sys.argv)-1]
    else:
        params = ""

# Parse optional parameters
parser=argparse.ArgumentParser()
parser.add_argument('--snippet-size', '-s', type=int, default=200, help='Maximal size of a snippet. Defaults to 200. If first snippet longer than snippet-size it is still displayed.')
parser.add_argument('--num-rows', '-r', type=int, default=10, help='Number of retrieved rows. Defaults to 10.')
args=parser.parse_args()

# Create sqlite3 Session
sessionII = SessionII()
sessionD  = SessionD()

# Tokenize input string
tokens_with_starts_and_ends = tokens_with_positions(params)

# Dictionaries of raw text per file
text_per_file = dict()
neighbors_per_token = dict()
counts_per_file = dict()

# For each token
query_time = time.time()
for (token, start, stop) in tokens_with_starts_and_ends:
    # Query for each token
    postings = sessionII.query(Posting).filter(Posting.word == token.lower()).all()
    
    # For each Posting
    for posting in postings:
        # Get raw text and tokens for each file
        if posting.documentName not in text_per_file:
            doc = sessionD.query(Document).filter(Document.documentName == posting.documentName).first()
            text_per_file[posting.documentName] = doc.content

        # Get Start-stop positions
        word_positions = sorted([ (int(idx),len(posting.word)) for idx in posting.indexes.split(',') ])
        start_stop = list()
        txt = text_per_file[posting.documentName]
        for word_position in word_positions:
            start = word_position[0]
            end = word_position[0] + word_position[1]
            i = 4
            while start > 0 and i > 0:
                start -= 1
                if txt[start] == ' ':
                    i -= 1
            if txt[start] == ' ' or start < 0:
                start += 1
            i = 3
            while end < len(txt) and i > 0:
                end += 1
                if txt[end] == ' ':
                    i -= 1
            start_stop.append( [start,end] )

        # If no list available in dictionary for this document create new
        if posting.documentName not in neighbors_per_token:
            neighbors_per_token[posting.documentName] = list()
        neighbors_per_token[posting.documentName] += start_stop

        # If no counts in dictionary create
        if posting.documentName not in counts_per_file:
            counts_per_file[posting.documentName] = 0
        counts_per_file[posting.documentName] += len(start_stop)
query_time = time.time() - query_time

# For pretty print format
freq_len = 11
doc_len  = 8
snip_len = 7

# For all tokens in neighbors_per_token
snippet_per_file = list()
for (doc, token_positions) in neighbors_per_token.items():
    text = text_per_file[doc]
    token_positions.sort(key=lambda x: x[0])
    tokens = [ token_positions[0] ]
    for t in range(1,len(token_positions)):
        if tokens[-1][1] >= token_positions[t][0]:
            tokens[-1][1] = token_positions[t][1]
        else:
            tokens.append(token_positions[t])

    i = 0
    ln = 0
    while ln < args.snippet_size and i < len(tokens):
        ln += tokens[i][1] - tokens[i][0]
        i += 1

    cnts = counts_per_file[doc]
    snip = " ... ".join( [ text[ token_pos[0] : token_pos[1] ] for token_pos in tokens[:i] ] )
    snippet_per_file.append( ( cnts, doc, snip ) )

# Set max document and snippet length for printing
snippet_per_file.sort(key=lambda x: x[0], reverse=True)
for i in range( min(args.num_rows,len(snippet_per_file)) ):
    doc_len  = max(len(snippet_per_file[i][1]), doc_len)
    snip_len = max(len(snippet_per_file[i][2]), snip_len)
formatter = "{:" + str(freq_len) + "}  {:" + str(doc_len) + "}  {:" + str(snip_len)  + "}"

# Print results
print('Results for query: "' + params + '"')
print('Results found in ' + str(int(query_time*1000)) + 'ms. Retrieved ' + str(len(snippet_per_file)) + ' documents.')
print( formatter.format('Frequencies', 'Document', 'Snippet') )
print( ('-'*freq_len) + '  ' + ('-'*doc_len) + '  ' + ('-'*snip_len) )
for i in range( min(args.num_rows,len(snippet_per_file)) ):
    print( formatter.format(*snippet_per_file[i]) )