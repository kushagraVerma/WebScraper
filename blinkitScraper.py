from common import *

class BlinkitScraper(Scraper):

    def __init__(self,category: Optional[str] = None) -> None:
        super().__init__(name="Blinkit",folder="blinkit",isPageWise=False)

    def getURL(self,term: str, page: str, outOfStock: bool) -> str:
        s = f"https://blinkit.com/s/?q={term}"
        return s

    def parseOne(self, resultElt: WebElement, pgno: int = 1, flags: Flags = set()) -> ResultItems.SingleItem:
        item = super().parseOne(resultElt,pgno)
        
        try:
            title = resultElt.find_element(By.XPATH,"./div[1]/div[1]/div[1]").text
        except Exception as e:
            if self.isDebug():
                print(e)
            title = None
        item.initialize('Title',title)

        item.initialize('Rating (/5 stars)',"N/A")

        item.initialize('# of Ratings',"N/A")
        
        try:
            price = resultElt.find_element(By.XPATH,"./div[2]/div[1]/div[1]").text[1:]
        except Exception as e:
            if self.isDebug():
                print(e)
            price = None
        item.initialize('Price',price)
        
        try:
            units = resultElt.find_element(By.XPATH,f"./div[1]/div[2]").text
        except Exception as e:
            if self.isDebug():
                print(e)
            units = None
        item.initialize('Units',units)

        item.initialize('Available',"N/A")

        item.initialize('Sponsored',"N/A")

        if  self.isDebug() and len(flags):
            item.initialize("DEBUG","|".join(flags))

        return item

    def scrape(self, driver: webdriver.Chrome, term: str, maxPages: int, outOfStock: bool, silent: bool = False) -> ResultItems:
        urli = self.getURL(term=term,page=1,outOfStock=outOfStock)
        driver.get(urli)

        while True:
            try:
                loadElement(
                    parent=driver,
                    by='XPATH',
                    query="//div[contains(@class,'LocationOverlay')]",
                    maxWait=1
                )
                input(f"[{print_as}] Enter the location in the browser, then press ENTER in this terminal")
            except Exception as e:
                if self.isDebug():
                    print("Error trying to get location popup\n",e)
                break

        # prodCardPath = "//a[@data-testid='product-card']"
        searchContainerPath = "//div[contains(@class,'search-wrapper')]/div[contains(@style,'display: grid;')]"
        searchContainer = loadElement(
            parent=driver,
            by='XPATH',
            query=searchContainerPath,
            maxWait=1
        )

        nScrolls = 0
        resultIterator = []
        nElts = -1
        while len(resultIterator)>nElts and nScrolls<self.getPageLimit():
            nElts = len(resultIterator)
            resultIterator = searchContainer.find_elements(By.XPATH,".//div[@role='button' and .='ADD']/../..")
            driver.execute_script("arguments[0].scrollIntoView();",resultIterator[-1])
            sleep(1)
            nScrolls += 1
        
        if not silent:
            resultIterator = tqdm(resultIterator, desc=f"[{print_as}] Parsing results")
        return ResultItems(items=map(
            lambda resultElt: self.parseOne(resultElt),
            resultIterator
        ))