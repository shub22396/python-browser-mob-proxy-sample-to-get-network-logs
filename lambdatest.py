
from pickle import TRUE
import unittest
import time
import os
import json
import subprocess
import datetime
import pyautogui
from weakref import proxy
from selenium import webdriver
from browsermobproxy import Server
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


username = "shubhamr"  # Replace the username
access_key = "dl8Y8as59i1YyGZZUeLF897aCFvIDmaKkUU1e6RgBmlgMLIIhh"  # Replace the access key


class FirstSampleTest(unittest.TestCase):
    
    # Generate capabilites from here: https://www.lambdatest.com/capabilities-generator/
    # setUp runs before each test case and
    def setUp(self):
        self.server = Server(path="/Users/shubhamr/Downloads/python-selenium-sample-master3/browsermob-proxy-2.1.4/bin/browsermob-proxy")
        
        
        self.server.start()
        time.sleep(10)
        #portn = str(self.server.getPort())

        self.proxy = self.server.create_proxy()
       
        time.sleep(2)
        proxyf=format(self.proxy.proxy)

        self.port= proxyf[10:14]


        print('port-------',self.port)
        print('proxy-------',proxyf)

        shell = './LT --user shubhamr@lambdatest.com --key dl8Y8as59i1YyGZZUeLF897aCFvIDmaKkUU1e6RgBmlgMLIIhh --ingress-only  --verbose --proxy-host localhost --proxy-port '+self.port
        print('------------->',shell)
        subprocess.Popen(shell,shell=True)
        print('Tunnel initiated')





        desired_caps = {
            'LT:Options': {
                "build": "Python Demo",  # Change your build name here
                "name": "Python Demo Test",  # Change your test name here
                "deviceName": "iPhone 12",
                "platformName": "ios",
                "console": 'true',  # Enable or disable console logs
                "platformVersion": '14.5',  # Enable or disable network logs
                "tunnel": True,
                #Enable Smart UI Project
                #"smartUI.project": "<Project Name>"
            },
            
            #"browserName": "firefox",
            #"browserVersion": "latest",
        }

        # options = webdriver.ChromeOptions()
        # options.browser_version = "105.0"
        # options.platform_name = "Windows 10"
        # options.add_argument('--proxy-server='+proxyf)
        # lt_options = {};
        # lt_options["username"] = "shubhamr";
        # lt_options["accessKey"] = "CCCCTfelp95y0WKq0MSKORBzWD7xpFGOTv5KlMTZ18qnAcGjId";
        # lt_options["project"] = "Untitled";
        # lt_options["selenium_version"] = "4.0.0";
        # lt_options["network"] = False;
        # lt_options["tunnel"] = True;
        # options.set_capability('LT:Options', lt_options);

        # Steps to run Smart UI project (https://beta-smartui.lambdatest.com/)
        # Step - 1 : Change the hub URL to @beta-smartui-hub.lambdatest.com/wd/hub
        # Step - 2 : Add "smartUI.project": "<Project Name>" as a capability above
        # Step - 3 : Run "driver.execute_script("smartui.takeScreenshot")" command wherever you need to take a screenshot 
        # Note: for additional capabilities navigate to https://www.lambdatest.com/support/docs/test-settings-options/
        time.sleep(5)
        self.driver = webdriver.Remote(
            command_executor="http://{}:{}@hub.lambdatest.com/wd/hub".format(
                username, access_key),
            desired_capabilities=desired_caps)
     
        

     


# tearDown runs after each test case


    def tearDown(self):
        self.driver.quit()
        self.proxy.close()
        pyautogui.hotkey('ctrl', 'c')
        #subprocess.Popen("",shell=True)

    # """ You can write the test cases here """
    def test_demo_site(self):

        # try:
        driver = self.driver
        abc= self.proxy
        print('abc',abc)
        #driver.implicitly_wait(10)
        #driver.set_page_load_timeout(30)
        #driver.set_window_size(1920, 1080)

        # Url
        url = "https://www.google.com/"
        self.proxy.new_har(url,options={'captureContent': True,'captureHeaders': True})
        self.proxy.new_har(url)
        print('Loading URL')
        driver.get(url)
        time.sleep(10)
        #driver.get("https://lambdatest.com")
        #time.sleep(10)
        result = json.dumps(self.proxy.har, ensure_ascii=False)

        #print ("Result Logs----->",result)

        # for ent in result:
        #     print (self.proxy.har[ent])

       # datetime1 = datetime.datetime.now()
        
        har_file = open(self.port + '.har', 'w')
        har_file.write(str(result))
        har_file.close()

        

      
            

        

        # Let's select the location
        # driver.find_element(By.ID, "headlessui-listbox-button-1").click()
        # location = driver.find_element(By.ID, "Bali")
        # location.click()
        # print("Location is selected as Bali.")

        #Take Smart UI screenshot
        #driver.execute_script("smartui.takeScreenshot")

        # Let's select the number of guests
        # driver.find_element(By.ID, "headlessui-listbox-button-5").click()
        # guests = driver.find_element(By.ID, "2")
        # guests.click()
        # print("Number of guests are selected.")

        # Searching for the results
        # search = driver.find_element(By.XPATH, "//*[@id='search']")
        # assert search.is_displayed(), "Search is not displayed"
        # search.click()
        # driver.implicitly_wait(3)

        # Let's select one of the hotels for booking
        # reserve = driver.find_element(By.ID, "reserve-now")
        # reserve.click()
        # driver.implicitly_wait(3)
        # proceed = driver.find_element(By.ID, "proceed")
        # proceed.click()
        # driver.implicitly_wait(3)
        # print("Booking is confirmed.")

        # Let's download the invoice
        # # download = driver.find_element(By.ID, "invoice")
        # if (download.is_displayed()):
        #     download.click()
        #     driver.execute_script("lambda-status=passed")
        #     print("Tests are run successfully!")
        # else:
        #     driver.execute_script("lambda-status=failed")


if __name__ == "__main__":
    unittest.main()
