# help from https://dev.to/davidisrawi/build-a-quick-summarizer-with-python-and-nltk
'''
the goal is to suss out the details of these reviews, so I can compare the sets of words
between products and between reviews,
i.e., all 3 star reviews have these words regardless of product,
or all reviews of this product have these words regardless of rating
'''
import os
import parse_json
import csv
import statistics as st
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
nltk.download('stopwords')
nltk.download('punkt')
# our set of stop words
_stopWords_ = set(stopwords.words("english"))
puncts={".",","," ","~","/","\\","^","@","'","'s","(",")"}
_stopWords_ = _stopWords_ | puncts

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

def csvWriterHelper(filename, rowToWrite, header):
    try :
        firstWrite = os.stat(filename).st_size == 0
    except:
        firstWrite = True
    with open(filename, 'a+') as outFile:
        writer = csv.DictWriter(outFile, fieldnames = header)
        if firstWrite:
            writer.writeheader()
        writer.writerow(rowToWrite)

def goThroughDataCSV():
    freqList = parse_json.fromJSONtoCSV()
    freqList.update({'_type_':None})
    masterFLH = set(freqList.keys())
    with open('review_data.csv','r') as csvFile:
        csvReader=csv.DictReader(csvFile, delimiter=',')
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

            title_freq.update({'_type_':'title'})
            processed_review, review_freq = processString(review_text)
            processed_review.update(shared_values)

            review_freq.update({'_type_':'review'})
            csvWriterHelper('processed_review_text_data.csv',
                    processed_review, list(processed_review.keys()))

            # freqList.append(review_freq)
            csvWriterHelper('processed_review_title_data.csv',
                    processed_title, list(processed_title.keys()))
            # need to cut out those words we know don't occur that often
            tf = { x: title_freq[x] for x in list(set(title_freq.keys()) & masterFLH ) }
            csvWriterHelper('processed_frequency_list.csv',
                    tf, list(freqList.keys()))
            rf = { x: review_freq[x] for x in list(set(review_freq.keys()) & masterFLH ) }
            csvWriterHelper('processed_frequency_list.csv',
                    rf, list(freqList.keys()))


def main():
    # goThroughDataCSV()
    fl= goThroughDataCSV()
    # print(fl)
    return(fl)

main()
        