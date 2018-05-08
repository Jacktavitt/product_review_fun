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
# import parse_json
import math
import sys
import os
import random
import csv
import statistics as st
import enchant
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer
from nltk.util import ngrams
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LinearRegression, LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from collections import Counter
# nltk.download('stopwords')
# nltk.download('punkt')
# our set of stop words
_stopWords_ = set(stopwords.words("english")) | {".",","," ","~","/","\\","^","@","'","'s","(",")","-"}
_classList_=[MultinomialNB, BernoulliNB,LinearRegression, LogisticRegression, SGDClassifier,SVC, LinearSVC, NuSVC]

def cleanAndStem(someString):
    # ps = PorterStemmer()
    lzr = WordNetLemmatizer()
    # tokenize it!
    # trying regex tokenizer to remove annoying shit
    tokener = RegexpTokenizer("[a-zA-Z'`]+")
    toked = tokener.tokenize(someString)
    # this will remove poorly-used apostophes and backtics from the mix
    for n in range(len(toked)):
        toked[n]=toked[n].lower().replace("'",'').replace("`",'')
    lemmad = [lzr.lemmatize(x) for x in toked]
    return lemmad, toked

def getStopAndMeaningWordPercent(stringList):
    '''
    takes a list of strings (from cleanandstem)
    '''
    if len(stringList) < 1:
        return 0,0
    total = len(stringList)
    stop = 0
    meaning = 0
    for word in stringList:
        if word in _stopWords_:
            stop += 1
        else: meaning += 1
    stopPerc = stop/total
    meanPerc = meaning/total
    return stopPerc, meanPerc

# def getPartsOfSpeech(stringList):
    
# featureSet=[(dumbGetFeatures( review, wordFeats ), rating, ident) for (review, rating, ident) in reviews]
def dumbGetFeatures(stringList,wordFeats):
    words = set(stringList)
    feats={}
    for word in wordFeats:
        # feats[word] = word in words
        feats[word]= stringList.count(word)
    return feats

def writeDumbARFF(featureSet, wordFeats):
    with open('dataParsing/parseResultFiles/fd.arff', 'w') as f:
        f.write("@RELATION frequency_distribution\n")
        wordFeats.sort()
        for word in wordFeats:
            f.write("@ATTRIBUTE {} (True, False)\n".format(word))
        f.write("@ATTRIBUTE rating NUMERIC\n")
        f.write("@DATA\n")
        for feat in featureSet:
            vals=[feat[0][x] for x in feat[0]]
            f.write("{},{}\n".format(vals, feat[1]))

def goThroughCSVBigram(numMostCommon, setIt, initialCSVfile, outFile, ngramNum=2):
    '''
    open csv, go through to build a dataset, simply sorted by above 2 stars or not with words
    classify with nltk Naive Bayes
    '''
    reviews=[]
    allBigrams=[]
    # folder= 'parseResultFiles/'
    # outFile = '_bigram_review_data_setstyle.csv' if setIt else '_bigram_review_data.csv'
    # outFile = folder+str(numMostCommon)+outFile
    outFile = outFile[:-4] + '_' + str(ngramNum)'-gram' +outFile[-4:]

    with open(initialCSVfile,'r') as csvFile:
        csvReader=csv.DictReader(csvFile, delimiter=',')
        for row in csvReader: # row is an orderedDict type
            # this will remove numbers and other characters
            tokener = RegexpTokenizer("[a-zA-Z'`]+")
            toked=tokener.tokenize(row['review_text'])
            # this will remove poorly-used apostophes and backtics from the mix
            for n in range(len(toked)):
                toked[n]=toked[n].lower().replace("'",'').replace("`",'')
            # now lets do some bigram action
            b_list = list(ngrams(toked,2, pad_right = True))
            # add bigram list and other info to review data
            reviews.append((b_list, float(row['review_rating']), row['product_name'][:20]))
            # add bigram list to allData
            if setIt:
                allBigrams.extend(set(b_list))
            else:
                allBigrams.extend(b_list)

    random.shuffle(reviews)
    # now make frequency list of bigrams
    biGramFD = Counter(allBigrams)
    print(biGramFD.most_common(25))
    # now create a header for the resulting csv file
    biGramFeats = list(dict(biGramFD.most_common(numMostCommon)).keys())
    # same as before, i think
    featureSet = [(dumbGetFeatures(review,biGramFeats),rating, ident) for (review, rating, ident) in reviews]
    bGf = list(biGramFeats)
    bGf.extend(['__rating__','__product_name__'])
    with open(outFile, 'w', newline='') as outputFile:
        writer = csv.DictWriter(outputFile, fieldnames = bGf)
        writer.writeheader()
        for n in featureSet:
            n[0]['__rating__'] = n[1]
            n[0]['__product_name__'] = n[2]
            writer.writerow(n[0])


