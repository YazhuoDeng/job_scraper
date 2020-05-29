import time
import urllib
import requests
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import os


def find_jobs_from(website, job_title, location, country, desired_characs):    
    """
    This function extracts all the desired characteristics of all new job postings
    of the title and location specified and returns them in single file.
    The arguments it takes are:
        - Website: to specify which website to search (options: 'Indeed' or 'CWjobs')
        - Job_title, which can be key words as well
        - Location, type the country name if search for the whole country
        - country
        - Desired_characs: this is a list of the job characteristics of interest,
            from titles, companies, links and date_listed.
            
    """
    
    if website == 'Indeed':
        job_soup = load_indeed_jobs_div(job_title, location, country)
        jobs_list, num_listings = extract_job_information_indeed(job_soup, desired_characs, country)
    
    #can be used for other websites
    if website == 'CWjobs':
        location_of_driver = os.getcwd()
        driver = initiate_driver(location_of_driver, browser='chrome')
        job_soup = make_job_search(job_title, location, driver)
        jobs_list, num_listings = extract_job_information_cwjobs(job_soup, desired_characs)
    
    jobs = pd.DataFrame(jobs_list)
    filetime = time.strftime('%Y%m%d')
    filename ='{}_{}_{}_{}.xls'.format(website, location, country, filetime)
    jobs.to_excel(filename)
 
    print('{} new job postings retrieved from {}. Stored in {}.'.format(num_listings, website, filename))




## ================== FUNCTIONS FOR INDEED.COM =================== ##

def load_indeed_jobs_div(job_title, location, country):
    getVars = {'q' : job_title, 'l' : location, 'fromage' : 'last', 'sort' : 'date'}
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
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    job_soup = soup.find(id="resultsCol")
    return job_soup

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

find_jobs_from('Indeed', 'statistics longitudinal', 'california', 'united_states', desired_characs)

find_jobs_from('Indeed', 'statistics', 'hawaii', 'united_states', desired_characs)

find_jobs_from('Indeed', 'statistics', 'florida', 'united_states', desired_characs)

find_jobs_from('Indeed', 'statistics', 'singapore', 'singapore', desired_characs)