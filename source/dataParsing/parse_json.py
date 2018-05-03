'''
this will open a JSON file returned by the data retreival script, and grab the relevant info,
and write it to a CSV file
'''


import json
import csv
import sys
import random

def fromJSONtoCSV(jsonFile, outputCSV):
    '''
    data is a list of dictionaries.
    each item in list is a product.
    data[n]['name'] - product name
    data[n]['reviews'] - list of dictionaries (reviews)
        data[n]['reviews'][n].keys() -
            dict_keys(['review_author', 'review_comment_count', 'review_header', 'review_posted_date', 'review_rating', 'review_text'])

    '''
    with open(jsonFile,'r') as json_file:
        data = json.loads(json_file.read())

    
    # for product in data:
    #     if not product['reviews']:
    #         data.remove(product)
    # lets create an id for each review
    iD = 42 # ;^)
    # now, we will write the reviews to a csv file
    with open(outputCSV,'w') as file:
        csvWriter=csv.writer(file)
        isHeader = True
        for product in data:
            # first, remove those items without reviews
            if not product['reviews']:
                data.remove(product)
            else:
                product_name=product['name'].lower()
                try :product_price = float(product['price'].replace('$',''))
                except Exception as e:
                    print(e)
                for review in product['reviews']:
                    if isHeader:
                        header = ['review_id'] + ['product_name'] + ['product_price'] + list(review.keys())
                        # header = ['product_name'] + header
                        csvWriter.writerow(header)
                        isHeader = False
                    review_data = [iD] + [product_name] + [product_price] + list(review.values())
                    try:
                        csvWriter.writerow(review_data)
                    except Exception as e:
                        print(e, product_name)
                    iD += 1
    # return fl
    
if __name__=="__main__":
    if len(sys.argv) != 3:
        print("usage:<jsonFile> <outputCSVfile>")
        exit()
    fromJSONtoCSV(sys.argv[1],sys.argv[2])
