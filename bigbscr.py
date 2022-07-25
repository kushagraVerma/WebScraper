from selenium.common.exceptions import NoSuchElementException
from helper import print_as,progBar
from random import random
from time import sleep
from chrdriver import waitNLoad
import time

folder = "bigbasket"

def parseOne(resElt):
    l = []
    log = []

    prodDiv = None
    try:
        prodDiv = waitNLoad(resElt, 5, 'XPATH', ".//div[@qa='product_name']")
        # resElt.find_element_by_xpath(".//div[contains(@qa,'product')]")
    except Exception as e:
        log.append(str(e))
        pass


    byS = "DIDNOTLOAD"
    try:
        # byDiv = prodDiv.find_element_by_xpath(".//div[contains(@class,'a-spacing-micro')]")
        byS = prodDiv.find_element_by_tag_name("h6").text
    except Exception as e:
        log.append(str(e))
        pass
    finally:
        l.append(byS)
    
    titleS = "DIDNOTLOAD"
    try:
        titleS = prodDiv.find_element_by_tag_name("a").text
    except Exception as e:
        log.append(str(e))
        pass
    finally:
        l.append(titleS)

    # starS = "DIDNOTLOAD"
    # revS = "DIDNOTLOAD"
    # try:
    #     starSpan = resElt.find_element_by_xpath(".//span[contains(@aria-label,'out of 5 stars')]")
    #     rating = starSpan.get_attribute("aria-label").split(' ')[0]
    #     starS = f"{rating}"
    #     byNum = starSpan.find_element_by_xpath(".//following-sibling::span[1]").get_attribute("aria-label")
    #     revS = f"{byNum}"
    # except:
    #     pass
    # finally:
    #     l.append(starS)
    #     l.append(revS)
    l.append("N/A")
    l.append("N/A")

    priceS = "DIDNOTLOAD"
    try:
        # priceSpan = resElt.find_element_by_xpath(".//span[@class='a-price']")
        # priceSpan = WebDriverWait(resElt, 1).until(
        #     EC.presence_of_element_located((By.XPATH, ".//span[@class='a-price']"))
        # )
        priceSpan = waitNLoad(resElt, 1, 'XPATH', ".//span[@class='discnt-price']")
        # print("AAAA", priceSpan.text)
        # newPrice = priceSpan.find_element_by_xpath(".//span[@class='a-offscreen']").text
        # newPriceSpan = WebDriverWait(priceSpan, 1).until(
        #     EC.presence_of_element_located((By.XPATH, ".//span[@class='a-offscreen']"))
        # )
        # newPrice = newPriceSpan.text
        # print("AAAA")
        priceS = priceSpan.find_element_by_xpath(".//span[@class='ng-binding']").text
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
    except Exception as e:
        log.append(str(e))
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
        pass
        # availSpan = waitNLoad(resElt, 0.5, 'XPATH', ".//span[contains(@aria-label,'unavailable')]")
        # availS = ("NO" if availSpan else "YES")
    except Exception as e:
        log.append(str(e))
        pass
    finally:
        l.append(availS)

    return l,log

def writeScr(term,pgno,outStk,driver,writer):
    writer.writerow(["By", "Title", "Stars (/5)", "Reviewers", "Price", "Available","Result#","Page#"])
    resCnt = 0
    loop = True
    urli = getURL(term, outStk, 0)
    driver.get(urli)
    btnpath = "//button[contains(text(),'Show More')]"
    i = 0
    tries = 0
    maxtr = 4
    while i<pgno-1 and tries<maxtr:
        try:
            print(f"[{print_as}] Loading page {i+2}...")
            btn = waitNLoad(driver, 5, 'XPATH', btnpath)
            # driver.execute_script("arguments[0].scrollIntoView();",btn)
            # time.sleep(1)
            # btn.click()
            js = "arguments[0].click(); window.scrollTo(0, document.body.scrollHeight/2);"
            driver.execute_script(js,btn)
            time.sleep(2)
            i+=1
            tries = 0
        except Exception as e:
            tries+=1
            print(f"[{print_as}] Could not load, retrying ({maxtr-tries} attempts left)")
            # print(f"[{print_as}] Could not load, attempting to scroll ({tries}/6)")
            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # driver.execute_script("vm.pagginator.showmorepage();")
    if tries==6:
        return
    if pgno>1:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.8);")
        time.sleep(3)
    # print(f"\n[{print_as}] Scraping page {i}: {urli}")
    log = []
    try:
        reslistPath = "//div[@class='items']"
        element = waitNLoad(driver, 3, 'XPATH', reslistPath)
        time.sleep(4)
        resXpath = ".//div[@qa='product']"
        children = element.find_elements_by_xpath(resXpath)
        numRes = len(children)
        print(f"[{print_as}] {numRes} results found")
        # if(numRes==0):
        #     loop = False
        #     break
        # print(f"[{print_as}] Progress: ",end='')
        currCnt = 0
        for child in children:
            vals = None
            try:
                childpath = ".//div[@class='ng-scope']"
                vals = child.find_element_by_xpath(childpath)
            except Exception as e:
                log.append("NOVAL: "+str(e))
                pass
                # childpath = ".//div[contains(@class,'s-product-image-container')]"
                # imgDiv = child.find_element_by_xpath(childpath)
                # vals = imgDiv.find_element_by_xpath(".//following-sibling::div[1]")
            row,_log = parseOne(vals)
            # log.append(_log)
            log.append(vals.text[:32])
            # row = parseOne(child)
            # row = list(range(6))
            matches = True
            for x in term.split('+'):
                if(row[1].lower().find(x)<0):
                    matches = False
                    break
            currCnt += 1
            if(row[1]=="DIDNOTLOAD" or not matches):
                continue
            resCnt += 1
            row.extend([resCnt,'N/A'])
            writer.writerow(row)
            # if resCnt%(numRes//10)==0:
            #     print('|',end='')
            progBar(currCnt,numRes)

    finally:
        print(" DONE")
        pass
    # if not loop:
    #     break
    # if i<pgno:
    #     randTime = 0.5+random()
    #     print(f"[{print_as}] Waiting for {randTime} seconds before loading next page...")
    #     sleep(randTime)
    print(log)

def getURL(term,outStk,page):
    s = f"https://www.bigbasket.com/ps/?q={term}"
    # if(outStk):
    #     s += "&rh=p_n_availability%3A1318485031"
    return s

bigbtpl = (folder,writeScr)