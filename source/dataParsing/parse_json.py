'''
this will open a JSON file returned by the data retreival script, and grab the relevant info,
and write it to a CSV file
'''


import json
import csv
import random

def fromJSONtoCSV():
    '''
    data is a list of dictionaries.
    each item in list is a product.
    data[n]['name'] - product name
    data[n]['reviews'] - list of dictionaries (reviews)
        data[n]['reviews'][n].keys() -
            dict_keys(['review_author', 'review_comment_count', 'review_header', 'review_posted_date', 'review_rating', 'review_text'])

    '''
    with open('data.json','r') as json_file:
        data = json.loads(json_file.read())

    
    # for product in data:
    #     if not product['reviews']:
    #         data.remove(product)
    # lets create an id for each review
    id = 42 # ;^)
    # now, we will write the reviews to a csv file
    with open('parseResultFiles/review_data_raw.csv','w') as file:
        csvWriter=csv.writer(file)
        isHeader = True
        for product in data:
            # first, remove those items without reviews
            if not product['reviews']:
                data.remove(product)
            product_name=product['name'].lower()
            for review in product['reviews']:
                if isHeader:
                    header = ['review_id'] + ['product_name'] + list(review.keys())
                    # header = ['product_name'] + header
                    csvWriter.writerow(header)
                    isHeader = False
                review_data = [id] + [product_name] + list(review.values())
                csvWriter.writerow(review_data)
                id += 1
    # return fl
    
