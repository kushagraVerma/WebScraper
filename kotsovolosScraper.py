from common import *

class KotsovolosScraper(Scraper):
    __page_limit__ = 8

    def __init__(self) -> None:
        super().__init__(name="Kotsovolos",folder="kotsovolos")

    def getURL(self,term: str, page: str = None, outOfStock: bool = None) -> str:
        s = f"https://www.kotsovolos.gr/SearchDisplay?q={term}"
        return s

    def parseOne(self, resultElt: WebElement, pgno: int, flags: Flags = set()) -> ResultItems.SingleItem:
        item = super().parseOne(resultElt,pgno)

        try:
            title = loadElement(
                parent=resultElt,
                by='XPATH',
                query=".//a[contains(@class,'product-name')]",
                maxWait=1
            ).text
        except Exception as e:
            if self.isDebug():
                print(e)
            title = None
        finally:
            item.initialize("Title",title)

        try:
            reviewElt = loadElement(
                parent=resultElt,
                by='XPATH',
                query=".//a[contains(@href,'showReviews')]",
                maxWait=1
            )
            ratingSpan = reviewElt.find_element(By.XPATH,f"./span")
            rating = ratingSpan.get_attribute("aria-label").split()[0]
            nRatingsP = reviewElt.find_element(By.XPATH,f"./p")
            nRatings = nRatingsP.text.strip("()").strip()
        except Exception as e:
            if self.isDebug():
                print(e)
            rating = None
            nRatings = "0"
        finally:
            item.initialize("Rating (/5 stars)",rating)
            item.initialize("# of Ratings",nRatings)

        try:
            priceDiv = loadElement(
                parent=resultElt,
                by='XPATH',
                query=".//div[contains(@class,'price-cta-wrp')]/div[not(descendant::button)]//p",
                maxWait=1
            )
            price = priceDiv.text[1:].strip()
        except Exception as e:
            if self.isDebug():
                print(e)
            price = None
        finally:
            item.initialize("Price",price)
            
        # try:
        #     unitSpanPath = ".//span[contains(@class,'PackChanger') or contains(@class,'PackSelector')]"
        #     units = resultElt.find_element(By.XPATH,unitSpanPath).text
        # except Exception as e:
        #     if self.isDebug():
        #         print(e)
        #     units = None
        # finally:
        #     item.initialize('Units',units)
        item.initialize('Units',None)

        # try:
        #     availableElt = loadElement(
        #         parent=resultElt, 
        #         by='XPATH', 
        #         query=f".//button[.='Add']"
        #     )
        #     available = "YES"
        # except Exception as e:
        #     if self.isDebug():
        #         print(e)
        #     available = "NO"
        #     item.initialize("Price",None)
        # finally:
        #     item.initialize('Available',available)
        item.initialize('Available',"YES")
            
        # try:
        #     sponElt = resultElt.find_element(By.XPATH,".//span[not(child::*) and .='Sponsored']")
        #     sponsored = "YES"
        # except Exception as e:
        #     if self.isDebug():
        #         print(e)
        #     sponsored = "NO"
        # finally:
        #     item.initialize('Sponsored',sponsored)
        item.initialize('Sponsored',None)

        if  self.isDebug() and len(flags):
            item.initialize("DEBUG","|".join(flags))

        return item

    def scrape(self, driver: webdriver.Chrome, term: str, maxPages: int, outOfStock: bool, silent: bool = False) -> ResultItems:
        urli = self.getURL(term=term)
        driver.get(urli)
        sleep(2)

        nLoads = 0
        if not silent:
            print(f"[{print_as}] Loading results in {urli}",flush=True)
        while nLoads<self.getPageLimit():
            try:
                if not silent:
                    print(f"Load#{nLoads}",end="\r",flush=True)
                loadBtn = loadElement(
                    parent=driver, 
                    by='XPATH', 
                    query="//button[descendant::p[contains(.,'Φόρτωση επόμενων')]]",
                    maxWait=3
                )
                driver.execute_script("arguments[0].click();",loadBtn)
                sleep(1)
            except Exception as e:
                if self.isDebug():
                    print(e)
                break
            nLoads += 1
        if not silent:
            print(f"[{print_as}] Loading complete")

        try:
            _ = loadElement(
                parent=driver,
                by='XPATH',
                query=f"//div[{strictlyContains('class','product-card')}]/div",
                maxWait=1
            )
        except Exception as e:
            if self.isDebug():
                print("ERROR FINDING RESULTS ELEMENT",e)
            return ResultItems([])
        
        resultIterator = driver.find_elements(By.XPATH,f"//div[{strictlyContains('class','product-card')}]/div")

        if not silent:
            resultIterator = tqdm(resultIterator, desc=f"[{print_as}] Parsing results")
        return ResultItems(items=map(
            lambda resultElt: self.parseOne(resultElt,pgno=-1),
            resultIterator
        ))