from typing import *
from time import sleep
from random import random
from tqdm import tqdm
import pandas as pd
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

with open('consts.txt','r') as f:
    keyvals = [line.split("=",maxsplit=1) for line in f.readlines()]
consts: Dict[str,str] = {keyval[0]:keyval[1] for keyval in keyvals}
print_as: str = "Webscraper v4"

def getDriver(driver_path: str = consts["chrome_driver_path"], headless: bool =False) -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument("log-level=3")

    chrome_prefs = {
        "profile.default_content_setting_values": {
            "images": 2, #block images
            # "javascript": 2, #block JS
        }
    }
    chrome_options.experimental_options["prefs"] = chrome_prefs

    caps = {}
    caps['acceptInsecureCerts'] = True
    caps['acceptSslCerts'] = True
    chrome_options.set_capability("cloud:options",caps)
    
    service = Service(executable_path=driver_path)
    return webdriver.Chrome(
        # options=options, 
        service=service,
        options=chrome_options
    )

def loadElement(parent: Union[WebElement,webdriver.Chrome], by: str, query: str, maxWait: float = 0.1) -> WebElement:
    return WebDriverWait(parent, maxWait).until(
        EC.presence_of_element_located((getattr(By, by), query))
    )

def strictlyContains(tagName: str, query: str) -> str:
    searchIn = '@'+tagName if tagName!='.' else '.'
    return f"contains(concat(' ', normalize-space({searchIn}), ' '), ' {query} ')"
def lowerCase(s: str) -> str:
    return f"translate({s}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"

class ResultItems:
    class SingleItem:
        def __init__(self) -> None:
            self.series = pd.Series(dtype='object')
        def initialize(self,field: str, val: Any = None) -> None:
            try:
                assert val is not None
                self.series[field] = str(val)
            except:
                self.series[field] = "DIDNOTLOAD"
        def indexed(self,index: int) -> pd.Series:
            self.series.name = index
            return self.series
        def __str__(self) -> str:
            return str(self.series.to_dict())
    def __init__(self, items: Iterator[SingleItem]) -> None:
        self.df = pd.DataFrame([item.indexed(i) for i,item in enumerate(items)]).fillna("-")
        self.df.index.name = "S.No."
    def writeToCSV(self,filepath: str) -> None:
        self.df.to_csv(filepath)
    def isEmpty(self) -> bool:
        return self.df.empty

Flags = Set[str]
class Scraper:
    @staticmethod
    def isDebug() -> bool:
        return False
    __page_limit__ = 20
    def getPageLimit(self) -> int:
        return self.__page_limit__
    def __init__(self, name: str, folder: str, isPageWise: bool = True) -> None:
        self.name = name
        self.folder = folder
        self.isPageWise = isPageWise
    def getURL(term: str, page: str, outOfStock: bool) -> str:
        raise NotImplementedError("Called function 'getURL' was not implemented in subclass")
    def parseOne(self, resultElt: WebElement, pgno: int, flags: Flags = set()) -> ResultItems.SingleItem:
        item = ResultItems.SingleItem()
        item.initialize(field="Page#",val=str(pgno) if pgno>=0 else "N/A")
        return item
    def getResultList(self, driver: webdriver.Chrome) -> List[Tuple[WebElement,Flags]]:
        raise NotImplementedError("Called function 'getResultList' was not implemented in subclass")
    def testOnLoad(self, driver: webdriver.Chrome) -> bool:
        return True
    def scrape(self, driver: webdriver.Chrome, term: str, maxPages: int, outOfStock: bool, silent: bool = False) -> ResultItems:
        if not self.isPageWise:
            raise NotImplementedError("Called function 'scrape' was not re-implemented in subclass even though isPageWise was set to False")
        resultItems: List[ResultItems.SingleItem] = []
        for i in range(1,maxPages+1):
            urli = self.getURL(term=term,page=i,outOfStock=outOfStock)
            if not silent:
                print(f"[{print_as}] Scraping page {i}: {urli}")
            driver.get(urli)
            if not self.testOnLoad(driver):
                break
            resultIterator = self.getResultList(driver=driver)
            if len(resultIterator)==0:
                break
            if not silent:
                resultIterator = tqdm(resultIterator,desc=f"[{print_as}] Parsing results")
            try:
                resultItems.extend([self.parseOne(elt,pgno=i,flags=flags) for elt,flags in resultIterator])
            except Exception as e:
                if self.isDebug():
                    print(e,flush=True)
                    input("ENTER to continue")
                if not silent:
                    print(" (skipped) ")
                continue
            finally:
                if not silent:
                    print(f" PAGE {i} DONE")
            if i<maxPages:
                randTime = 0.5+random()
                if not silent:
                    print(f"[{print_as}] Waiting for {randTime} seconds before loading next page...")
                sleep(randTime)
        return ResultItems(items=resultItems)
    