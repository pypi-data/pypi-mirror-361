from .chromesettings import ChromeSettings
from .inputs import Inputs
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select





class FirstWebPage():
    
    def __init__(self,chromesettings:ChromeSettings,inputs_instance:Inputs):
        
        self.chromesettings = chromesettings
        self.inputs_instance = inputs_instance
        self.jobtitle_firstwp = None
        self.joblocation_firstwp = None
        self.what = None
        self.where = None
        
        
    def webpage_interaction_firstwp(self):
        
        
        """Interacts with the first webpage."""
        
        

        self.jobtitle_firstwp = random.choice(self.inputs_instance.jobtitle_list)
        self.what = self.chromesettings.browser.find_element(
            By.XPATH,
            "/html/body/div[1]/div/form/div[1]/div[1]/span/input",
        )
        time.sleep(self.chromesettings.random_time)
        self.what.send_keys(self.jobtitle_firstwp)

        self.joblocation_firstwp = random.choice(self.inputs_instance.joblocation_list)
        self.where = self.chromesettings.browser.find_element(
            By.XPATH,
            "/html/body/div[1]/div/form/div[1]/div[2]/span/input",
        )
        time.sleep(self.chromesettings.random_time)
        self.where.send_keys(self.joblocation_firstwp)
        

        search_jobs = self.chromesettings.browser.find_element(By.CSS_SELECTOR,"button.btn.btn-primary.btn-search")
        time.sleep(self.chromesettings.random_time)
        search_jobs.click()
        
        self.chromesettings.browser.refresh()
        
   
        time.sleep(10)
        try:
            last_week = self.chromesettings.browser.find_element(By.CSS_SELECTOR, "option[value='lastweek']")
            last_week.click()
        except Exception as error:
            
            print(f"Button not found {error} \n trying second option")
            select_bar = self.chromesettings.browser.find_element(By.CSS_SELECTOR,"select[aria-label='Select date posted']")
            print("select bar found")
            select = Select(select_bar)
            select.select_by_value("last week")
            
            print("last week from select clicked")
        
        if self.inputs_instance.part_time_option == "Y":
            part_time_section = self.chromesettings.browser.find_element(By.CSS_SELECTOR,"input[data-qa='checkbox-partTime']")
            time.sleep(5)
            self.chromesettings.browser.execute_script("arguments[0].click();",part_time_section)
        elif self.inputs_instance.part_time_option == "n":
            pass
            
        if self.inputs_instance.remote == "Y":
            remote_section = self.chromesettings.browser.find_element(By.CSS_SELECTOR,"data-qa='remoteWorkingOption.label']")
            time.sleep(5)
            self.chromesettings.browser.execute_script("arguments[0].click();",remote_section)
                    
        elif self.inputs_instance.remote == "n":
            pass
       

            
            
        
        
    
  

        