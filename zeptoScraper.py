from common import *

class ZeptoScraper(Scraper):

    def __init__(self,category: Optional[str] = None) -> None:
        super().__init__(name="Zepto",folder="zepto",isPageWise=False)

    def getURL(self,term: str, page: str, outOfStock: bool) -> str:
        s = f"https://www.zeptonow.com/search?query={term}"
        return s

    def parseOne(self, resultElt: WebElement, pgno: int = 1, flags: Flags = set()) -> ResultItems.SingleItem:
        item = super().parseOne(resultElt,pgno)
        
        try:
            titleElt = resultElt.find_element(By.XPATH,".//h5")
            title = titleElt.text
        except Exception as e:
            if self.isDebug():
                print(e)
            title = None
        item.initialize('Title',title)

        try:
            ratingDiv = titleElt.find_element(By.XPATH,"./following::div[1]")
            ratings = ratingDiv.find_element(By.XPATH,".//p[1]").text
            nRatings = ratingDiv.find_element(By.XPATH,".//p[2]").text.strip("()")
        except Exception as e:
            if self.isDebug():
                print(e)
            ratings = None
            nRatings = None
        item.initialize('Rating (/5 stars)',ratings)
        item.initialize('# of Ratings',nRatings)
        
        try:
            pricingDiv = resultElt.find_element(By.XPATH,".//img[@data-testid='product-card-image']/parent::div/following::div[1]")
            price = pricingDiv.find_element(By.XPATH,".//p[1]").text[1:]
            try:
                originalPrice = pricingDiv.find_element(By.XPATH,".//p[2]").text[1:]
            except Exception as e:
                originalPrice = price
        except Exception as e:
            if self.isDebug():
                print(e)
            price = None
            originalPrice = None
        item.initialize('Price',price)
        item.initialize('Original Price',originalPrice)
        
        try:
            units = ratingDiv.find_element(By.XPATH,f"./following::div[1]").text
        except Exception as e:
            if self.isDebug():
                print(e)
            units = None
        item.initialize('Units',units)

        try:
            unavailableDiv = resultElt.find_element(By.XPATH,f".//img[@alt='ring-bell-icon']")
            available = "NO"
        except Exception as e:
            if self.isDebug():
                print(e)
            available = "YES"
        item.initialize('Available',available)

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
                    by='CSS_SELECTOR',
                    query=".location-popup-container",
                    maxWait=1
                )
                input(f"[{print_as}] Enter the location in the browser, then press ENTER in this terminal")
            except Exception as e:
                if self.isDebug():
                    print("Error trying to get location popup\n",e)
                break

        prodCardPath = "//a[@data-testid='product-card']"
        loadElement(
            parent=driver,
            by='XPATH',
            query=prodCardPath,
            maxWait=1
        )

        nScrolls = 0
        resultIterator = []
        nElts = -1
        while len(resultIterator)>nElts and nScrolls<self.getPageLimit():
            nElts = len(resultIterator)
            resultIterator = driver.find_elements(By.XPATH,prodCardPath)
            driver.execute_script("arguments[0].scrollIntoView();",resultIterator[-1])
            sleep(1)
            nScrolls += 1
        
        if not silent:
            resultIterator = tqdm(resultIterator, desc=f"[{print_as}] Parsing results")
        return ResultItems(items=map(
            lambda resultElt: self.parseOne(resultElt),
            resultIterator
        ))