from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def getDriver(driver_path,headless=False):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument("log-level=3")

    ### This blocks images and javascript requests
    chrome_prefs = {
        "profile.default_content_setting_values": {
            "images": 2,
            # "javascript": 2,
        }
    }
    chrome_options.experimental_options["prefs"] = chrome_prefs

    caps = webdriver.DesiredCapabilities.CHROME.copy()
    caps['acceptInsecureCerts'] = True
    caps['acceptSslCerts'] = True

    driver = webdriver.Chrome(
        # options=options, 
        executable_path=driver_path,
        options=chrome_options,
        desired_capabilities=caps
    )

    return driver

def waitNLoad(parentElt,waitMax,bystr,qstr):
    return WebDriverWait(parentElt, waitMax).until(
        EC.presence_of_element_located((getattr(By, bystr), qstr))
    )