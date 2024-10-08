import re
import string
# from ftfy import fix_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def ngrams(string, n=3):
    # string = fix_text(string) # fix text
    string = string.encode("ascii", errors="ignore").decode()  # remove non-ascii chars
    string = string.lower()
    chars_to_remove = [")", "(", ".", "|", "[", "]", "{", "}", "'"]
    rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
    string = re.sub(rx, '', string)
    string = string.replace('&', 'and')
    string = string.replace(',', ' ')
    string = string.replace('-', ' ')
    string = string.title()  # normalize case - capital at start of each word
    string = re.sub(' +', ' ', string).strip()  # get rid of multiple spaces and replace with a single
    string = ' ' + string + ' '  # pad names for ngrams...
    string = re.sub(r'[,-./]|\sBD', r'', string)
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]


def knearestNeighbors(skills, query):
    matches = []
    vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams, lowercase=False)
    tfidf = vectorizer.fit_transform(skills)
    queryTFIDF_ = vectorizer.transform(query)

    nbrs = NearestNeighbors(n_neighbors=1, n_jobs=-1).fit(tfidf)
    distances, indices = nbrs.kneighbors(queryTFIDF_)
    for i, j in enumerate(indices):
        dist = round(distances[i][0], 2)
        temp = [dist]
        matches.append(temp)
    return matches


def cleaningText(text):
    text = text.replace('\\n', '\n')
    text = text.replace('\\t', '\n')
    text = text.replace('\\r', '\n')
    text = text.replace('\n', ' ')  # replace new line into space
    text = text.translate(str.maketrans('', '', string.punctuation))  # remove all punctuations
    text = text.replace("'b", ' ')
    text = re.sub(' nan ', ' ', text)
    text = re.sub(r'\\x[0-9a-z]{2}', r' ', text)
    text = re.sub(r'[0-9]{2,}', r' ', text)
    text = re.sub(r'http\S+\s*', ' ', text)  # remove URLs
    text = re.sub(r'RT|cc', ' ', text)  # remove RT and cc
    text = re.sub(r'#\S+', ' ', text)  # remove hashtags
    text = re.sub(r'@\S+', ' ', text)  # remove mentions
    text = re.sub(r'\s+', ' ', text)  # remove extra whitespace
    text = text.lower()
    text = re.sub(r'xx+', r' ', text)
    text = re.sub(r'XX+', r' ', text)
    text = re.sub(r'[^\x00-\x7f]', "", text)
    return text.strip()  # remove space from both left and right text


def casefoldingText(text):  # Converting all the characters in a text into lower case
    text = text.lower()
    return text


# Pipeline
def preprocessing(text):
    text = cleaningText(text)
    text = casefoldingText(text)
    return text


def vectorizing(skills, job):
    count_matrix = []
    for jobs in job:
        text = [skills, jobs]
        cv = CountVectorizer()
        count_matrix.append(cv.fit_transform(text))
    return count_matrix


def coSim(vector):
    matchPercentage = []
    for vec in vector:
        matchPercentage.append(cosine_similarity(vec)[0][1] * 100)
    matchPercentage = [round(percent, 2) for percent in matchPercentage]
    return matchPercentage
