'''
this is the driver to process the JSON file.
the file 'review_data_raw.csv' is the jumping-off point.
List of things we want to know for each review:
 > Review ID
 > Product
 > NLP for title and review text:
    > Initial word count
    > % stop words
    > % meaningful words
    > % adjective
    > % noun
    > % pronoun
    > % adverb
    > % verb
    > % 'wh' things
 > Rating
 > 
'''
import parse_json


def cleanAndStem(someString):
    ps = PorterStemmer()
    # tokenize it!
    toked = word_tokenize(someString)
    # lowercase it!
    toked = [x.lower() for x in toked]
    # make stems!
    stemmed = [ps.stem(x) for x in toked]
    # remove doubles! (?)
    # trimmed = list(set(stemmed))
    return stemmed

if __name__=='__main__':
    # generate initial csv file
    parse_json.fromJSONtoCSV()

