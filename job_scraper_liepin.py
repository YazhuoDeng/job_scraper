


import time
import urllib
import requests
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import os


def find_jobs_from(website, job_title, location, desired_characs):    
    """
    This function extracts all the desired characteristics of all new job postings
    of the title and location specified and returns them in single file.
    The arguments it takes are:
        - Website: to specify which website to search
        - Job_title, which can be key words as well
        - Location, type the country name if search for the whole country
        - Desired_characs: this is a list of the job characteristics of interest,
            from titles, companies, links and date_listed.
    """
    
    #can be used for other websites
    if website == 'Liepin':
        driver = webdriver.Chrome(executable_path=('/usr/local/bin/chromedriver'))        
        job_soup = make_job_search_liepin(job_title, location, driver)
        jobs_list, num_listings = extract_job_information_liepin(job_soup, desired_characs)
    
    jobs = pd.DataFrame(jobs_list)
    filetime = time.strftime('%Y%m%d')
    filename ='{}_{}_{}.xls'.format(website, location, filetime)
    jobs.to_excel(filename)
 
    print('{} new job postings retrieved from {}. Stored in {}.'.format(num_listings, website, filename))


def make_job_search_liepin(job_title, location, driver):
    driver.get('https://www.liepin.com/')
    
    # Select the job box
    job_title_box = driver.find_element_by_xpath("//*[@name='key']")
    job_title_box.clear()
    
    # Send job information
    job_title_box.send_keys(job_title)
    
    # Find Search button
    search_button = driver.find_element_by_xpath("//*[@class='search-btn float-right']")
    search_button.click()
    
    # Find city button
    location_button = driver.find_element_by_xpath("//*[text()= \'{}\']".format(location))
    location_button.click()
    
    driver.implicitly_wait(5)

    page_source = driver.page_source
    
    job_soup = BeautifulSoup(page_source, "html.parser")
    
    return job_soup


def extract_job_information_liepin(job_soup, desired_characs):
    
    job_elems = job_soup.find_all('div', class_ = 'job-info')
    company_elems = job_soup.find_all('div', class_ = 'company-info nohover')
     
    cols = []
    extracted_info = []
    
    if 'titles' in desired_characs:
        titles = []
        cols.append('titles')
        for job_elem in job_elems:
            titles.append(extract_title_liepin(job_elem))
        extracted_info.append(titles) 
                               
    if 'companies' in desired_characs:
        companies = []
        cols.append('companies')
        for company_elem in company_elems:
            companies.append(extract_company_liepin(company_elem))
        extracted_info.append(companies)
    
    if 'areas' in desired_characs:
        areas = []
        cols.append('areas')
        for job_elem in job_elems:
            areas.append(extract_area_liepin(job_elem))
        extracted_info.append(areas)
    
    if 'links' in desired_characs:
        links = []
        cols.append('links')
        for job_elem in job_elems:
            links.append(extract_link_liepin(job_elem))
        extracted_info.append(links)
                
    if 'date_listed' in desired_characs:
        dates = []
        cols.append('date_listed')
        for job_elem in job_elems:
            dates.append(extract_date_liepin(job_elem))
        extracted_info.append(dates)    
    
    jobs_list = {}
    
    for j in range(len(cols)):
        jobs_list[cols[j]] = extracted_info[j]
    
    num_listings = len(extracted_info[0])
    
    return jobs_list, num_listings


def extract_title_liepin(job_elem):
    title_elem = job_elem.find('h3')
    title = title_elem.text.strip()
    return title

def extract_company_liepin(company_elem):
    company_elem = company_elem.find('a')
    company = company_elem.text.strip()
    return company

def extract_area_liepin(job_elem):
    area_elem = job_elem.find('a', class_='area')
    area = area_elem.text.strip()
    return area

def extract_link_liepin(job_elem):
    link = job_elem.find('a')['href']
    return link

def extract_date_liepin(job_elem):
    date = job_elem.find('time')['title']
    return date

#example 

desired_characs = ['titles', 'companies', 'links', 'date_listed']
find_jobs_from('Liepin', '统计', '深圳', desired_characs)




