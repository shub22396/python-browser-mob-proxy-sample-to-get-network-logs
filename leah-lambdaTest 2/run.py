from ast import arg
from testing import Testing
import time
from multiprocessing import Process
import argparse
import json
from page import Page

def test(config, customer_id, customer_name, use_random_ua, device_type, headless):
    try:
        bot = Testing(config=config, customer_id=customer_id, customer=customer_name, use_random_ua=use_random_ua, device_type=device_type, headless=headless)
        try:
            bot.land_home_page()
        except Exception as exp:
            print(f"FAILED TO LAND ON HOME PAGE, Error {exp}")
        try:
            bot.accept_cookie()
        except Exception as exp:
            print(f"FAILED TO ACCEPT COOKIE, Error {exp}")
        try:
            bot.switch_locale()
        except Exception as exp:
            print(f"FAILED TO SWITCH LOCALE, Error {exp}")
        try:
            bot.check_home_page()
        except Exception as exp:
            print(f"FAILED ON HOME PAGE, Error {exp}")
        try:    
            bot.go_wishlist()
        except Exception as exp:
            print(f"FAILED ON WISHLIST PAGE, Error {exp}")
        try:    
            bot.go_page_by_url(page_type=Page.WISHLIST)
        except Exception as exp:
            print(f"FAILED ON WISHLIST PAGE, Error {exp}")
        try:
            bot.go_plp()
        except Exception as exp:
            print(f"FAILED ON PLP PAGE, Error {exp}")
        try:
            bot.go_page_by_url(page_type=Page.PLP)
        except Exception as exp:
            print(f"FAILED ON PLP PAGE, Error {exp}")
    except Exception as e:
        if 'in PATH' in str(e):
            print(
                'You are trying to run the bot from command line \n'
                'Please add to PATH your Selenium Drivers \n'
                'Windows: \n'
                '    set PATH=%PATH%;C:path-to-your-folder \n \n'
                'Linux: \n'
                '    PATH=$PATH:/path/to/your/folder/ \n'
            )
        else:
            raise

def get_config(customer_id, locale, device_type):
    with open('config.json') as config_file:
        config_file = json.load(config_file)
    config = {}
    customer_name = ""
    use_random_ua = True
    for idx, obj in enumerate(config_file):
        if obj['customer_id'] == customer_id:
            configs = obj['configs']
            if device_type == "mobile":
                config_by_device_type = 'mobile_configs'
            else:
                config_by_device_type = 'desktop_configs'
            if locale == "default":
                config = configs[0][config_by_device_type]
            else:
                for i, config_by_locale in enumerate(configs):
                    if config_by_locale['locale'].lower() == locale.lower():
                        config = config_by_locale[config_by_device_type]
            customer_name = obj['customer']
            use_random_ua = obj['use_random_ua']
    return config, customer_name, use_random_ua

# Run: 
def main(arg_list):
    mode, customer_id, locale, device_type, headless, page_type  = [arg for arg in arg_list]
    config, customer_name, use_random_ua = get_config(customer_id, locale, device_type)
    if config == {}:
        print(f'Customer Configuration Info Not Found for id {customer_id}, locale {locale}, device_type {device_type}')
        quit()
    start_time = time.time()
    if mode == 'general':
        test(config, customer_id, customer_name, use_random_ua, device_type, headless)
    else:
        print("Invalid mode")
    print("--- Running time: %s seconds ---" % round((time.time() - start_time), 2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Testing...")
    parser.add_argument("-m", "--mode", dest="mode",
        help="general mode tests for element integration, 404 mode only tests for 404 probems")
    parser.add_argument("-c", "--cid", dest="customer_id",
        help="customer id")
    parser.add_argument("-l", "--locale", dest="locale", default="default",
        help="locale")
    parser.add_argument("-d", "--devicetype", dest="device_type", default="default",
        help="device type")
    parser.add_argument("-headless", "--headless", dest="headless",
        help="No testing browser window pop-up", action="store_true")
    parser.add_argument("-pt", "--pagetype", dest="page_type", default="pdp",
        help="page type for one page testing")
    args = parser.parse_args()

    arg_list = [args.mode, args.customer_id, args.locale, args.device_type, args.headless, args.page_type]
    main(arg_list)