import pandas
import sys
from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer

def getReviewStrings(jsonFileName):
    with open(jsonFileName,'r') as jsonFile:
        df = pandas.read_json(jsonFile.read())
    # df['reviews'] is a bunch of dictionaries. must set them aside to get the nougat out
    reviews = []
    for n in range(len(df['reviews'])):
        if  df['reviews'][n]:
            for rev in df['reviews'][n]:
                    reviews.append(rev)
    # now we have a list of individual dicts
    # lets get a string of all of the reviews for good or bad
    good = ''
    bad = ''
    for rev in reviews:
        if float(rev['review_rating']) > 3.0:
            good = good + ' ' + rev['review_text'].lower()
        else :
            bad = bad + ' ' + rev['review_text'].lower()
    
    return good, bad

if __name__=="__main__":
    if len(sys.argv) != 3:
        print("usage:<JSON FILE> <OUTPUT FILE>")
        exit()
    tokener = RegexpTokenizer("[a-zA-Z'`]+")
    good, bad = getReviewStrings(sys.argv[1])
    good = tokener.tokenize(good)
    good = " ".join(good)
    bad = tokener.tokenize(bad)
    bad = " ".join(bad)
    goodOut = sys.argv[2][:-4]+"_good"+sys.argv[2][-4:]
    badOut = sys.argv[2][:-4]+"_bad"+sys.argv[2][-4:]
    with open(goodOut,'w') as file:
        file.write(good)
        
    with open(badOut,'w') as file:
        file.write(bad)
        