def goThroughCSVDumb(numMostCommon, setIt, useTokens, initialCSVfile, outFile):
    '''
    open csv, go through to build a dataset, simply sorted by above 2 stars or not with words
    classify with nltk Naive Bayes
    '''
    reviews=[]
    allWords=[]
    outFile = outFile[:-4] + '_dumb' +outFile[-4:]
    # folder = 'parseResultFiles/'
    # usingWhich = '_tokens.csv' if useTokens else '_lemmas.csv'
    # outFile = '_dumb_review_data_setstyle' if setIt else '_dumb_review_data'
    # outFile = folder + str(numMostCommon)+outFile+ usingWhich
    with open(initialCSVfile,'r') as csvFile:
        csvReader=csv.DictReader(csvFile, delimiter=',')
        for row in csvReader: # row is an orderedDict type
            lem, tok = cleanAndStem(row['review_text'])
            # rate = 'good' if float(row['review_rating']) > 2.5 else 'bad'
            # reviews.append((tok, float(row['review_rating'])))
            # allWords.extend(tok)
            # use lemma'd words instead of token
            reviews.append((lem, float(row['review_rating']), row['product_name'][:20]))
            data = tok if useTokens else lem
            if setIt:
                allWords.extend(set(data))
            else:
                allWords.extend(data)

    random.shuffle(reviews)
    # print(reviews[3])
    allWordsFD=nltk.FreqDist(allWords)
    print(allWordsFD.most_common(25))
    wordFeats = list(dict(allWordsFD.most_common(numMostCommon)).keys())
    featureSet=[(dumbGetFeatures( review, wordFeats ), rating, ident) for (review, rating, ident) in reviews]

    wf=list(wordFeats)
    wf.extend(['__rating__','__product_name__'])
    # sortedWFT = sorted(wordFeats.extend(['__rating__','__product_name__']))
    # header = sortedWFT.extend(['__rating__','__product_name__'])
    # !!! This is hardcoded bullshit to try to even out the dataset !!! BAD SCIENCE!!!
    numberFiveStars = 0
    with open(outFile, 'w', newline='') as outputFile:
        writer = csv.DictWriter(outputFile, fieldnames = wf)
        writer.writeheader()
        for n in featureSet:
            # print("yo\n'")
            n[0]['__rating__'] = n[1]
            n[0]['__product_name__'] = n[2]
            if n[1] == 5.0:
                numberFiveStars += 1
            if (n[1] == 5.0) and (numberFiveStars > 999):
                # print(type(n[1]))
                pass
            else:
                writer.writerow(n[0])

def percentPOS(tagged):
    '''
    return the percentages for NOUN, VERB, ADJ, ADV, WH-things, and misspelled words
    '''
    SC = enchant.Dict("en_US")
    totalLen = len(tagged)
    if totalLen == 0:
        return {
            'propNouns' : 0,
            'nouns' : 0,
            'adjectives' : 0,
            'pronouns' : 0,
            'verbs' : 0,
            'adverbs' : 0,
            'whs' : 0,
            'bad_spelling':0
        }
    partsList = list(dict(tagged).values())
    percents = {
        'propNouns' : len([x for x in partsList if 'NNP' in x])/totalLen,
        'nouns' : (len([x for x in partsList if 'NN' in x]) - len([x for x in partsList if 'NNP' in x]))/totalLen,
        'adjectives' : len([x for x in partsList if 'JJ' in x])/totalLen,
        'pronouns' : len([x for x in partsList if 'PR' in x])/totalLen,
        'verbs' : len([x for x in partsList if 'VB' in x])/totalLen,
        'adverbs' : len([x for x in partsList if 'RB' in x])/totalLen,
        'whs' : len([x for x in partsList if 'W' in x])/totalLen,
        'bad_spelling': len([x for x in partsList if not SC.check(x)])/totalLen
    }
    return percents

def cleanProductName(productName):
    punks = {".",",","[","]","~","/","\\","^","@","'","'s","(",")","-","`"}
    for p in punks:
        productName.replace(p,'')
    productName = productName[:20]
    return productName

