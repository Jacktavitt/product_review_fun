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
import os
import random
import csv
import statistics as st
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LinearRegression, LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
# nltk.download('stopwords')
# nltk.download('punkt')
# our set of stop words
_stopWords_ = set(stopwords.words("english")) | {".",","," ","~","/","\\","^","@","'","'s","(",")","-"}
_classList_=[MultinomialNB, BernoulliNB,LinearRegression, LogisticRegression, SGDClassifier,SVC, LinearSVC, NuSVC]

def cleanAndStem(someString):
    # ps = PorterStemmer()
    lzr = WordNetLemmatizer()
    # tokenize it!
    toked = word_tokenize(someString)
    # lowercase it!
    toked = [x.lower() for x in toked]
    # make stems!
    # stemmed = [ps.stem(x) for x in toked]
    # doing lemmas instead 
    lemmad = [lzr.lemmatize(x) for x in toked]
    # remove doubles! (?)
    # trimmed = list(set(stemmed))
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


def goThroughCSVDumb(numMostCommon):
    '''
    open csv, go through to build a dataset, simply sorted by above 2 stars or not with words
    classify with nltk Naive Bayes
    '''
    reviews=[]
    allWords=[]
    with open('parseResultFiles/review_data_big_raw.csv','r') as csvFile:
        csvReader=csv.DictReader(csvFile, delimiter=',')
        for row in csvReader: # row is an orderedDict type
            lem, tok = cleanAndStem(row['review_text'])
            # rate = 'good' if float(row['review_rating']) > 2.5 else 'bad'
            # reviews.append((tok, float(row['review_rating'])))
            # allWords.extend(tok)
            # use lemma'd words instead of token
            reviews.append((lem, float(row['review_rating']), row['product_name'][:20]))
            allWords.extend(lem)

    random.shuffle(reviews)
    # print(reviews[3])
    allWordsFD=nltk.FreqDist(allWords)
    print(allWordsFD.most_common(25))
    wordFeats = list(allWordsFD.keys())[:numMostCommon]
    featureSet=[(dumbGetFeatures( review, wordFeats ), rating, ident) for (review, rating, ident) in reviews]

    wf=list(wordFeats)
    wf.extend(['__rating__','__product_name__'])
    # sortedWFT = sorted(wordFeats.extend(['__rating__','__product_name__']))
    # header = sortedWFT.extend(['__rating__','__product_name__'])
    with open('parseResultFiles/dumb_review_data.csv', 'w', newline='') as outputFile:
        writer = csv.DictWriter(outputFile, fieldnames = wf)
        writer.writeheader()
        for n in featureSet:
            # print("yo\n'")
            n[0]['__rating__'] = n[1]
            n[0]['__product_name__'] = n[2]
            writer.writerow(n[0])


    # train_set = featureSet[:math.floor(len(featureSet)/2)]
    # test_set = featureSet[math.floor(len(featureSet)/2):]
    # classifier = nltk.NaiveBayesClassifier.train(train_set)
    # print("Classifier accuracy percent:",(nltk.classify.accuracy(classifier, test_set))*100)
    # classifier.show_most_informative_features(30)
    # for cfr in _classList_:
    #     New_classifier = SklearnClassifier(cfr())
    #     New_classifier.train(train_set)
    #     print('{} accuracy percent: {}'.format(str(cfr), (nltk.classify.accuracy(New_classifier, test_set))*100 ))
        
    # TODO: somehow remove words that are product specific, but keep a count somwhwere
    # TODO: maybe also remove stop words to see what effect it has
    # TODO: find a better classifier than nltk naive bayes
    #       if the dataset is just a bunch of booleans, Should be able to use scikit learn tools

def percentPOS(tagged):
    '''
    return the percentages for NOUN, VERB, ADJ, ADV, WH-things
    '''
    totalLen = len(tagged)
    if totalLen == 0:
        return {
            'propNouns' : 0,
            'nouns' : 0,
            'adjectives' : 0,
            'pronouns' : 0,
            'verbs' : 0,
            'adverbs' : 0,
            'whs' : 0
        }
    partsList = list(dict(tagged).values())
    percents = {
        'propNouns' : len([x for x in partsList if 'NNP' in x])/totalLen,
        'nouns' : (len([x for x in partsList if 'NN' in x]) - len([x for x in partsList if 'NNP' in x]))/totalLen,
        'adjectives' : len([x for x in partsList if 'JJ' in x])/totalLen,
        'pronouns' : len([x for x in partsList if 'PR' in x])/totalLen,
        'verbs' : len([x for x in partsList if 'VB' in x])/totalLen,
        'adverbs' : len([x for x in partsList if 'RB' in x])/totalLen,
        'whs' : len([x for x in partsList if 'W' in x])/totalLen
    }
    return percents

def cleanProductName(productName):
    punks = {".",",","[","]","~","/","\\","^","@","'","'s","(",")","-","`"}
    for p in punks:
        productName.replace(p,'')
    productName = productName[:20]
    return productName

def goThroughCSVSmart():
    '''
    go through csv file, line by line, and generate new csv files we can use
    '''
    outputFile = open('dataParsing/parseResultFiles/smart_review_data.csv', 'w', newline='')
    writer = csv.DictWriter(outputFile, fieldnames = [
        'id','product_name','type', 'rating', 'num_words',
        'stop_%', 'meaning_%', 
        'proper_noun_%', 'noun_%', 'pronoun_%', 'verb_%', 'adverb_%', 'adjective_%', 'wh-word_%' 
    ] )
    writer.writeheader()
    # id, type (review or title), product_name, percent_stop, percent_meaning, %Proper noun, %noun, %pronoun, %verb, %adverb, %adj, %wh 
    with open('dataParsing/parseResultFiles/review_data_big_raw.csv','r') as csvFile:
        csvReader=csv.DictReader(csvFile, delimiter=',')
        for row in csvReader: # row is an orderedDict type
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
            revTag = nltk.pos_tag(reviewTok)
            titTag = nltk.pos_tag(titleTok)
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
                'wh-word_%':revPOSpcnt['whs']
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
                'wh-word_%':titPOSpcnt['whs']
            }
            writer.writerow(toWriteRev)
            writer.writerow(toWriteTit)
    outputFile.close()


def main():
    # generate initial csv file
    # parse_json.fromJSONtoCSV()
    # go through initial csv file and create two files: one for processed title / review ,
    # and one for a frequency list of some of the more popular words
    goThroughCSVSmart()
    
if __name__=='__main__':
    goThroughCSVDumb(200)