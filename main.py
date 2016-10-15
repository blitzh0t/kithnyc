import json
import re
import requests
import timeit
import time
from bs4 import BeautifulSoup as bs
from getconf import *

URL = 'https://kithnyc.com/collections/adidas/mens'
BASE_URL = 'https://kithnyc.com'
headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
#KEYWORD = 'adidas Originals EQT Support 93/16'
KEYWORD = 'yeezy'
CART_URL = 'https://shop.kithnyc.com/cart/'
EXT = '.json'
session = requests.session()
shoe_size = '9'
shop_url = 'https://shop.kithnyc.com'
def matchKeyWord(jsonUrl,keyword=KEYWORD):
	response = session.get(jsonUrl)
	jsonData = json.loads(response.text)
	title = jsonData['product']['title']
	variantID = jsonData['product']['variants']
	searchObj = re.search(keyword,title,re.M|re.I)
	if searchObj:
		print("keyword found")
		varID = getVariantID(variantID,shoe_size)
		return str(varID)
	else:
		return 0

def getVariantID(variantID,shoe_size):
	for items in variantID:
		if items['title'] == shoe_size:
			return items['id']

def crawlSite():
	response = session.get(URL)
	soup = bs(response.text,'html.parser')
	shoeUrl = soup.select(".product-card-image-wrapper")
	linkCount = 0
	for link in shoeUrl:
		jsonUrl = BASE_URL + link.attrs['href'] + EXT
		linkurl = BASE_URL + link.attrs['href']
		id = matchKeyWord(jsonUrl)
		if id:
			print(linkurl)
			linkCount += 1
			break
			buy = add_to_cart(id)
			if buy.status_code == requests.codes.ok:
				checkout(buy)
				break
	if linkCount == 0:
		print("no links found")

def add_to_cart(id):
	print("add to cart")
	payload = {
			'id': id,
			'quantity': '1'
		}
	response = session.get(CART_URL + id + ':1')
	print(response.status_code)
	print('url is: ' + response.url)
	return response


def checkout(buy):
	print("checkout")
	soup = bs(buy.text,'html.parser')
	forms = soup.find('form', {'class': 'edit_checkout'})
	token = soup.find('input', {'name': 'authenticity_token'})['value']
	print('token is: '+ token)
	time.sleep(.8)
	payload = {
		'utf8': '✓',
		'_method': 'patch',
		'button': '',
		'authenticity_token': token,
		'previous_step': 'contact_information',
		'checkout[email]': email,
		'checkout[shipping_address][first_name]': first_name,
		'checkout[shipping_address][last_name]': last_name,
		'checkout[shipping_address][address1]': shipping_address_1,
		'checkout[shipping_address][address2]': '',
		'checkout[shipping_address][city]': shipping_city,
		'checkout[shipping_address][country]': shipping_country,
		'checkout[shipping_address][province]': '',
		'checkout[shipping_address][province]': '',
		'checkout[shipping_address][province]': shipping_state,
		'checkout[shipping_address][zip]': shipping_zip,
		'checkout[shipping_address][phone]': phone_number,
		'checkout[client_details][browser_height]': '728',
		'checkout[client_details][browser_width]': '1280',
		'checkout[client_details][javascript_enabled]': '0',
		'step': 'shipping_method'
	}
	print('url shop: ' + shop_url + forms['action'] )
	response = session.post(shop_url + forms['action'], data=payload, headers=headers)  # customer info
	print('after shopurl')
	print(response.status_code)
	soup = bs(response.text, 'html.parser')
	form = soup.find('form', {'class': 'edit_checkout'})

	payload = {
		'_method': 'patch',
		'authenticity_token': form.find('input', {'name': 'authenticity_token'})['value'],
		'button': '',
		'checkout[client_details][browser_height]': '728',
		'checkout[client_details][browser_width]': '1280',
		'checkout[client_details][javascript_enabled]': '0',
		'checkout[shipping_rate][id]': 'shopify-UPS%20GROUND%20(5-7%20business%20days)-10.00',
		'previous_step': 'shipping_method',
		'step': 'payment_method',
		'utf8': '✓'
	}
	response = session.post(shop_url + form['action'], data=payload, headers=headers)
	print('after shipping details')
	print(response.status_code)
	soup = bs(response.text, 'html.parser')
	print(soup.p)
	form = soup.find_all('form', {'class': 'edit_checkout'})[-1]

	payload = {
		'utf8': '✓',
		'_method': 'patch',
		'authenticity_token': form.find('input', {'name': 'authenticity_token'})['value'],
#		's': form.find('input', {'name': 'c'})['value'],
#		'd': form.find('input', {'name': 'd'})['value'],
		'checkout[buyer_accepts_marketing]': '0',
		'checkout[client_details][browser_height]': '728',
		'checkout[client_details][browser_width]': '1280',
		'checkout[client_details][javascript_enabled]': '1',
		'checkout[credit_card][month]': card_exp_month,
		'checkout[credit_card][name]': first_name + ' ' + last_name,
		'checkout[credit_card][number]': card_number,
		'checkout[credit_card][verification_value]': card_cvv,
		'checkout[credit_card][year]': card_exp_year,
		'checkout[different_billing_address]': 'false',
		'checkout[payment_gateway]': form.find('input', {'name': 'checkout[payment_gateway]'})['value'],
		'complete': '1',
		'expiry': card_exp_month + '/' + card_exp_year[-2:],
		'previous_step': 'payment_method',
		's': '',
		'step': ''
		
	}
	print('payload before submitting pay options')
	print(payload)

#	return 0
	response = session.post(form['action'], data=payload, headers=headers)  # payment
	print('after payment')
	print(response.status_code)
	print(response.url)
	soup = bs(response.text, 'html.parser')
	print('heahder: ' + str(soup.h2))
#	print(soup.find(class_=re.compile("notice")))
	with open('bs4.html', 'w') as f:
		for line in soup.prettify():
			f.write(str(line))

def main():
	crawlSite()

if __name__ == '__main__':
	print("running....")
	startTime = timeit.default_timer()
	main()
	stopTime = timeit.default_timer()
	elapsedTime = stopTime - startTime
	print(elapsedTime)