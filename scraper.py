"""
scraper.py
Author: Bonhwang Koo
Date: 4/25/2019

A quick script written to scrape keywords from links listed on a 
government website on obesity (https://medlineplus.gov/obesity.html)

"""

import certifi
import csv
import matplotlib.pyplot as plt
import os
import pandas as pd
import re
import sys
import urllib3
from bs4 import BeautifulSoup as bs

# Function: wordListToFreqDict
# params:
#	wordlist: a list of strings
# returns a dictionary of string frequencies in a list
def wordListToFreqDict(wordlist):
    wordfreq = [wordlist.count(p) for p in wordlist]
    return dict(zip(wordlist,wordfreq))

# Configure HTTPS requests
# For further explanation, read https://urllib3.readthedocs.io/en/latest/user-guide.html
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

# Dictionary of attributes to scrape from websites
attributes = {"name":["keywords", "Description"], "property":"og.description"}

# Scrape HTML from MedlinePlus Website
responseMedline = http.request('GET', 'https://medlineplus.gov/obesity.html')
soupMedline = bs(responseMedline.data, 'lxml')
# Scrape all sections with external links (class = 'section')
sectionDivs = soupMedline.findAll('div', {'class', 'section'}) 

urls = []
for div in sectionDivs:
	for a in div.findAll('a', href = True):
		if a.text != 'Spanish': # Ignore links in Spanish
			urls.append(a['href'])

if not os.path.isdir('outputs'):
	os.mkdir('outputs') # Create a new directory for outputs	
with open("outputs/urls.csv",'w') as file:
    wr = csv.writer(file, dialect='excel')
    for url in urls:
    	wr.writerows([[url]])

# Loop through all links
allKeywords = []
for url in urls:
	response = http.request('GET', url)
	soup = bs(response.data, 'lxml')
	# Scrape meta attributes
	for attribute in attributes:
		for value in attributes[attribute]:
			try:
				keywordString = soup.find('meta', {attribute:value})['content']
				keywords = re.findall(r"[\w']+", keywordString) # Remove punctuation from keywords
				keywords = [keyword.lower() for keyword in keywords] # Convert all keywords to lowercase
				allKeywords.extend(keywords)
			except:
				continue

# Create dict with frequency of keywords
frequencies = wordListToFreqDict(allKeywords)
# Remove frequent words
frequentWords = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my']
for key in frequentWords:
	frequencies.pop(key, None)
	
# Convert dict to pandas dataframe
frequenciesDF = pd.DataFrame(frequencies.items())
frequenciesDF = frequenciesDF.sort_values(by = 1, ascending = False)
frequenciesDF.to_csv("outputs/keywordFrequencies.csv", header = False, index = False) # Save data as .csv fkle

# Subset 25 most frequent keywords for plotting
plotDF = frequenciesDF.iloc[0:25]

# Plot 25 most frequent keywords
plt.figure()
plt.bar(plotDF[0], plotDF[1])
plt.xticks(plotDF[0], rotation='vertical')
plt.xlabel('Keyword')
plt.ylabel('Frequency')
plt.subplots_adjust(bottom=0.25) # Add room to bottom of plot so axis labels don't get cut off
plt.savefig('outputs/frequencies.png')