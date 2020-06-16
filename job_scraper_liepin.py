#!/usr/bin/env python

import time
import urllib
import requests
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import os


def find_jobs_from(job_title, location, pubtime, desired_characs):    
    """
    This function extracts all the desired characteristics of all new job postings
    of the title, location and pubtime specified and returns them in single file.
    The arguments it takes are:
        - Job_title, which can be key words as well
        - Location, type the country name if search for the whole country
        - pubtime, published date
        - Desired_characs, this is a list of the job characteristics of interest,
            from titles, companies, links and date_listed.
    """   

    driver = webdriver.Chrome(executable_path=('/usr/local/bin/chromedriver'))  
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

    # limit job within 3 days
    # place cursor to the dropdown for visibility
    dropdown_time = driver.find_element_by_xpath("//*[@class='dropdown dropdown-time']") 
    webdriver.ActionChains(driver).move_to_element(dropdown_time).perform() 

    # click the pub time
    pub_time_button = driver.find_element_by_xpath("//*[text()= \'{}\']".format(pubtime))
    pub_time_button.click()

    driver.implicitly_wait(5)
    
    page = 1
    all_jobs = pd.DataFrame() 

    while page < 11: # pick an arbitrary number of pages so this doesn't run infinitely
        print(f'\nNEXT PAGE #: {page}\n')        

        page_source = driver.page_source
        job_soup = BeautifulSoup(page_source, 'html.parser')
        jobs_list, num_listings = extract_job_information_liepin(job_soup, desired_characs) 
        jobs_list = pd.DataFrame(jobs_list)
        all_jobs= pd.concat([all_jobs,jobs_list])

        #scroll down to the bottom of the page
        page_bar = driver.find_element_by_xpath("//*[@class='commonweblink-main wrap']") 
        webdriver.ActionChains(driver).move_to_element(page_bar).perform()
        #click next page
        next_page_button = driver.find_element_by_xpath("//*[text() = '下一页']")
        next_page_button.click()
        
        page += 1 # increment page count
        
        driver.implicitly_wait(5)       
    
    #store jobs in an excel file
    filetime = time.strftime('%Y%m%d')
    filename ='{}_{}.xls'.format(location, filetime)
    all_jobs.to_excel(filename)
    driver.close() #close the browser window
 
    print('{} new job postings in {}. Stored in {}.'.format(num_listings, location, filename))


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
    # if there is no lie pin prefex, add that
    if link[0] == '/':
        link = f"https://www.liepin.com{link}"
    return link

def extract_date_liepin(job_elem):
    date = job_elem.find('time')['title']
    return date


#example 

desired_characs = ['titles', 'companies', 'links', 'date_listed']
find_jobs_from( '统计', '深圳', '三天以内', desired_characs)
