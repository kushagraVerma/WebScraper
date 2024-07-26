from common import *

class FlipkartScraper(Scraper):
    @staticmethod
    def parseCategory(category: Optional[str] = None) -> Tuple[str,str]:
        if category == "GROCERY":
            return "Flipkart Grocery","flipkart_grocery"
        return "Flipkart","flipkart"

    def __init__(self,category: Optional[str] = None) -> None:
        self.category: Optional[str] = category
        name,folder = FlipkartScraper.parseCategory(category)
        super().__init__(name,folder)

    def getURL(self,term: str, page: str, outOfStock: bool) -> str:
        s = f"https://www.flipkart.com/search?q={term}&page={page}"
        if self.category is not None:
            s += f"&marketplace={self.category}"
        if outOfStock:
            s += "&p%5B%5D=facets.availability%255B%255D%3DInclude%2BOut%2Bof%2BStock"
        return s

    def parseOne(self, resultElt: WebElement, pgno: int, flags: Flags = set()) -> ResultItems.SingleItem:
        item = super().parseOne(resultElt,pgno)
        
        try:
            if "tiles" in flags:
                title = resultElt.find_element(By.XPATH,".//a[boolean(@title) and not(descendant::img)]").text
            else:
                title = resultElt.find_element(By.XPATH,".//div[@class='KzDlHZ']").text
        except Exception as e:
            if self.isDebug():
                print(e)
            title = None
        item.initialize('Title',title)
        
        try:
            ratingSpan = resultElt.find_element(By.XPATH,".//span[contains(@id,'productRating_')]")
            rating = ratingSpan.text
        except Exception as e:
            if self.isDebug():
                print(e)
            rating = None
        item.initialize('Rating (/5 stars)',rating)
        
        try:
            nRatingSpanTxt = ratingSpan.find_element(By.XPATH,"./following-sibling::span[1]").text
            if "tiles" in flags:
                nRatings = nRatingSpanTxt.strip("()")
            else:
                nRatings = nRatingSpanTxt.split("Rating")[0].strip()
        except Exception as e:
            if self.isDebug():
                print(e)
            nRatings = None
        item.initialize('# of Ratings',nRatings)
        
        try:
            price = resultElt.find_element(By.XPATH,f".//div[{strictlyContains('class','Nx9bqj')}]").text[1:]
        except Exception as e:
            if self.isDebug():
                print(e)
            price = None
        item.initialize('Price',price)
        
        try:
            if self.category=="GROCERY":
                unitDiv = resultElt.find_element(By.XPATH,f".//button[not({strictlyContains('.','Add')})]//div[not(child::*)][1]")
            else:
                unitDiv = resultElt.find_element(By.XPATH,f".//div[{strictlyContains('class', 'NqpwHC')}]")
            units = unitDiv.text
        except Exception as e:
            if self.isDebug():
                print(e)
            units = None
        item.initialize('Units',units)

        try:
            containerPath = "." if "tiles" in flags else ".."
            unavailableDiv = resultElt.find_element(By.XPATH,f"{containerPath}//div[.='Currently unavailable']")
            available = "NO"
        except Exception as e:
            if self.isDebug():
                print(e)
            available = "YES"
        item.initialize('Available',available)

        try:
            sponElt = resultElt.find_element(By.XPATH,".//div[@class='xgS27m' or @class='_4m3oFf' or @class='f8qK5m']")
            sponsored = "YES"
        except Exception as e:
            if self.isDebug():
                print(e)
            sponsored = "NO"
        item.initialize('Sponsored',sponsored)

        if  self.isDebug() and len(flags):
            item.initialize("DEBUG","|".join(flags))

        return item
    
    def testOnLoad(self, driver: webdriver.Chrome) -> bool:
        if self.category is None:
            return True
        try:
            formElt = loadElement(
                parent=driver,
                by='XPATH',
                query="//input[@name='pincode']",
                maxWait=2
            )
        except:
            return True
        pincode = ""
        while True:
            pincode = input(f"[{print_as}] Flipkart Grocery requires a valid pincode (only local results will appear): ")
            if pincode.isnumeric() and len(pincode)==6:
                try:
                    formElt.send_keys(f"{pincode}")
                    formElt.submit()
                except:
                    print("Error submitting pincode!")
                    return False
                try:
                    sleep(3)
                    formElt = loadElement(
                        parent=driver,
                        by='XPATH',
                        query="//input[@name='pincode']",
                        maxWait=2
                    )
                    print("Not available for this area!")
                    return False
                except:
                    return True
            else:
                print("Invalid pincode!")

    def getResultList(self, driver: webdriver.Chrome) -> List[Tuple[WebElement,Flags]]:
        resultList: List[Tuple[WebElement,Flags]] = []

        try:
            containerElt = loadElement(parent=driver, by='ID', query='container')
        except Exception as e:
            if self.isDebug():
                print("ERROR LOADING MAIN CONTAINER",e)
            return []

        flags: Flags = set()
        try:
            simpleEltsPath = "//div[boolean(@data-tkid)]//div[contains(@class,'row')]"
            resultList.extend([
                (simpleElt,flags.copy()) for simpleElt in 
                containerElt.find_elements(By.XPATH,simpleEltsPath)
            ])
        except Exception as e:
            if self.isDebug():
                print("ERROR FINDING SIMPLE ELEMENTS",e)

        flags.add("tiles")
        try:
            tileEltsPath = "//div[boolean(@data-tkid) and descendant::a[boolean(@title) and not(descendant::img)]]"
            tileElts = driver.find_elements(By.XPATH,tileEltsPath)
            resultList.extend([
                (tileElt,flags.copy()) for tileElt in 
                containerElt.find_elements(By.XPATH,tileEltsPath)
            ])
        except Exception as e:
            if self.isDebug():
                print("ERROR FINDING SIMPLE ELEMENTS",e)

        return resultList