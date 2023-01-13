from selenium import webdriver
from bs4 import BeautifulSoup
import random
import pandas as pd
import time


options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome"
chrome_driver_binary = "/usr/local/bin/chromedriver"


def get_soup(url):
    """
    This function get the beautifulsoup object of a webpage.

    Args:
        url (str): the link string of webpage

    Returns:
        soup (obj): beautifulsoup object
    """
    driver = webdriver.Chrome(chrome_driver_binary, options=options)
    driver.get(url)
    time.sleep(random.uniform(1, 3))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup

def scraping_job(soup):
    res = []
    jobs = soup.find_all(attrs={'class':'job_seen_beacon'})
        
    for idx,job in enumerate(jobs):
        job_gap_min = 5 #min sleep time between jobs
        job_gap_max = 10 #max sleep time between jobs
        gap = random.uniform(job_gap_min,job_gap_max) 
        time.sleep(gap)
        print(f'scrapping {idx} job...')
        try:
            linkpart = job.select_one('h2 a')['href']
        except:
            continue
        
        head = "https://www.indeed.com/"
        link = linkpart.replace('/rc/clk?','')
        job_url = head+'viewjob?'+link
        #print(job_url)
        
        job_title = job.find('h2').getText()
        attr_snip = []
        try:
            company_name = job.find(attrs={'class':'companyName'}).getText()
        except:
            company_name = 'none'
        company_location = job.find(attrs={'class':'companyLocation'}).getText()

        try:
            salary = job.find(attrs={'class':'metadata estimated-salary-container'}).getText()
        except:
            salary = 'not given'
        try:
            for attr in job.find_all(attrs={'class':'attribute_snippet'}):
                attr_snip.append(attr.getText())
        except:
            attr_snip = ['not given']         
        
        res.append(
            {
                'title': job_title,
                'company': company_name,
                'location': company_location,
                'salary': salary,
                'attrs': attr_snip,
                'link': job_url            
            }
        
        )
        resdict = pd.DataFrame.from_dict(res)
    return resdict
        
    
    

def get_jobs_df(job_title):
    """
    Args:
        job_title (str): example: 'data+scientist'
    Returns:
        a dataframe, and saved to .csv
    """
    #needed to be changed
    num_pages = 5 #number of pages to scrape
    page_gap_min = 3 #min sleep time between pages
    page_gap_max = 5 #max sleep time between pages
    job_per_page = 25 #number of jobs in one page


    data = pd.DataFrame()
    for i in range(num_pages): 
        #sleep between each call
        gap = random.uniform(page_gap_min,page_gap_max) 
        time.sleep(gap)
        
        head = "https://www.indeed.com/"
        tail = "jobs?q={0}&sort=date&limit={1}".format(job_title,job_per_page)
        if i>0:
            tail += "&start={0}".format(i*job_per_page)

        #get link to joblist page
        url = head+tail 
        soup = get_soup(url)
        data = pd.concat([data, scraping_job(soup)])
        print(f'Finished {i+1} page, {num_pages-i-1} pages left')
    data.to_csv('sample_data.csv')
    print('Done....')
    return data


if __name__ == "__main__":
    get_jobs_df("data+scientist")