def goThroughCSVSmart(sourcedata,outFile):
    '''
    go through csv file, line by line, and generate new csv files we can use
    '''
    outputFile = open(outFile, 'w', newline='')
    writer = csv.DictWriter(outputFile, fieldnames = [
        'id','product_name','type', 'rating', 'num_words',
        'stop_%', 'meaning_%', 
        'proper_noun_%', 'noun_%', 'pronoun_%', 'verb_%', 'adverb_%', 'adjective_%', 'wh-word_%', 'missspelled_%' 
    ] )
    writer.writeheader()
    # id, type (review or title), product_name, percent_stop, percent_meaning, %Proper noun, %noun, %pronoun, %verb, %adverb, %adj, %wh 
    # !!! This is hardcoded bullshit to try to even out the dataset !!! BAD SCIENCE!!!
    numberFiveStars = 0
    with open(sourcedata,'r') as csvFile:
        csvReader=csv.DictReader(csvFile, delimiter=',')
        for row in csvReader: # row is an orderedDict type
            if len(row) > 0:
                # productName = ' '.join(word_tokenize(row['product_name'])[:3]).replace('(','').replace(')','')
                # productName = str(row['product_name'].replace('(','').replace(')','')[:20])
                productName = cleanProductName(row['product_name'])
                # review_id,product_name,review_author,review_header,review_rating,review_comment_count,review_text,review_posted_date
                reviewLem, reviewTok = cleanAndStem(row['review_text'])
                titleLem, titleTok = cleanAndStem(row['review_header'])
                # overall word count
                numRevWords = len(reviewTok)
                numTitWords = len(titleTok)
                # get percentages of meaning and stop words
                revStop,revMean = getStopAndMeaningWordPercent(reviewLem)
                titStop, titMean = getStopAndMeaningWordPercent(titleLem)
                # get tagged for title and review
                # if len(reviewTok) >1:
                try:
                    revTag = nltk.pos_tag(reviewTok)
                except Exception as e:
                    print(str(reviewTok)+'\n'e)
                    continue
                # else:
                #     revTag = {'None': 'None'}
                # if len(titleTok) > 1:
                try:
                    titTag = nltk.pos_tag(titleTok)
                except Exception as e:
                    print(str(titTok)+'\n'e)
                    continue
                # else:
                #     titTag = {'None': 'None'}
                # get percent of each part of speech
                revPOSpcnt = percentPOS(revTag)
                titPOSpcnt = percentPOS(titTag)
                # other things we want in the file
                ident = row['review_id']
                rating = float(row['review_rating'].strip())
                # now to put it all in a file
                toWriteRev = {
                    'id':ident,
                    'product_name':productName,
                    'type': 'review',
                    'rating': rating,
                    'num_words': numRevWords,
                    'stop_%':revStop,
                    'meaning_%':revMean, 
                    'proper_noun_%':revPOSpcnt['propNouns'],
                    'noun_%':revPOSpcnt['nouns'],
                    'pronoun_%':revPOSpcnt['pronouns'],
                    'verb_%':revPOSpcnt['verbs'],
                    'adverb_%':revPOSpcnt['adverbs'],
                    'adjective_%':revPOSpcnt['adjectives'],
                    'wh-word_%':revPOSpcnt['whs'],
                    'missspelled_%':revPOSpcnt['bad_spelling']
                }
                toWriteTit = {
                    'id':ident,
                    'product_name':productName,
                    'type': 'title',
                    'rating': rating,
                    'num_words': numTitWords,
                    'stop_%':titStop,
                    'meaning_%':titMean, 
                    'proper_noun_%':titPOSpcnt['propNouns'],
                    'noun_%':titPOSpcnt['nouns'],
                    'pronoun_%':titPOSpcnt['pronouns'],
                    'verb_%':titPOSpcnt['verbs'],
                    'adverb_%':titPOSpcnt['adverbs'],
                    'adjective_%':titPOSpcnt['adjectives'],
                    'wh-word_%':titPOSpcnt['whs'],
                    'missspelled_%':titPOSpcnt['bad_spelling']
                }  
                writer.writerow(toWriteRev)
                writer.writerow(toWriteTit)
    outputFile.close()


def main(sourcefile, outfile):
    # generate initial csv file
    # parse_json.fromJSONtoCSV()
    # go through initial csv file and create two files: one for processed title / review ,
    # and one for a frequency list of some of the more popular words
    goThroughCSVSmart(sourcefile, outfile)
    
if __name__=='__main__':
    if len(sys.argv) > 3 and len(sys.argv) != 6:
        print("usage:<NUMCOM> <USESET> <USETOK> <INITIAL CSV FILE> <OUTPUT FILE>")
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
        exit()
    elif len(sys.argv) == 6:
        numCom = int(sys.argv[1])
        useSet = bool(sys.argv[2])
        useTok = bool(sys.argv[3])
        # sample call: python pre_process_raw_data.py 200 False True big_data.csv big_data_parsed.csv
        goThroughCSVBigram(numCom,useSet,sys.argv[4], sys.argv[5])
        # goThroughCSVSmart(sys.argv[4], sys.argv[5])
        # how many words (300 too many for weka) , use sets of words instead of lists, use token instead of lemma
        goThroughCSVDumb(numCom, useSet, useTok,sys.argv[4], sys.argv[5])
    elif len(sys.argv) == 7:
        numCom = int(sys.argv[1])
        useSet = bool(sys.argv[2])
        useTok = bool(sys.argv[3])
        ngramNum= int(sys.argv[6])
        # sample call: python pre_process_raw_data.py 200 False True big_data.csv big_data_parsed.csv
        goThroughCSVBigram(numCom,useSet,sys.argv[4], sys.argv[5],ngramNum)
    else:
        print("usage:<NUMCOM> <USESET> <USETOK> <INITIAL CSV FILE> <OUTPUT FILE>")
        exit()