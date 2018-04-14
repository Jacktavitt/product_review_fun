# help from https://dev.to/davidisrawi/build-a-quick-summarizer-with-python-and-nltk
'''
the goal is to suss out the details of these reviews, so I can compare the sets of words
between products and between reviews,
i.e., all 3 star reviews have these words regardless of product,
or all reviews of this product have these words regardless of rating
'''


import csv
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
nltk.download('stopwords')
nltk.download('punkt')
# our set of stop words
_stopWords_ = set(stopwords.words("english"))

def buildProcessedPacket(initWC, postWC, goodWds, badWds, numGood, numBad):
    return {
        'initial_WC':initWC,
        'processed_WC': postWC,
        # 'freq_list':fL,
        'meaningful_words':goodWds,
        'stop_words':badWds,
        'meaning_percent':numGood,
        'stop_percent':numBad
    }

def processString(aString):
    # what do I want from this?
    # first tokenize words
    reviewWds = word_tokenize(aString)
    # initial word count:
    initial_word_count = len(reviewWds)
    # frequency list:
    freq_list={}
    for word in reviewWds:
        word=word.lower()
        if word not in freq_list and word not in _stopWords_:
            freq_list[word] = reviewWds.count(word)
    # now that we dont' need repeats, make a set from words:
    reviewWds_set = set(reviewWds)
    # set of words from review that are not stop words
    meaning_words = reviewWds_set - _stopWords_
    # set of words that are stopwords
    useless_words = _stopWords_ & reviewWds_set
    # percent of useful or useless words compared to whole review set
    meaning_percent = len(meaning_words) / len(reviewWds_set)
    useless_percent = len(useless_words) / len(reviewWds_set)
    # put it into a dict and return it
    packet = buildProcessedPacket(initial_word_count, len(reviewWds_set), \
            meaning_words,useless_words,meaning_percent,useless_percent )
    return packet, freq_list

def goThroughDataCSV():
    freqList=[]
    with open('review_data.csv','r') as csvFile:
        csvReader=csv.DictReader(csvFile, delimiter=',')
        # fieldnames for writing to new csv file
        # fieldNames = ['initial_WC', 'meaning_percent' , 'meaningful_words', 'stop_words', 'processed_WC', 'stop_percent'] 
        firstTextWrite = True
        firstTitleWrite = True
        # collect all of the frequency lists, so i can go thru and write them all afterwords
        
        counter = 0
        for row in csvReader:
            product_name = row['product_name']
            review_title= row['review_header']
            review_score= row['review_rating']
            review_text = row['review_text']
            # adding this so i can write it to each different csv
            shared_values = {'product_name':product_name,'review_score':review_score }
            # send to helper function
            processed_title,title_freq = processString(review_title)
            processed_title.update(shared_values)
            # title_freq = processed_title['freq_list']
            title_freq.update({'_type_':'title'})
            processed_review, review_freq = processString(review_text)
            processed_review.update(shared_values)
            # review_freq = processed_review['freq_list']
            review_freq.update({'_type_':'review'})
            with open('processed_review_text_data.csv', 'a+') as outFile:
                writer = csv.DictWriter(outFile, fieldnames = list(processed_review.keys()))
                if firstTextWrite:
                    writer.writeheader()
                    firstTextWrite = False
                writer.writerow(processed_review)
            freqList.append(review_freq)
            with open('processed_review_title_data.csv', 'a+') as outFile:
                writer = csv.DictWriter(outFile, fieldnames = list(processed_title.keys()))
                if firstTitleWrite:
                    writer.writeheader()
                    firstTitleWrite = False
                writer.writerow(processed_title)
            freqList.append(title_freq)
            # if counter %25 == 0:
            #     print(freqList)
            # counter += 1
    # print(type(freqList))
        # now must set up the freq table for all reviews
        # first, get headers for all words in all reviews (huge!)
    allWords = []
    for d in freqList:
        for k in d.keys():
            allWords.append(k)
    # now we shou;d have a list of all the words
    # lets narrow it down into a set, and make a sorted list for headers
    allWords.sort()
    allWords = set(allWords)
    allWords = list(allWords)
    firstFreqWrite = True
    for freqDict in freqList:
        with open('processed_frequency_list.csv', 'a+') as freqFile:
            writer = csv.DictWriter(freqFile, fieldnames = allWords)
            if firstFreqWrite:
                writer.writeheader()
                firstFreqWrite = False
            writer.writerow(freqDict)
    # print(type(freqList))
    # return freqList

def main():
    # goThroughDataCSV()
    fl= goThroughDataCSV()
    # print(type(fl))
    # return(fl)

main()
        