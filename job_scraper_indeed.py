import time
import urllib
import requests
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import os


def find_jobs_from( job_title, location, country, desired_characs):    
    """
    This function extracts all the desired characteristics of all new job postings
    of the title and location specified and returns them in single file.
    The arguments it takes are:
        - Job_title, which can be key words as well
        - Location, type the country name if search for the whole country
        - country
        - Desired_characs: this is a list of the job characteristics of interest,
            from titles, companies, links and date_listed.
            
    """
    
    getVars = {'q' : job_title, 'l' : location, 'fromage' : 'last', 'sort' : 'date'}
    
    #define country domain for url
    if country == 'united_states':
        url = ('https://www.indeed.com/jobs?' + urllib.parse.urlencode(getVars))        
    if country == "malaysia": 
        url = ('https://malaysia.indeed.com/jobs?' + urllib.parse.urlencode(getVars))
    if country == "singapore": 
        url = ('https://sg.indeed.com/jobs?' + urllib.parse.urlencode(getVars))
    if country == "canada": 
        url = ('https://ca.indeed.com/jobs?' + urllib.parse.urlencode(getVars))
    if country == "united_kingdom": 
        url = ('https://www.indeed.co.uk/jobs?' + urllib.parse.urlencode(getVars))
    if country == "australia": 
        url = ('https://au.indeed.com/jobs?' + urllib.parse.urlencode(getVars))
    if country == "china": 
        url = ('https://cn.indeed.com/jobs?' + urllib.parse.urlencode(getVars))
    
    #load chrome
    driver = webdriver.Chrome(executable_path=('/usr/local/bin/chromedriver'))  
    driver.get(url)
    
    page = 1
    all_jobs = pd.DataFrame() 
    total_num_listings = 0

    while page < 10: # pick an arbitrary number of pages so this doesn't run infinitely
        print(f'\nNEXT PAGE #: {page}\n')    
        
        #extract job info and put them into a data frame
        page_source = driver.page_source
        job_soup = BeautifulSoup(page_source, 'html.parser')
        jobs_list, num_listings = extract_job_information_indeed(job_soup, desired_characs, country) 
        jobs_list = pd.DataFrame(jobs_list)
        all_jobs= pd.concat([all_jobs,jobs_list])
        total_num_listings += num_listings
        page += 1 # increment page count

        
        # close a random popup if it shows up
        try:
            driver.find_element_by_xpath("//*[@id='popover-x']").click()
        except NoSuchElementException:
            pass
        
        #click next page
        try:
            #scroll down to the bottom of the page
            page_bar = driver.find_element_by_xpath("//*[@class='pagination-list']") 
            webdriver.ActionChains(driver).move_to_element(page_bar).perform()
            #click next page button
            next_page_button = driver.find_element_by_xpath("//*[@aria-label = 'Next']")
            next_page_button.click()
        except NoSuchElementException:
            break
        
        driver.implicitly_wait(5)  
    
    #close chrome
    driver.close()
    #store jobs in an excel file
    filetime = time.strftime('%Y%m%d')
    filename ='{}_{}_{}.xls'.format(location, country, filetime)
    all_jobs.to_excel(filename)
 
    print('{} new job postings in {}. Stored in {}.'.format(total_num_listings, location, filename))




## ================== FUNCTIONS FOR INDEED.COM =================== ##


def extract_job_information_indeed(job_soup, desired_characs, country):
    job_elems = job_soup.find_all('div', class_='jobsearch-SerpJobCard')
     
    cols = []
    extracted_info = []
    
    
    if 'titles' in desired_characs:
        titles = []
        cols.append('titles')
        for job_elem in job_elems:
            titles.append(extract_job_title_indeed(job_elem))
        extracted_info.append(titles)                    
    
    if 'companies' in desired_characs:
        companies = []
        cols.append('companies')
        for job_elem in job_elems:
            companies.append(extract_company_indeed(job_elem))
        extracted_info.append(companies)
    
    if 'links' in desired_characs:
        links = []
        cols.append('links')
        for job_elem in job_elems:
            links.append(extract_link_indeed(job_elem, country))
        extracted_info.append(links)
    
    if 'date_listed' in desired_characs:
        dates = []
        cols.append('date_listed')
        for job_elem in job_elems:
            dates.append(extract_date_indeed(job_elem))
        extracted_info.append(dates)
    
    jobs_list = {}
    
    for j in range(len(cols)):
        jobs_list[cols[j]] = extracted_info[j]
    
    num_listings = len(extracted_info[0])
    
    return jobs_list, num_listings


def extract_job_title_indeed(job_elem):
    title_elem = job_elem.find('h2', class_='title')
    title = title_elem.text.strip()
    return title

def extract_company_indeed(job_elem):
    company_elem = job_elem.find('span', class_='company')
    company = company_elem.text.strip()
    return company

def extract_link_indeed(job_elem, country):
    link = job_elem.find('a')['href']
    if country == 'united_states':
        link = 'http://www.Indeed.com/' + link
    if country == 'malaysia':
        link = 'http://malaysia.Indeed.com/' + link
    if country == 'singapore':
        link = 'http://sg.Indeed.com/' + link
    if country == 'canada':
        link = 'http://ca.Indeed.com/' + link
    if country == 'united_kingdom':
        link = 'http://www.Indeed.co.uk/' + link
    if country == 'australia':
        link = 'http://au.Indeed.com/' + link
    if country == 'china':
        link = 'http://cn.Indeed.com/' + link
    return link

def extract_date_indeed(job_elem):
    date_elem = job_elem.find('span', class_='date')
    date = date_elem.text.strip()
    return date





#try few examples

desired_characs = ['titles', 'companies', 'links', 'date_listed']

find_jobs_from('statistics longitudinal', 'california', 'united_states', desired_characs)

find_jobs_from('statistics', 'hawaii', 'united_states', desired_characs)

find_jobs_from('statistics', 'florida', 'united_states', desired_characs)

find_jobs_from('statistics', 'singapore', 'singapore', desired_characs)
