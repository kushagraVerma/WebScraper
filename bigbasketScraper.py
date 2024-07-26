from common import *
from urllib.parse import urlparse,parse_qs

class BigbasketScraper(Scraper):
    __page_limit__ = 8
    def __init__(self) -> None:
        super().__init__(name="BigBasket",folder="bigbasket",isPageWise=False)

    def getURL(self,term: str, page: str, outOfStock: bool) -> str:
        s = f"https://www.bigbasket.com/ps/?q={term}&page={page}"
        # if outOfStock:
        return s

    def parseOne(self, resultElt: WebElement, pgno: int, flags: Flags = set()) -> ResultItems.SingleItem:
        item = super().parseOne(resultElt,pgno)

        try:
            title = resultElt.find_element(By.XPATH,".//h3[not(child::*)]").text
        except Exception as e:
            if self.isDebug():
                print(e)
            title = None
        finally:
            item.initialize("Title",title)

        try:
            reviewDiv = resultElt.find_element(By.XPATH,f".//div[contains(@class,'ReviewsAndRatings___StyledDiv')]")
            rating = reviewDiv.find_element(By.XPATH,f"./span[1]").text
            nRatings = reviewDiv.find_element(By.XPATH,f"./span[2]").text.split("Rating")[0].strip()
        except Exception as e:
            if self.isDebug():
                print(e)
            rating = None
            nRatings = None
        finally:
            item.initialize("Rating (/5 stars)",rating)
            item.initialize("# of Ratings",nRatings)

        try:
            priceSpan = resultElt.find_element(By.XPATH,f".//div[contains(@class,'Pricing___StyledDiv')]/span[1]")
            price = priceSpan.text[1:]
        except Exception as e:
            if self.isDebug():
                print(e)
            price = None
        finally:
            item.initialize("Price",price)
            
        try:
            unitSpanPath = ".//span[contains(@class,'PackChanger') or contains(@class,'PackSelector')]"
            units = resultElt.find_element(By.XPATH,unitSpanPath).text
        except Exception as e:
            if self.isDebug():
                print(e)
            units = None
        finally:
            item.initialize('Units',units)

        try:
            availableElt = loadElement(
                parent=resultElt, 
                by='XPATH', 
                query=f".//button[.='Add']"
            )
            available = "YES"
        except Exception as e:
            if self.isDebug():
                print(e)
            available = "NO"
            item.initialize("Price",None)
        finally:
            item.initialize('Available',available)
            
        try:
            sponElt = resultElt.find_element(By.XPATH,".//span[not(child::*) and .='Sponsored']")
            sponsored = "YES"
        except Exception as e:
            if self.isDebug():
                print(e)
            sponsored = "NO"
        finally:
            item.initialize('Sponsored',sponsored)

        if  self.isDebug() and len(flags):
            item.initialize("DEBUG","|".join(flags))

        return item

    def scrape(self, driver: webdriver.Chrome, term: str, maxPages: int, outOfStock: bool, silent: bool = False) -> ResultItems:
        urli = self.getURL(term=term,page=1,outOfStock=outOfStock)
        driver.get(urli)
        try:
            resultsElement = loadElement(
                parent=driver,
                by='XPATH',
                query="//ul[parent::section/parent::section and child::li[contains(@class,'Paginate')]]"
            )
        except Exception as e:
            if self.isDebug():
                print("ERROR FINDING RESULTS ELEMENT",e)
            return ResultItems([])

        nScrolls = 0
        if not silent:
            print(f"[{print_as}] Scrolling through {urli}",flush=True)
        while nScrolls<self.getPageLimit():
            try:
                if not silent:
                    print(f"Scroll#{nScrolls}",end="\r",flush=True)
                scrollElt = loadElement(
                    parent=resultsElement, 
                    by='XPATH', 
                    query="../following-sibling::div//div[contains(@class,'Shimmers')]",
                    maxWait=1
                )
                driver.execute_script("arguments[0].scrollIntoView();",scrollElt)
                sleep(1)
                driver.execute_script("window.scrollTo(0,0);")
                sleep(1)
            except Exception as e:
                if self.isDebug():
                    print(e)
                break
            nScrolls += 1
        if not silent:
            print(f"[{print_as}] Scrolling complete")

        try:
            resultIterator = resultsElement.find_elements(By.XPATH,".//li[contains(@class,'Paginate')]")
            assert len(resultIterator) != 0
        except:
            return ResultItems([])

        if not silent:
            resultIterator = tqdm(resultIterator, desc=f"[{print_as}] Parsing results")
        return ResultItems(items=map(
            lambda resultElt: self.parseOne(resultElt,pgno=-1),
            resultIterator
        ))