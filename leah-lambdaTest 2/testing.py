import os
import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys 
from fake_useragent import UserAgent
import json
import tenacity
import requests
import cloudscraper
import random
from datetime import datetime
import boto3
import re
from slack_sdk import WebClient
from page import Page
from config_map import config_map
from browsermobproxy import Server

from weakref import proxy
import subprocess

username = "leah.fei"  # Replace the username
access_key = "8wnE6kBjEsRXG0D6GPi5gSpwBjM9jbYEsshR7Pcd97kNMKZluL"  # Replace the access key

class Testing(unittest.TestCase):
    def __init__(self, teardown=False, config={}, customer_id="", customer="", use_random_ua=True, device_type="desktop", headless=False, page_type='pdp', global_previous_recs=[]):
        self.server = Server(r"/home/leah/qa-automation/leah-lambdaTest/browsermob-proxy-2.1.4/bin/browsermob-proxy")
        self.server.start()
        # portn = str(self.server.getPort())

        self.proxy = self.server.create_proxy()
        time.sleep(2)
        proxyf=format(self.proxy.proxy)
        # get port number
        self.port= proxyf[10:14]
        print('port-------',self.port)
        print('proxy-------',proxyf)
        # start tunnel
        shell = './LT  --user leah.fei@xgen.ai --key 8wnE6kBjEsRXG0D6GPi5gSpwBjM9jbYEsshR7Pcd97kNMKZluL --ingress-only  --verbose --proxy-host localhost --proxy-port '+self.port
        print('------------->',shell)
        subprocess.Popen(shell,shell=True)
        print('Tunnel initiated')

        options = SafariOptions()
        options.browser_version = "15.0"
        lt_options = {}
        lt_options["project"] = "try_iphone"
        lt_options["platformName"] = "ios"
        lt_options["deviceName"] = "iPhone 13"
        lt_options["platformVersion"] = "15.0"
        lt_options["tunnel"] = True
        # display network logs
        lt_options["network"] = True
        lt_options["isRealMobile"] = True
        options.set_capability('LT:Options', lt_options)
        options.set_capability(
            "loggingPrefs", {"performance": "ALL", "browser": "ALL"}
        )

        self.teardown = teardown
        self.config = config
        self.use_random_ua = use_random_ua
        self.global_previous_recs = global_previous_recs
        self.fourOfour_links = []
        self.customer = customer
        self.customer_id = customer_id
        self.slack_url = "https://hooks.slack.com/services/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"
        self.channel_id = "C043L3XCNQ1"
        self.client = WebClient(token="xoxb-386956934151-4109621571186-VCd1wyNaQWVJrU7riwKAMIBz")
        self.render_data = []
        self.predictions = []
        self.config_map = config_map
        # self.driver = webdriver.Remote(
        #     options=options,
        #     command_executor="https://{}:{}@hub.lambdatest.com/wd/hub".format(username, access_key),
        # )
        self.driver = webdriver.Remote(
            options=options,
            command_executor="https://{}:{}@mobile-hub.lambdatest.com/wd/hub".format(username, access_key),
        )

        # All methods with retries and backoff
        retry = tenacity.retry(reraise=True, wait=tenacity.wait_exponential(), stop=tenacity.stop_after_attempt(config['retry_times']))
        self.land_home_page = retry(self._land_home_page)
        self.check_home_page = retry(self._check_home_page)
        self.accept_cookie = retry(self._accept_cookie)
        self.must_accept_cookie = retry(self._must_accept_cookie)
        self.switch_locale = retry(self._switch_locale)
        self.change_test_group = retry(self._change_test_group)
        self.go_wishlist = retry(self._go_wishlist)
        self.go_page_by_url = retry(self._go_page_by_url)
        self.element_visible = retry(self._element_visible)
        self.go_plp = retry(self._go_plp)
        self.get_xgen_events = retry(self._get_xgen_events)
        self.check_render_status = retry(self._check_render_status)
        self.check_event_status = retry(self._check_event_status)
        self.check_current_page_404 = retry(self._check_current_page_404)
        self.get_next_pdp_url = retry(self._get_next_pdp_url)
        self.get_recs_and_next_page = retry(self._get_recs_and_next_page)
        self.check_current_page_static_recs = retry(self._check_current_page_static_recs)

        
    # Close the window once job done
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.server.stop()
            self.driver.quit()
            self.proxy.close()
            subprocess.Popen("",shell=True)

    def send_slack_message(self, payload, webhook):
        """Send a Slack message to a channel via a webhook. 
        Args:
            payload (dict): Dictionary containing Slack message, i.e. {"text": "This is a test"}
            webhook (str): Full Slack webhook URL for your chosen channel. 
        Returns:
            HTTP response code, i.e. <Response [503]>
        """
        return requests.post(webhook, json.dumps(payload))
    
    def slack_upload_file(self, file_name):
        self.client.files_upload(
            channels=self.channel_id,
            file=file_name,
        )

    # Land on home page by url
    def _land_home_page(self):
        time.sleep(3)        
        self.proxy.new_har(self.config['homepage_url'], options={'captureContent': True,'captureHeaders': True})
        self.proxy.new_har(self.config['homepage_url'])

        self.driver.get(self.config['homepage_url'])
        print('> Landed on Home Page')
        
        time.sleep(20)

        result = json.dumps(self.proxy.har, ensure_ascii=False)
        # print ("Result Logs----->",result)

        har_file = open(self.port + '.har', 'w')
        har_file.write(str(result))
        har_file.close()

    """Do several tests on the page:
    Routine:
        1. Land on page by url
            2. Check element_visibilty
            3. Check 404 links
            4. Check statis recommendations
        6. Refresh the page
            7. Check element_visibilty
            8. Check 404 links
    """
    def _check_home_page(self, general_mode=True):
        self.close_pop_ups()
        if 'homepage_elements' in self.config and self.config['homepage_elements']:
            print('> Checking home page')
            self.generate_random_ua()
            self.driver.get(self.config['homepage_url'])
            for element in self.config['homepage_elements']:
                self.element_visible(element)
            if general_mode:
                self.check_current_page_404()
                self.check_current_page_static_recs()
                print('> Refreshing')
                self.generate_random_ua()
                self.driver.refresh()
                for element in self.config['homepage_elements']:
                    self.element_visible(element)
                self.check_current_page_404()

    def _accept_cookie(self):
        if 'accept_cookie_btn_selector' in self.config:
            if 'cookie_mandatory' not in self.config or not self.config['cookie_mandatory']:
                self.click_when_clickable(self.config['accept_cookie_btn_selector'])
                print('> Cookie policy accepted')
            else:
                self.must_accept_cookie()

    # For some clients (e.g. Armani), we will render only if user accept the cookie policy
    def _must_accept_cookie(self):
        cookie_accepted = False
        print("must accept cookie...")
        while not cookie_accepted:
            self.generate_random_ua()
            self.land_home_page()
            self.click_when_clickable(self.config['accept_cookie_btn_selector'])
            cookie_accepted = True
            print('> Cookie policy accepted')

    # Switch locale
    def _switch_locale(self):
        if 'switch_locale_btn_selectors' in self.config:
            for selector in self.config['switch_locale_btn_selectors']:
                self.click_when_clickable(selector)
            print('> Locale switched')
 
    # Change to the ab testing group which we render on
    def _change_test_group(self):
        if 'target_test_group' in self.config and self.config['target_test_group']:
            ab_cookie = self.driver.get_cookie('xgen_ab_info')
            # print(ab_cookie)
            if ab_cookie != None:
                self.driver.delete_cookie('xgen_ab_info')
                value = json.loads(ab_cookie["value"])
                value.update({'testing_group_name': self.config['target_test_group']})
                ab_cookie.update({'value': json.dumps(value)})
                self.driver.add_cookie(ab_cookie)
            elif self.customer == "Gucci":
                self.driver.add_cookie({'name':'xgen_ab_info', 'value': json.dumps({'ab_test_id':'85232bb9-5bb2-44a9-9741-b513ee65b99e','percent':16,'testing_group_id':'316fd2a8-e953-414d-a014-fd5ba6f8c137','testing_group_name':'b'})})
            new_ab_cookie = self.driver.get_cookie('xgen_ab_info')
            # print(new_ab_cookie)
            print(f'> Set testing group to {self.config["target_test_group"]}')

    # Tested for element visibility after render success
    def _element_visible(self, element_id, one_page_mode=False):
        # WebDriverWait(self.driver, self.config['timeout']).until(
        #     lambda wd: wd.check_render_status(requests=wd.get_xgen_events(), element_id=element_id) == True)
        smel = self.driver.find_element(By.CSS_SELECTOR, '#XSE-'+element_id)
        visible = smel.value_of_css_property('display') != 'none'
        if visible:
            print(f"  > Xgen Element {element_id} visible")
            if one_page_mode:
                payload = {"text": f"*PASSED*: Tested element visibility on *{self.customer}* for element `{element_id}`"}
                self.send_slack_message(payload, self.slack_url)
        else:
            print(f"  > Xgen Element {element_id} NOT visible")
            if one_page_mode:
                payload = {"text": f"*FAILED*: Tested element visibility on *{self.customer}*\n<@U02KVV927HB> Xgen Element `{element_id}` NOT visible"}
                self.send_slack_message(payload, self.slack_url)

    # Do several tests on the page:
    def _go_wishlist(self):
        if 'wishlist_elements' in self.config and self.config['wishlist_elements']:
            self.generate_random_ua()
            self.click_when_clickable(self.config['wishlist_btn_selector'])
            print('> Landed on Wishlist Page')
            for element in self.config['wishlist_elements']:
                self.element_visible(element)
            self.check_current_page_404()
            print('> Refreshing')
            self.generate_random_ua()
            self.driver.refresh()
            for element in self.config['wishlist_elements']:
                self.element_visible(element)
            self.check_current_page_404()

    # Do several tests on the page:
    def _go_page_by_url(self, page_type, general_mode=True):
        url_of_page_type = self.config_map[page_type]['url']
        element_ids_of_page_type = self.config_map[page_type]['elements']
        if page_type == Page.PLP or page_type == Page.PDP:
            self.generate_random_ua()
            self.driver.get(self.config[url_of_page_type])
            print(f'> Landed on {page_type.value} by URL')
            if element_ids_of_page_type in self.config and self.config[element_ids_of_page_type]:
                for element in self.config[element_ids_of_page_type]:
                    self.element_visible(element)
                if general_mode:
                    self.check_current_page_404()
                    self.check_current_page_static_recs()
        elif element_ids_of_page_type in self.config and self.config[element_ids_of_page_type]:
            self.generate_random_ua()
            self.driver.get(self.config[url_of_page_type])
            print(f'> Landed on {page_type.value} by URL')
            for element in self.config[element_ids_of_page_type]:
                self.element_visible(element)
            if general_mode:
                self.check_current_page_404()
                self.check_current_page_static_recs()

    # Do several tests on the page:
    def _go_plp(self):
        self.generate_random_ua()
        if 'navigation_selector' in self.config:
            self.click_when_clickable(self.config['navigation_selector'])
        self.close_pop_ups()
        if 'category_plp_selector' in self.config:
            self.click_when_clickable(self.config['category_plp_selector'])
            print('> Landed on PLP')
            self.close_pop_ups()
            if 'plp_elements' in self.config and self.config['plp_elements']:
                for element in self.config['plp_elements']:
                    self.element_visible(element)
                self.check_current_page_404()
                print('> Refreshing')
                self.generate_random_ua()
                self.driver.refresh()
                for element in self.config['plp_elements']:
                    self.element_visible(element)
                self.check_current_page_404()

    # Get events fron network tab, and filter for 'xgen'
    def _get_xgen_events(self):
        logs_raw = self.driver.get_log("performance")
        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
        def log_filter(log_):
            return (
                # check if is an actual response
                log_["method"] == "Network.responseReceived"
                # filter for type json and xgen in url
                and "json" in log_["params"]["response"]["mimeType"]
                and "xgen" in log_["params"]["response"]["url"]
                # NOTE: can filter events by event_type by un-commenting the line below
                # and event_type in log_["params"]["response"]["url"]
            )
        requests = filter(log_filter, logs)
        return requests

    # Check status of xgen render request
    def _check_render_status(self, requests, element_id):
        self.render_data = []
        print(f"  > Checking render status")
        def log_filter(log_):
                return (
                    "prediction" in log_["params"]["response"]["url"]
                )
        events = list(filter(log_filter, requests))
        if len(events) < 1:
            print('    prediction Event Not Fired (yet)')
            time.sleep(1)
            return False
            # raise
        else:
            for event in events:
                resp_url = event["params"]["response"]["url"]
                resp_status = event["params"]["response"]["status"]
                print(f"    Caught {resp_status} {resp_url}")
                # check empty recommendation
                if element_id != "":
                    self.check_empty_rec(event, element_id)
                else:
                    self.render_data = self.get_render_data(event)
                # check render status
                if int(resp_status) != 200:
                    print('Render request got bad status')
                    return False
            return True

    # Get render_data from render request
    def get_render_data(self, event):
        request_id = event["params"]["requestId"]
        body = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
        render_data = json.loads(body['body'])['render_data']
        return render_data

    # Test for empty reccomendation
    def check_empty_rec(self, event, element_id):
        print(f"  > Checking empty recommendation for element {element_id}")
        render_data = self.get_render_data(event)
        if render_data == []:
            print('Got Empty Render Data')
        else:
            for data in render_data:
                if data['element']['element_id'] == element_id and data['prediction'] == []:
                    print(f"Got Empty Recommendation")
                    return 
                elif data['element']['element_id'] == element_id and data['prediction'] != []:
                    print("    Passed")
                    return 
            print(f"No render data found for element {element_id}")

    # Check status of xgen events
    def _check_event_status(self, requests, event_type):
        print(f"  > Checking {event_type} event status")
        def log_filter(log_):
            return (
                event_type in log_["params"]["response"]["url"]
            )
        req = requests
        events = list(filter(log_filter, req))
        if len(events) < 1:
            print(f'    {event_type} Event Not Fired (yet)')
            return False
        else:
            for event in events:
                resp_url = event["params"]["response"]["url"]
                resp_status = event["params"]["response"]["status"]
                print(f"    Caught {resp_status} {resp_url}")
                if int(resp_status) != 200:
                    print('{event_type} Event with Bad Status')
                    return False
            return True

    # Get all ids of xgen smart elements who has at least one 404 links
    def get_elements_ids_with_404(self, bad_links):
        bad_element_ids = []
        for link in bad_links:
            id = re.search(pattern="xse=(.+?)$", string=link).group(1)
            if id not in bad_element_ids:
                bad_element_ids.append(id)
        return bad_element_ids

    # Get full prediction data of the samrt element with 404 links
    def get_predictions_with_404(self, bad_element_ids):
        for id in bad_element_ids:
            for data in self.render_data:
                if data['element']['element_id'] == id:
                    self.predictions.append(data['prediction'])

    def _check_current_page_404(self, in_404_mode=False):
        next_page = ''
        bad_links = []
        if 'get_link_sleep_time' in self.config:
            time.sleep(float(self.config['get_link_sleep_time']))
        if in_404_mode:
            # WebDriverWait(self.driver, self.config['timeout']).until(
            #     lambda wd: wd.check_render_status(requests=wd.get_xgen_events(), element_id="") == True)
            if self.customer in ["Feeders-Pet-Supply", "Gucci"]:
                time.sleep(5)
        # Find all html elements that have a rec product url as child and can be selected simply by rec_urls_selector
        rec_elements = self.driver.find_elements(By.CSS_SELECTOR, self.config['rec_urls_selector'])
        if len(rec_elements) > 0:
            # Get the rec url and check for 404 status
            for element in rec_elements:
                url = element.get_attribute("href").replace("http://", "https://")
                if 'get_link_sleep_time' in self.config:
                    time.sleep(float(self.config['get_link_sleep_time']))
                resp = self.check_url(url)
                if resp.status_code == 404 or resp.status_code == 410:
                    # print(f"{resp.status_code} {url}")
                    bad_links.append(url)
                else:
                    if next_page == '':
                        next_page = self.get_next_pdp_url([element])
                #     print(f"{resp.status_code} {url}")
            if len(bad_links) > 0:
                print(f'404 recommendation links found: {bad_links}')
                self.fourOfour_links.extend(bad_links)
                # Get element ids with 404 links, then get prediction data from render
                if in_404_mode:
                    print('  > Getting prediction')
                    bad_element_ids = self.get_elements_ids_with_404(bad_links)
                    self.get_predictions_with_404(bad_element_ids)
            else:
                print('  > Recommendation Links all valid (No 404s)')
        else:
            print('Got no recommendation links when checking 404s')
        return next_page

    # Get next testing page
    # excluding some url pattern because, for example, we don't render on Gucci's diy product page
    def _get_next_pdp_url(self, rec_elements):
        if 'check_404_exclude_url_pattern' not in self.config:
            return rec_elements[0].get_attribute("href").replace("http://", "https://")
        else:
            for element in rec_elements:
                if self.config['check_404_exclude_url_pattern'] not in element.get_attribute("href"):
                    return element.get_attribute("href").replace("http://", "https://")
            return ''

    # Helper function for static rec test: get rec urls and next tessting page url
    def _get_recs_and_next_page(self, is_static_mode):
        if is_static_mode:
            pdp_element = self.driver.find_element(By.CSS_SELECTOR, '#XSE-'+self.config['pdp_elements'][0])
            rec_elements = pdp_element.find_elements(By.CSS_SELECTOR, self.config['rec_urls_selector'])
        else:
            rec_elements = self.driver.find_elements(By.CSS_SELECTOR, self.config['rec_urls_selector'])
        recs = []
        next_page = ''
        if len(rec_elements) > 0:
            next_page = self.get_next_pdp_url(rec_elements)
            for element in rec_elements:
                url = element.get_attribute("href").replace("http://", "https://").split('?')[0]
                recs.append(url)
        else:
            print('Got no recs when checking static recs')
        return recs, next_page

    # Check static recommendation
    # Be careful when using this fn, recs is expected to be static when repeatedly landed on same page
    def _check_current_page_static_recs(self):
        print('  > Checking static recs')
        recs, next_page = self.get_recs_and_next_page(is_static_mode=False)
        if self.global_previous_recs != []:
            shorter_len = len(recs) if len(recs) <= len(self.global_previous_recs) else len(self.global_previous_recs)
            if recs[0:shorter_len] == self.global_previous_recs[0:shorter_len]:
                # # PROD_CODE for gucci demo
                # recs_code = self.link_to_code(recs)
                # print(f"Recs are same as previous page: {recs_code}")
                print(f"Recs are same as previous page: {recs}")
            else:
                # # PROD_CODE for demo
                # recs_code = self.link_to_code(recs)
                # print(f"    Passed: {recs_code}")
                print(f"    Passed: {recs}")
        self.global_previous_recs = recs

    # Handle robot detection
    def generate_random_ua(self):
        if self.use_random_ua:
            ua = UserAgent()
            # userAgent = ua.random
            # self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": f"{userAgent}"})

    # Convert link to code for gucci demo
    def link_to_code(self, link_list):
        code_list = []
        for link in link_list:
            code = link.split('?')[0].rsplit('-', 1)[-1]
            code_list.append(code)
        return code_list

    # Retry menthod for 404 mode
    def retry_with_backoff(retries=5, backoff_in_seconds=1):
        def rwb(f):
            def wrapper(*args, **kwargs):
                x = 0
                while True:
                    try:
                        return f(*args, **kwargs)
                    except:
                        if x == retries:
                            raise
                        sleep = backoff_in_seconds * 2 ** x \
                            + random.uniform(0, 1)
                        time.sleep(sleep)
                        x += 1
            return wrapper
        return rwb

    @retry_with_backoff(retries=6)
    # Fetch url
    def check_url(self, url):
        scraper = cloudscraper.create_scraper()
        r = scraper.get(url, timeout=2)
        # print(r)
        return r

    # Wait for the html element to be clickable, and click 
    def click_when_clickable(self, html_element):
        WebDriverWait(self.driver, self.config['timeout']).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, html_element), 
            )
        ).click()