from common import *

class AmazonScraper(Scraper):
    @staticmethod
    def parseCategory(category: Optional[str] = None) -> Tuple[str,str]:
        if category == "fresh":
            return "Amazon Fresh","amazon_fresh"
        return "Amazon India","amazon_in"

    def __init__(self,category: Optional[str] = None) -> None:
        self.category: Optional[str] = category
        name,folder = AmazonScraper.parseCategory(category)
        super().__init__(name,folder)

    def getURL(self,term: str, page: str, outOfStock: bool) -> str:
        s = f"https://www.amazon.in/s?k={term}&page={page}"
        if self.category is not None:
            s += f"&i={self.category}"
        if outOfStock:
            s += "&rh=p_n_availability%3A1318485031"
        return s

    def parseOne(self, resultElt: WebElement, pgno: int, flags: Flags = set()) -> ResultItems.SingleItem:
        item = super().parseOne(resultElt,pgno)

        try:
            if "slideshow" in flags:
                title = resultElt.find_element(By.XPATH,".//div[contains(@class,'itemTitle')]").text
            else:
                title = resultElt.find_element(By.TAG_NAME,"h2").text
        except Exception as e:
            if self.isDebug():
                print(e)
            title = None
        finally:
            item.initialize("Title",title)

        try:
            if "slideshow" in flags:
                starSpan = resultElt.find_element(By.XPATH,f".//i[{strictlyContains('class','a-icon-star-mini')}]//span")
                rating = starSpan.text.split(' ')[0]
            else:
                starSpan = resultElt.find_element(By.XPATH,f".//span[{strictlyContains('aria-label','out of 5 stars')}]")
                rating = starSpan.get_attribute("aria-label").split(' ')[0]
        except Exception as e:
            if self.isDebug():
                print(e)
            rating = None
        finally:
            item.initialize("Rating (/5 stars)",rating)

        try:
            if "slideshow" in flags:
                nRatingSpan = resultElt.find_element(By.XPATH,f".//i[{strictlyContains('class','a-icon-star-mini')}]/following-sibling::span")
                nRating = nRatingSpan.text.split(' ')[0]
            else:
                nRatingSpan = resultElt.find_element(By.XPATH,f".//span[{strictlyContains('aria-label','ratings')}]")
                nRating = nRatingSpan.get_attribute("aria-label").split(' ')[0]
        except Exception as e:
            if self.isDebug():
                print(e)
            nRating = None
        finally:
            item.initialize("# of Ratings",nRating)

        try:
            price = None
            if "slideshow" not in flags:
                try:
                    priceSpan = loadElement(
                        parent=resultElt,
                        by='XPATH',
                        query=".//span[@class='a-price']",
                        maxWait=0.5
                    )
                except:
                    priceSpan = loadElement(
                        parent=resultElt,
                        by='XPATH',
                        query=".//div[@data-cy='secondary-offer-recipe']//span[@class='a-color-base']",
                        maxWait=0.5
                    )
                price = priceSpan.text[1:]
        except Exception as e:
            if self.isDebug():
                print(e)
            price = None
        finally:
            item.initialize("Price",price)

        try:
            unavailableSpan = loadElement(
                parent=resultElt, 
                by='XPATH', 
                query=f".//span[{strictlyContains('aria-label','unavailable')}]",
                maxWait=0.5
            )
            available = "NO"
        except Exception as e:
            if self.isDebug():
                print(e)
            available = "YES"
        finally:
            item.initialize("Available",available)
            
        item.initialize("Sponsored","YES" if "ad" in flags else "NO")

        if self.isDebug() and len(flags):
            item.initialize("DEBUG","|".join(flags))

        return item

    def getResultList(self, driver: webdriver.Chrome) -> List[Tuple[WebElement,Flags]]:
        resultList: List[Tuple[WebElement,Flags]] = []

        try:
            resultsElement = loadElement(
                parent=driver,
                by='XPATH',
                query=f"//div[{strictlyContains('class','s-main-slot')}]",
                maxWait=1
            )
        except Exception as e:
            if self.isDebug():
                print("ERROR FINDING RESULTS ELT\n",e)
            return []

        flags: Flags = set()
        simpleCondition = "@data-component-type='s-search-result'"
        adCondition = f"{strictlyContains('class','AdHolder')}"
        try:
            resultList.extend([
                (resultElt,flags.copy()) for resultElt in 
                resultsElement.find_elements(By.XPATH,f".//div[{simpleCondition} and not({adCondition})]")
            ])
        except Exception as e:
            if self.isDebug():
                print("ERROR FINDING SIMPLE RESULTS\n",e)
        
        flags.add("ad")
        try:
            resultList.extend([
                (resultElt,flags.copy()) for resultElt in 
                resultsElement.find_elements(By.XPATH,f".//div[{simpleCondition} and {adCondition}]")
            ])
        except Exception as e:
            if self.isDebug():
                print("ERROR FINDING SIMPLE RESULTS\n",e)
        
        flags.add("slideshow")
        try:
            slideEltPath = f".//div[{strictlyContains('data-cel-widget','slideshow')} or contains(@data-cel-widget,'loom-desktop')]//div[boolean(@data-asin)]"
            resultList.extend([
                (resultElt,flags.copy()) for resultElt in 
                resultsElement.find_elements(By.XPATH,slideEltPath)
            ])
        except Exception as e:
            if self.isDebug():
                print("ERROR FINDING SLIDESHOW ELTS\n",e,flush=True)
        flags.remove("slideshow")

        flags.add("single-video")
        try:
            vidEltsPath = f".//span[@data-component-type='sbv-video-single-product']//div[{strictlyContains('class','puis-sbv-product')}]"
            resultList.extend([
                (vidElt,flags.copy()) for vidElt in 
                resultsElement.find_elements(By.XPATH,vidEltsPath)
            ])
        except Exception as e:
            if self.isDebug():
                print("ERROR FINDING VIDEO ELTS\n",e)
        flags.remove("single-video")

        flags.add("video-product")
        try:
            vidEltsPath = f".//div[{strictlyContains('data-card-metrics-id','sb-video-product')}]//div[{strictlyContains('class','productDetailsContainer')}]"
            resultList.extend([
                (vidElt,flags.copy()) for vidElt in 
                resultsElement.find_elements(By.XPATH,vidEltsPath)
            ])
        except Exception as e:
            if self.isDebug():
                print("ERROR FINDING VIDEO ELTS\n",e)
        flags.remove("video-product")

        flags.add("carousel")
        try:
            caroEltsPath = ".//div[boolean(@data-asin) and descendant::span[@data-action='multi-ad-feedback-form-trigger']]//div[boolean(@data-asin)]"
            resultList.extend([
                (caroElt,flags.copy()) for caroElt in 
                resultsElement.find_elements(By.XPATH,caroEltsPath)
            ])
        except Exception as e:
            if self.isDebug():
                print("ERROR FINDING CAROUSEL ELTS\n",e)
        flags.remove("carousel")

        return resultList