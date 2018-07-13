# Mining Amazon Product Reviews

Final project for csc558, Data Mining and Predictive Analytics II. I chose a broad and unrelated set of products based on their dissimilarity to eachother, and how many reviews they contained. This data is then sent in two different directions, 'smart' and 'dumb'.
'Smart' has the text tokenized, and part-of-speach and word count information statistics are analyzed.
'Dumb' is tokenized text, and single words or n-grams of words are analyzed by frequency.
These results are then used to experiment with generating a positive or negative review.
One technique is using Keras and Tensorflow to build an LSTM trained on the input text.
The other technique is generating a Markov chain based on review text.

## Getting Started

You'll want Python 3.x 
(more things coming)

### Prerequisites

NLTK library 

```
nltk.download('stopwords')
nltk.download('punkt')
```

### Installing

A step by step series of examples that tell you how to get a development env running

Step 1

```
example
```

Step n-1

```
finished
```

End with an example of getting some data out of the system or using it for a little demo


## Author

* **John Feilmeier** - *Initial work* - [Jacktavitt](https://github.com/jacktavitt)


## License

If its helpful, let me know!

## Acknowledgments

* Billie Thompson *README template* - [PurpleBooth](https://github.com/PurpleBooth)
* More
* etc

