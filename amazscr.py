from selenium.common.exceptions import NoSuchElementException
from consts import print_as
from random import random
from time import sleep
from chrdriver import waitNLoad

folder = "amazon_in"

def parseOne(resElt):
    l = []

    sponS = "DIDNOTLOAD"
    try:
        sponDiv = resElt.find_elements_by_xpath(".//div[contains(@class,'a-spacing-micro')]")
        sponS = ("YES" if len(sponDiv)>0 else "NO")
    except:
        pass
    finally:
        l.append(sponS)
    
    titleS = "DIDNOTLOAD"
    try:
        titleS = resElt.find_element_by_tag_name("h2").text
    except:
        pass
    finally:
        l.append(titleS)

    starS = "DIDNOTLOAD"
    revS = "DIDNOTLOAD"
    try:
        starSpan = resElt.find_element_by_xpath(".//span[contains(@aria-label,'out of 5 stars')]")
        rating = starSpan.get_attribute("aria-label").split(' ')[0]
        starS = f"{rating}"
        byNum = starSpan.find_element_by_xpath(".//following-sibling::span[1]").get_attribute("aria-label")
        revS = f"{byNum}"
    except:
        pass
    finally:
        l.append(starS)
        l.append(revS)

    priceS = "DIDNOTLOAD"
    try:
        # priceSpan = resElt.find_element_by_xpath(".//span[@class='a-price']")
        # priceSpan = WebDriverWait(resElt, 1).until(
        #     EC.presence_of_element_located((By.XPATH, ".//span[@class='a-price']"))
        # )
        priceSpan = waitNLoad(resElt, 1, 'XPATH', ".//span[@class='a-price']")
        # print("AAAA", priceSpan.text)
        # newPrice = priceSpan.find_element_by_xpath(".//span[@class='a-offscreen']").text
        # newPriceSpan = WebDriverWait(priceSpan, 1).until(
        #     EC.presence_of_element_located((By.XPATH, ".//span[@class='a-offscreen']"))
        # )
        # newPrice = newPriceSpan.text
        # print("AAAA")
        priceS = f"{priceSpan.text[1:]}"
        # try:
        #     # oldPriceSpan = priceSpan.find_elements_by_xpath(".//following-sibling::span[1]")
        #     oldPriceSpan = WebDriverWait(priceSpan, 1).until(
        #         EC.presence_of_element_located((By.XPATH, ".//following-sibling::span[2]"))
        #     )
        #     print("AAAA",oldPriceSpan.text)
        #     oldPrice = (oldPriceSpan[0].find_element_by_xpath(".//[@class='a-offscreen']").text if len(oldPriceSpan)>0 else "-")
        #     s += f"Old price: {oldPrice},"
        # except:
        #     print(3.5)
    except:
        pass
    finally:
        l.append(priceS)
    
    # try:
    #     dealSpan = WebDriverWait(resElt, 1).until(
    #         EC.presence_of_element_located((By.XPATH, ".//span[@class='a-truncate-full a-offscreen']"))
    #     )
    #     # dealSpan = resElt.find_elements_by_xpath(".//span[@class='a-truncate-full a-offscreen']")
    #     print("AAAA",dealSpan.text)
    #     deal = (dealSpan.text if dealSpan else "-")
    #     if deal=="":
    #         deal = "--"
    #     s += f"Deals: {deal},"
    # except:
    #     pass

    availS = "YES"
    try:
        availSpan = waitNLoad(resElt, 0.5, 'XPATH', ".//span[contains(@aria-label,'unavailable')]")
        availS = ("NO" if availSpan else "YES")
    except:
        pass
    finally:
        l.append(availS)

    return l

def writeScr(term,pgno,driver,writer):
    writer.writerow(["Sponsored", "Title", "Stars (/5)", "Reviewers", "Price", "Available","Result#","Page#"])
    resCnt = 0
    for i in range(1,pgno+1):
        urli = getURL(term, i)
        print(f"\n[{print_as}] Scraping page: {urli}")

        driver.get(urli)
        try:
            reslistPath = "//div[contains(@class,'s-main-slot')]"
            element = waitNLoad(driver, 1, 'XPATH', reslistPath)
            resXpath = ".//div[@data-component-type='s-search-result']"
            children = element.find_elements_by_xpath(resXpath)
            numRes = len(children)
            print(f"[{print_as}] {numRes} results found")
            print(f"[{print_as}] Progress: ",end='')
            for child in children:
                vals = None
                try:
                    childpath = ".//div[contains(@class,'s-list-col-right')]"
                    vals = child.find_element_by_xpath(childpath)
                except NoSuchElementException:
                    childpath = ".//div[contains(@class,'s-product-image-container')]"
                    imgDiv = child.find_element_by_xpath(childpath)
                    vals = imgDiv.find_element_by_xpath(".//following-sibling::div[1]")
                row = parseOne(vals)
                resCnt += 1
                row.extend([resCnt,i])
                writer.writerow(row)
                if resCnt%(numRes//10)==0:
                    print('|',end='')

        finally:
            print(" DONE")
            pass
        
        if i<pgno:
            randTime = 0.5+random()
            print(f"[{print_as}] Waiting for {randTime} seconds before loading next page...")
            sleep(randTime)

def getURL(term,page):
    return f"https://www.amazon.in/s?k={term}&page={page}&rh=p_n_availability%3A1318485031"

amaztpl = (folder,writeScr)