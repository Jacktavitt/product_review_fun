import json
import csv

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

    # first, remove those items without reviews
    for product in data:
        if not product['reviews']:
            data.remove(product)

    # now, we will write the reviews to a csv file
    with open('review_data.csv','w') as file:
        csvWriter=csv.writer(file)
        isHeader = True
        for product in data:
            product_name=product['name']
            for review in product['reviews']:
                if isHeader:
                    header = ['product_name'] + list(review.keys())
                    # header = ['product_name'] + header
                    csvWriter.writerow(header)
                    isHeader = False
                review_data = [product_name] + list(review.values())
                csvWriter.writerow(review_data)
    
fromJSONtoCSV()
