# Scraping Notes

## Basic Structure:
The base site is an xml map with sub xml site maps

## Steps:
1. use pythons requests library to send get request to site map
2. from each sub xml map build a list of links
3. determine if link is recipe or not
4. if it is a recipe pull data for analysis (at this point we are only interested in inredients)
5. create csv file

## Dependancies:
* Requests
* bs4
* pandas
* lxml