# from tut here: https://www.scrapehero.com/how-to-scrape-amazon-product-reviews/

from lxml import html  
import json
import re
import requests
import json,re
from dateutil import parser as dateparser
from time import sleep
import sys

# def ParseReviews(asin):
def ParseReviews(wholeUrl):
	# for i in range(5):
	# 	try:
	#This script has only been tested with Amazon.com
	# amazon_url  = 'http://www.amazon.com/dp/'+asin
	# changing this to hopefully grab more reviews
	amazon_url = wholeUrl
	# Add some recent user agent to prevent amazon from blocking the request 
	# Find some chrome user agent strings  here https://udger.com/resources/ua-list/browser-detail?browser=Chrome
	# headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
	page = requests.get(amazon_url,headers = headers,verify=False)
	page_response = page.text

	parser = html.fromstring(page_response)
	XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
	XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
	XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'

	XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
	# XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
	XPATH_PRODUCT_NAME = '//head//title//text()'
	XPATH_PRODUCT_PRICE  = '//span[@class="a-color-price arp-price"]/text()'
	# XPATH_PRODUCT_PRICE  = '//span[@id="priceblock_ourprice"]/text()'
	
	raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
	product_price = ''.join(raw_product_price).replace(',','')

	raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
	product_name = ''.join(raw_product_name).replace('Amazon.com: Customer reviews:','').strip()
	total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
	# reviews = parser.xpath(XPATH_REVIEW_SECTION_1)
	# if not reviews:
	reviews = parser.xpath(XPATH_REVIEW_SECTION_2)
	ratings_dict = {}
	reviews_list = []
	
	if reviews:
		# raise ValueError('unable to find reviews in page')

		#grabing the rating  section in product page
		for ratings in total_ratings:
			extracted_rating = ratings.xpath('./td//a//text()')
			if extracted_rating:
				rating_key = extracted_rating[0] 
				raw_raing_value = extracted_rating[1]
				rating_value = raw_raing_value
				if rating_key:
					ratings_dict.update({rating_key:rating_value})
		
		#Parsing individual reviews
		for review in reviews:
			XPATH_RATING  = './/i[@data-hook="review-star-rating"]//text()'
			XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
			XPATH_REVIEW_POSTED_DATE = './/span[@data-hook="review-date"]//text()'
			# XPATH_REVIEW_TEXT_1 = './/div[@data-hook="review-collapsed"]//text()'
			XPATH_REVIEW_TEXT_2 = './/div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing-showfullreview'
			XPATH_REVIEW_BODY = './/span[@data-hook="review-body"]//text()'
			XPATH_REVIEW_COMMENTS = './/span[@data-hook="review-comment"]//text()'
			XPATH_AUTHOR  = './/span[contains(@class,"profile-name")]//text()'
			XPATH_REVIEW_TEXT_3  = './/div[contains(@id,"dpReviews")]/div/text()'
			
			raw_review_author = review.xpath(XPATH_AUTHOR)
			raw_review_rating = review.xpath(XPATH_RATING)
			raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
			raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
			raw_review_text1 = review.xpath(XPATH_REVIEW_BODY)
			raw_review_text2 = review.xpath(XPATH_REVIEW_TEXT_2)
			raw_review_text3 = review.xpath(XPATH_REVIEW_TEXT_3)

			#cleaning data
			author = ' '.join(' '.join(raw_review_author).split())
			review_rating = ''.join(raw_review_rating).replace('out of 5 stars','')
			review_header = ' '.join(' '.join(raw_review_header).split())

			try:
				review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
			except:
				review_posted_date = None
			review_text = ' '.join(' '.join(raw_review_text1).split())

			#grabbing hidden comments if present
			if raw_review_text2:
				json_loaded_review_data = json.loads(raw_review_text2[0])
				json_loaded_review_data_text = json_loaded_review_data['rest']
				cleaned_json_loaded_review_data_text = re.sub('<.*?>','',json_loaded_review_data_text)
				full_review_text = review_text+cleaned_json_loaded_review_data_text
			else:
				full_review_text = review_text
			if not raw_review_text1:
				full_review_text = ' '.join(' '.join(raw_review_text3).split())

			raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)
			review_comments = ''.join(raw_review_comments)
			review_comments = re.sub('[A-Za-z]','',review_comments).strip()
			review_dict = {
								'review_comment_count':review_comments,
								'review_text':full_review_text,
								'review_posted_date':review_posted_date,
								'review_header':review_header,
								'review_rating':review_rating,
								'review_author':author

							}
			reviews_list.append(review_dict)

		data = {
					'ratings':ratings_dict,
					'reviews':reviews_list,
					'url':amazon_url,
					'price':product_price,
					'name':product_name
				}
		return data
	else:
		return {'reviews': None}
	# 	except ValueError:
	# 		print("Retrying to get the correct response")

	# return {"error":"failed to process the page","asin":asin}

def getBCodes():
	'''
	opens file with amazon urls, and sends the b-codes to the scraper function.
	'''
	with open('dataRetreival/product_sites.dat', 'r') as f:
		data = f.read()

	# split into lines, and regex them. assuming all have no '/' at the end
	lines=data.split('\n')
	# bcode=re.compile(r'(B[a-zA-Z0-9_]+)$')
	codeList=[]
	for url in lines:
		codeList.append(url[-10:])
		# try:
		# 	# codeList.append(bcode.match(url).group(0))
		# 	codeList.append(re.search(r'(B[a-zA-Z0-9_]+)', url).group(0))
		# except:
		# 	print('{} not matched!'.format(url))

	return codeList

def gen500Pages(filename, numPages):
	with open(filename, 'r') as f:
		data = f.read()

	# split into lines, and regex them. assuming all have no '/' at the end
	lines=data.split('\n')
	# bcode=re.compile(r'(B[a-zA-Z0-9_]+)$')
	urlList=[]
	for url in lines:
		newUrl = url[:-1]
		for num in range(1,numPages+1):
			urlList.append(newUrl+str(num))

	return urlList

		

def ReadAsin(listfile, outputname, numPages):
	#Add your own ASINs here 
	# AsinList = ['B01ETPUQ6E','B017HW9DEW','B01CT3K500','B009P4845K','1582972400','B009NVTE5E','B00006IAKF','B000USRG90','B00UXG4WR8','B07BWQ622V','B003YFI0O6','B073P2FRXS','B0035440R2','B00OACD9CU','B00990Z4W6','B01F24RGZK','B00NGV4506']
	# AsinList = getBCodes()
	UrlList = gen500Pages(listfile, numPages)
	extracted_data = []
	# for asin in AsinList:
	# 	print("Downloading and processing page http://www.amazon.com/dp/"+asin)
	# 	extracted_data.append(ParseReviews(asin))
	# 	sleep(1)
	for url in UrlList:
		print("Downloading and processing page "+url)
		try:
			extracted_data.append(ParseReviews(url))
		except Exception as e:
			print(e)
		with open(outputname,'w') as f:
			json.dump(extracted_data,f,indent=4)
		sleep(3)
	# with open(outputname,'w') as f:
	# 	json.dump(extracted_data,f,indent=4)

if __name__ == '__main__':
	if len(sys.argv) != 4:
		print("usage:<listfile> <outputfile> <num pages to scrape through>")
		exit()
	ReadAsin(sys.argv[1],sys.argv[2], int(sys.argv[3]))