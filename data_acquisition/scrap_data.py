# Imporing required libraries
from msilib.schema import Property
import requests
import re
import selenium
from bs4 import BeautifulSoup, BeautifulStoneSoup
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import org.openqa.selenium.chrome.ChromeDriver




# driver = webdriver.Chrome("C:\Users\Admin\Desktop\REAL_ESTATE_PREDICTION\SergeMartin_HousePrice_Prediction\data_acquisition\chromedriver.exe")
# driver.get ("https://www.immoweb.be/nl/zoeken/huis/te-koop?countries=BE")

# # #assigning url
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
url = "https://www.immoweb.be/nl/zoeken/huis/te-koop?countries=BE&priceType=SALE_PRICE&page=1&orderBy=relevance&gclid=Cj0KCQjw-fmZBhDtARIsAH6H8qjTKK4fMtFTGdZ8MLuXMXsZkgY9qfCZGz8AqwAO-e8qYmoK8WgHEqQaAhFgEALw_wcB"

#defining the get_property function to get  the property from the url
def get_property(url):
     req = requests.get(url, headers=headers)
     content=req.content
     soup=BeautifulSoup(content, "html.parser")
     scripts = soup.findAll('script', type='text/javascript')
     len(scripts)
     #print(len(scripts))
     property_dic = {} 
     for script in scripts:
        text = script.text
        if 'window.classified' in text:
            text = text[text.find('{'): text.rfind(';')]
            property_dic = json.loads(text)
            #print(property_dic)
            break
    # new_dic = {'id': property_dic ["id", "cluster"] }
    # print(new_dic)
     return property_dic["property"] # this dic contain info of all properties,
   
# #Testing the above function on one web page
property_dic=get_property("https://www.immoweb.be/nl/zoekertje/huis/te-koop/berloz/4257/10151895?searchId=633d5556493a0")
#print(property_dic)
print(property_dic.keys())
#print(property_dic.values())
print(property_dic["type"])
print(property_dic["location"])
#print(property_dic)

from parsel import Selector 
#Obtain 10000 url of houses with webdriver

# driver = webdriver.Chrome("../chromedriver.exe")
# driver.get ("https://www.immoweb.be/nl/zoeken/huis/te-koop?countries=BE")

# The url  "houses_url" list.
houses_url = [] 

# Iterate through all result pages (page) and get the url of each
for page in range(1, 334):
    apikey = str(page)+'&orderBy=relevance'
    url = 'https://www.immoweb.be/en/search/house/for-sale?countries=BE&page='+apikey
    driver.implicitly_wait(10)
    driver.get(url)
 
    sel = Selector(text = driver.page_source) 
    # Store the xpath query of houses
    xpath_houses = '//*[@id="main-content"]/li//h2//a/@href'
    
    # Find nodes matching the xpath ``query`` and return the result
    page_houses_url = sel.xpath(xpath_houses).extract()
    
    # Add each page url list to houses_url, like in a matrix.
    houses_url.append(page_houses_url)

# Store all houses urls in a csv file
with open('C:/Users/Admin/Desktop/REAL_ESTATE_PREDICTION/SergeMartin_HousePrice_Prediction/data_acquisition/csv_files/houses_apartments_urls.csv', 'w') as file:
    for page_url in houses_url:
        for url in page_url:
            file.write(url+'\n')

# The url of each appartment that resulted from the search will be stored in the "houses_url" list
apartments_url = []
for page in range(1, 334):
    apikey = str(page)+'&orderBy=relevance'
    url = 'https://www.immoweb.be/en/search/apartment/for-sale?countries=BE&page='+apikey
    driver.implicitly_wait(10) 
    driver.get(url)
    sel = Selector(text=driver.page_source) 
    xpath_apartments = '//*[@id="main-content"]/li//h2//a/@href'
    page_apartments_url = sel.xpath(xpath_apartments).extract()
    apartments_url.append(page_apartments_url)
# As with houses, store all appartments urls in the same csv file
with open('C:/Users/Admin/Desktop/REAL_ESTATE_PREDICTION/SergeMartin_HousePrice_Prediction/data_acquisition/csv_files/houses_apartments_urls.csv', 'a') as file:
    for page_url in apartments_url:
        for url in page_url:
            file.write(url+'\n')


