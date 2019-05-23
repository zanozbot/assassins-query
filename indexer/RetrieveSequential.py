import os, sys, argparse, collections, time
from Utilities import tokens_with_positions
from Utilities import get_clean_text
from Utilities import base_path
from Utilities import remove_stopwords_and_tokenize

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

# Tokenize input string
tokens_with_starts_and_ends = tokens_with_positions(params)

# Start query time
query_time = time.time()

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
text_per_file = { html_file_name : get_clean_text(base_path + os.path.sep + html_file_name) for html_file_name in html_file_names }

token_db = dict()
for (html_file_name, html_text) in text_per_file.items():
    # Get tokens with positions
    tokens_ret = remove_stopwords_and_tokenize(html_text)
    for token in tokens_ret:
        if token[0] not in token_db:
            token_db[token[0]] = []
        token_db[token[0]].append( [ html_file_name, token[1], token[2] ] )

# Dictionaries
neighbors_per_token = dict()
counts_per_file = dict()

# For each token
for (token, start, stop) in tokens_with_starts_and_ends:

    if token not in token_db:
        continue
    else:
        refs = token_db[token]

    # For each reference
    for ref in refs:
        txt = text_per_file[ref[0]]
        start = ref[1]
        end =  ref[2]
        i = 4
        while start > 0 and i > 0:
            start -= 1
            if txt[start] == ' ':
                i -= 1
        if txt[start] == ' ' or start < 0:
            start += 1
        i = 3
        while end < len(txt)-1 and i > 0:
            end += 1
            if txt[end] == ' ':
                i -= 1

        # If no list available in dictionary for this document create new
        if ref[0] not in neighbors_per_token:
            neighbors_per_token[ref[0]] = list()
        neighbors_per_token[ref[0]].append( [start,end] )

        # If no counts in dictionary create
        if ref[0] not in counts_per_file:
            counts_per_file[ref[0]] = 0
        counts_per_file[ref[0]] += 1
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
print('Results found in ' + ( "{0:.2f}".format(query_time) ) + 's. Retrieved ' + str(len(snippet_per_file)) + ' documents.')
print( formatter.format('Frequencies', 'Document', 'Snippet') )
print( ('-'*freq_len) + '  ' + ('-'*doc_len) + '  ' + ('-'*snip_len) )
for i in range( min(args.num_rows,len(snippet_per_file)) ):
    print( formatter.format(*snippet_per_file[i]) )