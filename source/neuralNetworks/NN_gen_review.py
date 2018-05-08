# frmo tut here https://machinelearningmastery.com/text-generation-lstm-recurrent-neural-networks-python-keras/

import sys
import math
import pandas
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils

punctuation = {"\"","'","`","-","=","+","&","%","$","#","@","(",")","\\","/","~"}

def getReviewStrings(jsonFileName):
    with open(jsonFileName,'r') as jsonFile:
        df = pandas.read_json(jsonFile.read())
    # df['reviews'] is a nuch of dictionaries. must set them aside to get the nougat out
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

def prepData(data, SEQ_LENGTH):
    chars = list(set(data))
    VOCAB_SIZE = len(chars)
    # dictionaries so we can convert letters to numbers and back again
    index_to_char = {idx:char for idx, char in enumerate(chars)}
    char_to_index = {char:idx for idx, char in enumerate(chars)}

    # create input for network
    X = np.zeros((len(data)/SEQ_LENGTH, SEQ_LENGTH, VOCAB_SIZE))
    y = np.zeros((len(data)/SEQ_LENGTH, SEQ_LENGTH, VOCAB_SIZE))
    for i in range(0, len(data)/SEQ_LENGTH):
        X_sequence = data[i*SEQ_LENGTH:(i+1)*SEQ_LENGTH]
        X_sequence_ix = [char_to_ix[value] for value in X_sequence]
        input_sequence = np.zeros((SEQ_LENGTH, VOCAB_SIZE))
        for j in range(SEQ_LENGTH):
            input_sequence[j][X_sequence_ix[j]] = 1.
            X[i] = input_sequence

        y_sequence = data[i*SEQ_LENGTH+1:(i+1)*SEQ_LENGTH+1]
        y_sequence_ix = [char_to_ix[value] for value in y_sequence]
        target_sequence = np.zeros((SEQ_LENGTH, VOCAB_SIZE))
        for j in range(SEQ_LENGTH):
            target_sequence[j][y_sequence_ix[j]] = 1.
            y[i] = target_sequence
    return X, y, VOCAB_SIZE, ix_to_char

def main(jsonFileName, brownleeOutput):
    goodReview, badReview = getReviewStrings(jsonFileName)
    brownleeTut(goodReview)

def brownleeTrainModel(raw_text):
    raw_text = raw_text.lower()
    # create mapping of unique chars to integers, and a reverse mapping
    chars = sorted(list(set(raw_text)))
    char_to_int = dict((c, i) for i, c in enumerate(chars))
    int_to_char = dict((i, c) for i, c in enumerate(chars))
    # summarize the loaded data
    n_chars = len(raw_text)
    n_vocab = len(chars)
    # print "Total Characters: ", n_chars
    print(("Total Characters: ", n_chars))
    print(("Total Vocab: ", n_vocab))
    # print "Total Vocab: ", n_vocab
    # prepare the dataset of input to output pairs encoded as integers
    seq_length = 100
    dataX = []
    dataY = []
    for i in range(0, n_chars - seq_length, 1):
        seq_in = raw_text[i:i + seq_length]
        seq_out = raw_text[i + seq_length]
        dataX.append([char_to_int[char] for char in seq_in])
        dataY.append(char_to_int[seq_out])
    n_patterns = len(dataX)
    print(("Total Patterns: ", n_patterns))
    # print "Total Patterns: ", n_patterns
    # reshape X to be [samples, time steps, features]
    X = np.reshape(dataX, (n_patterns, seq_length, 1))
    # normalize
    X = X / float(n_vocab)
    # one hot encode the output variable
    y = np_utils.to_categorical(dataY)
    # define the LSTM model
    # model = Sequential()
    # model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2])))
    # model.add(Dropout(0.2))
    # model.add(Dense(y.shape[1], activation='softmax'))
    # model.compile(loss='categorical_crossentropy', optimizer='adam')
    model = Sequential()
    model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(256))
    model.add(Dropout(0.2))
    model.add(Dense(y.shape[1], activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    # define the checkpoint
    # filepath="weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
    filepath="weights-improvement-{epoch:02d}-{loss:.4f}-bigger.hdf5"
    # checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
    # callbacks_list = [checkpoint]
    # # fit the model
    # model.fit(X, y, epochs=20, batch_size=128, callbacks=callbacks_list)
    checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
    callbacks_list = [checkpoint]
    # fit the model
    model.fit(X, y, epochs=50, batch_size=64, callbacks=callbacks_list)

def brownleeGenText(inputText, outFile):
    # with open(inputText,'r') as f:
    #     raw_text=f.read()
    raw_text = inputText.lower()
    out = open(outFile,'a')
    # create mapping of unique chars to integers, and a reverse mapping
    chars = sorted(list(set(raw_text)))
    char_to_int = dict((c, i) for i, c in enumerate(chars))
    int_to_char = dict((i, c) for i, c in enumerate(chars))
    # summarize the loaded data
    n_chars = len(raw_text)
    n_vocab = len(chars)
    # print "Total Characters: ", n_chars
    out.write("Total Characters: "+str(n_chars))
    out.write("Total Vocab: " +str(n_vocab))
    # print "Total Vocab: ", n_vocab
    # prepare the dataset of input to output pairs encoded as integers
    seq_length = 100
    dataX = []
    dataY = []
    for i in range(0, n_chars - seq_length, 1):
        seq_in = raw_text[i:i + seq_length]
        seq_out = raw_text[i + seq_length]
        dataX.append([char_to_int[char] for char in seq_in])
        dataY.append(char_to_int[seq_out])
    n_patterns = len(dataX)
    out.write("Total Patterns: "+ str(n_patterns))
    # print "Total Patterns: ", n_patterns
    # reshape X to be [samples, time steps, features]
    X = np.reshape(dataX, (n_patterns, seq_length, 1))
    # normalize
    X = X / float(n_vocab)
    # one hot encode the output variable
    y = np_utils.to_categorical(dataY)
    # define the LSTM model
    model = Sequential()
    model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(256))
    model.add(Dropout(0.2))
    model.add(Dense(y.shape[1], activation='softmax'))
    # load the network weights
    filename = "neuralNetworks/weights-improvement-42-1.1754-bigger.hdf5"
    model.load_weights(filename)
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    # pick a random seed
    start = np.random.randint(0, len(dataX)-1)
    pattern = dataX[start]
    out.write("Seed:")
    out.write(("\""+ ''.join([int_to_char[value] for value in pattern]) + "\""))
    # generate characters
    for i in range(270):
        x = np.reshape(pattern, (1, len(pattern), 1))
        x = x / float(n_vocab)
        prediction = model.predict(x, verbose=0)
        index = np.argmax(prediction)
        result = int_to_char[index]
        seq_in = [int_to_char[value] for value in pattern]
        sys.stdout.write(result)
        out.write(result)
        pattern.append(index)
        pattern = pattern[1:len(pattern)]
    out.write( "\nDone." )


if __name__=="__main__":
    if len(sys.argv) != 3:
        print("usage: <input TXT file>  <output text file>  ")
        exit()
    # goodReview, badReview = getReviewStrings(sys.argv[1])
    with open(sys.argv[1])as file:
        data = file.read()
    # brownleeTrainModel(data[:200000])
    # brownleeTrainModel(goodReview[:math.floor(len(goodReview)/2)])
    brownleeGenText(data, sys.argv[2])