class HouseApartmentScraping:
    '''
    Define a class through which properties' data will be scraped

    Each url represents a property (house or appartment), 
    each of which has a number of attributes (e.g., locality, type_property etc.). 
    We thus create a class defining the attributes of each property

    :param url: urls of properties in houses_apartments_urls.csv
    :param html: html code of urls
    :param soup: BeautifulSoup text of htmls
    :param house_dict: attribute referring to the set of houses data 
        (stored in a dictionary; see below in house dict method)
    '''
    def __init__(self, url):
        self.url = url
        # attributes to obtain html code (self.html) and select parts of it (self.soup)
        self.html = requests.get(self.url).content
        self.soup = BeautifulSoup(self.html,'html.parser')
        
        # attribute referring to the set of houses data (stored in a dictionary; see below)
        self.house_dict = self.house_dict()
        
        # set of attributes collected in the dictionary
        self.type_property = self.type_property()
        self.locality = self.locality()
        self.subtype = self.subtype()
        self.price = self.price()
        self.type_sale = self.type_sale()
        self.num_rooms = self.num_rooms()
        self.area = self.area()
        self.kitchen = self.kitchen()
        self.furnished = self.furnished()
        self.fire = self.fire()
        self.terrace_area = self.terrace_area()
        self.garden_area = self.garden_area()
        self.land = self.land()
        self.num_facade = self.num_facade()
        self.pool = self.pool()
        self.state = self.state()
        
        
    def house_dict(self):
        '''
        Define a method that creates the dictionary with attributes as keys and houses' values as values
        '''
        try:
            # The relevant info is under a "script" tag in the website
            result_set = self.soup.find_all('script',attrs={"type" :"text/javascript"})
            
            # Iterate through the "script" tags found and keep the one containing the substring "window.classified"
            # which contains all the relevant info
            for tag in result_set:
                if 'window.classified' in str(tag.string):
                    window_classified = tag
                    #when we've found the right tag we can stop the loop earlier
            
            
            # Access to the string attribute of the tag and remove leading and trailing whitespaces (strip)break
            wcs = window_classified.string
            wcs.strip()
            
            # Keep only the part of the string that will be converted into a dictionary
            wcs = wcs[wcs.find("{"):wcs.rfind("}")+1]
            
            # Convert it into a dictionary through json library
            house_dict = json.loads(wcs)
            return house_dict
        except:
            return None

    # Define a method to scrap each property attribute
    def type_property(self):
        try:
            return self.house_dict['property']['type']
        except:
            return None        
    
    def locality(self):
        try:
            return self.house_dict['property']['location']['postalCode']
        except:
            return None
    
    def subtype(self):
        try:
            return self.house_dict['property']['subtype']
        except:
            return None
    
    def price(self):
        try:
            return int(self.house_dict['transaction']['sale']['price'])
        except:
            return None
    
    def type_sale(self):
        try:
            if self.house_dict['flags']['isPublicSale'] == True:
                return 'Public Sale'
            elif self.house_dict['flags']['isNotarySale'] == True:
                return 'Notary Sale'
            elif self.house_dict['flags']['isAnInteractiveSale'] == True:
                return 'Intractive Sale'
            else:
                return None
        except:
            return None 
    
    def num_rooms(self):
        try:
            return int(self.house_dict['property']['bedroomCount'])
        except:
            return None
    
    def area(self):
        try:
            return int(self.house_dict['property']['netHabitableSurface'])
        except:
            return None
    
    def kitchen(self):
        try: 
            kitchen_type = self.house_dict['property']['kitchen']['type']
            if kitchen_type:
                return 1
            else:
                return 0        
        except:
            return None
        
    def furnished(self):
        try:
            furnished = self.house_dict['transaction']['sale']['isFurnished']
            if furnished == True:
                return 1
            else:
                return 0
            
        except:
            return None
    
    def fire(self):
        try:
            fire = self.house_dict['property']['fireplaceExists']
            if fire == True:
                return 1 
            else:
                return 0                
        except:
            return None
    
    def terrace_area(self):
        try:
            if self.house_dict['property']['hasTerrace'] == True:
                return int(self.house_dict['property']['terraceSurface'])
            else:
                return 0
        except:
            return None
    
    def garden_area(self):
        try:
            if self.house_dict['property']['hasGarden'] ==  True:
                return self.house_dict['property']['gardenSurface']
            else:
                return 0
        except:
            return None
    
    def land(self):
        try:
            if self.house_dict['property']['land'] != None:
                return self.house_dict['property']['land']['surface']
            else:
                return 0
        except:
            return None
        
    def num_facade(self):
        try:
            return int(self.house_dict['property']['building']['facadeCount'])
        except:
            return None
        
    def pool(self):
        try: 
            swim_regex = re.findall('swimming pool', str(self.html))
            if swim_regex:
                return 1
            else:
                return 0
        except:
            return None
        
    def state(self): 
        try:
            return self.house_dict['property']['building']['condition']
        except:
            return None

