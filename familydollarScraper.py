from common import *

class FamilyDollarScraper(Scraper):

    def __init__(self) -> None:
        super().__init__(name="Family Dollar",folder="familydollar")

    def getURL(self,term: str, page: str = None, outOfStock: bool = None) -> str:
        s = f"https://www.familydollar.com/searchresults?Ntt={term}"
        return s

    def parseOne(self, resultElt: WebElement, pgno: int, flags: Flags = set()) -> ResultItems.SingleItem:
        item = super().parseOne(resultElt,pgno)

        try:
            title = loadElement(
                parent=resultElt,
                by='XPATH',
                query=".//div[@class='product-title']",
                maxWait=1,
                awaitVisible=True
            ).text
        except Exception as e:
            if self.isDebug():
                print(e)
            title = None
        finally:
            item.initialize("Title",title)

        try:
            reviewDiv = loadElement(
                parent=resultElt,
                by='XPATH',
                query=".//div[contains(@class,'inline-rating')]",
                maxWait=1,
                awaitVisible=True
            )
            try:
                rating = reviewDiv.find_element(By.XPATH,f".//span[@class='bv-rating']").text
            except:
                rating = "N/A"
            nRatings = reviewDiv.find_element(
                By.XPATH,
                f".//span[@class='bv-rating-label']"
            ).get_attribute("innerHTML").strip().strip("()")
        except Exception as e:
            if self.isDebug():
                print(e)
            rating = None
            nRatings = None
        finally:
            item.initialize("Rating (/5 stars)",rating)
            item.initialize("# of Ratings",nRatings)

        try:
            priceDiv = loadElement(
                parent=resultElt,
                by='XPATH',
                query=".//div[@class='product-item-price']",
                maxWait=1,
                awaitVisible=True
            )
            price = priceDiv.text[1:]
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

        try:
            closePopupButton = loadElement(
                parent=driver,
                by='CSS_SELECTOR',
                query="div.alert-error a",
                maxWait=3,
                awaitClickable=True
            )
            closePopupButton.click()
        except Exception as e:
            if self.isDebug():
                print(e)

        parsedItems = []
        
        for i in range(maxPages):
            try:
                randTime = 2+random()
                if not silent:
                    print(f"[{print_as}] Waiting for {randTime} seconds before parsing...")
                sleep(randTime)
                _ = loadElement(
                    parent=driver,
                    by='CSS_SELECTOR',
                    query="div.product",
                    maxWait=5
                )
                resultElts = driver.find_elements(By.CSS_SELECTOR,"div.product")
            except:
                if not silent:
                    print(f"[{print_as}] No more results loaded!",flush=True)
                break
            if not silent:
                resultElts = tqdm(resultElts, desc=f"[{print_as}] Parsing results")
            
            parsedItems.extend([self.parseOne(elt,i+1) for elt in resultElts])

            try:
                assert i < maxPages-1
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                dropdown = loadElement(
                    parent=driver,
                    by='CSS_SELECTOR',
                    query="div.pagination div.dropdown",
                    maxWait=1,
                    awaitClickable=True
                )
                dropdown.click()
                dropdown.find_element(By.XPATH,f".//a[text()='{i+2}']").click()
            except Exception as e:
                if self.isDebug():
                    print("ERROR CLICKING 'NEXT' BUTTON")
                break

        return ResultItems(items=parsedItems)