# impot HouseApartmentScraping class
from collecting_data_from_url_properties import HouseApartmentScraping 

# to build a defaultdict
from collections import defaultdict

# to build the dataframe
import pandas as pd 

# 3) store all data of properties into a defaultdict
houses_apartments_dict = defaultdict(list)

with open('../csv_files/houses_apartments_urls.csv', 'r') as file:
    url = file.readline()
    while url != "":
        
        houses_class = HouseApartmentScraping(url)
        
        houses_apartments_dict['Locality'].append(houses_class.locality)
        houses_apartments_dict['Type of property'].append(houses_class.type_property)
        houses_apartments_dict['Subtype of property'].append(houses_class.subtype)
        houses_apartments_dict['Price'].append(houses_class.price)
        houses_apartments_dict['Type of sale'].append(houses_class.type_sale)
        houses_apartments_dict['Number of rooms'].append(houses_class.num_rooms)
        houses_apartments_dict['Living surface area'].append(houses_class.area)
        houses_apartments_dict['Kitchen'].append(houses_class.kitchen)
        houses_apartments_dict['Furnished'].append(houses_class.furnished)
        houses_apartments_dict['Open fire'].append(houses_class.fire)
        houses_apartments_dict['Terrace'].append(houses_class.terrace_area)
        houses_apartments_dict['Garden'].append(houses_class.garden_area)
        houses_apartments_dict['Surface of the land'].append(houses_class.land)
        houses_apartments_dict['Number of facades'].append(houses_class.num_facade)
        houses_apartments_dict['Swimming pool'].append(houses_class.pool)
        houses_apartments_dict['State of the building'].append(houses_class.state)

        url = file.readline()

# 3) We store all data to a csv file with dataframe.
df = pd.DataFrame(houses_apartments_dict)
df.to_csv('C:/Users/Admin/Desktop/REAL_ESTATE_PREDICTION/SergeMartin_HousePrice_Prediction/data_acquisition/csv_files/all_data_of_the_houses.csv')






# # searching over al the link
# data_all = {}
# url_list = []
# property_list = []
# for page in range (1, 334):
#     url = f"https://www.immoweb.be/en/search/house/for-sale?countries=BE&page={page}&orderBy=relevance."
#     req=requests.get(url, headers=headers)
#     soup=BeautifulSoup(req.content, "html.parser")
#     propertyid = soup.find("div",class_="classified__header--immoweb-code")
#     property_list = soup.find_all('li', class_='search-results__item')
#     for property in range(len(property_list)):
#         current_property = property_list[property].find('a',href=True)
#         try:
#             data_all[propertyid] = get_property(current_property['href'])
#             url_list[property] = current_property['href']
#         except:
#             print("None")       

# print (data_all)



# #     characteristics = get_property(url)    
# #     property_list.append(characteristics)# make a list of all ppty
# # print(property_list)
















# results = eval(property.text)
# print(results)

# # dic = {}
# # dic = json.loads(property.text)
# # print(type(dic))




# # function to get the property into a dictionary
# #dic{
#     #for page in pages
# # }

# # string = string[string.find('{'):string.rfind('}')+1]
# # string = dict(json.loads(string))
# # print(string['classified'])


# # dic = {}

#     # return dic