from selenium.common.exceptions import NoSuchElementException
from helper import print_as,progBar
from random import random
from time import sleep
from chrdriver import waitNLoad

folder = "flipkart_grocery"

def parseOneA(resElt):
    l = ["N/A"]

    titleS = "DIDNOTLOAD"
    try:
        titleS = resElt.find_element_by_xpath(".//div[@class='_4rR01T']").text
    except:
        pass
    finally:
        l.append(titleS)

    starS = "DIDNOTLOAD"
    try:
        starDiv = waitNLoad(resElt, 1, 'XPATH', ".//div[@class='_3LWZlK']")
        starS = starDiv.text
    except:
        pass
    finally:
        l.append(starS)

    ratingS = "DIDNOTLOAD"
    try:
        ratingSpan = resElt.find_element_by_xpath(".//span[@class='_2_R_DZ']//span[1]//span[1]")
        ratingS = ratingSpan.text.split(' ')[0]
    except:
        pass
    finally:
        l.append(ratingS)

    priceS = "DIDNOTLOAD"
    try:
        priceDiv = resElt.find_element_by_xpath(".//div[contains(@class,'_30jeq3')]")
        priceS = priceDiv.text[1:]
    except:
        pass
    finally:
        l.append(priceS)

    availS = "YES"
    try:
        # availSpan = resElt.find_element_by_xpath(".//span[@class='_192laR']")
        availSpan = waitNLoad(resElt, 1, 'XPATH', ".//span[@class='_192laR']")
        availS = ("NO" if availSpan else "YES")
    except:
        pass
    finally:
        l.append(availS)

    return l

def parseOneB(resElt):
    l = ["N/A"]

    titleS = "DIDNOTLOAD"
    try:
        # titleA = resElt.find_element_by_xpath(".//a[@class='s1Q9rs']")
        titleA = waitNLoad(resElt, 1, 'XPATH', ".//a[@class='s1Q9rs']")
        titleS = titleA.get_attribute('title')
    except:
        pass
    finally:
        l.append(titleS)

    starS = "DIDNOTLOAD"
    try:
        starDiv = waitNLoad(resElt, 1, 'XPATH', ".//div[@class='_3LWZlK']")
        starS = starDiv.text
    except:
        pass
    finally:
        l.append(starS)

    ratingS = "DIDNOTLOAD"
    try:
        ratingSpan = resElt.find_element_by_xpath(".//span[@class='_2_R_DZ']")
        ratingS = ratingSpan.text[1:-1]
    except:
        pass
    finally:
        l.append(ratingS)

    priceS = "DIDNOTLOAD"
    try:
        priceDiv = resElt.find_element_by_xpath(".//div[contains(@class,'_30jeq3')]")
        priceS = priceDiv.text[1:]
    except:
        pass
    finally:
        l.append(priceS)

    availS = "YES"
    try:
        # availSpan = resElt.find_element_by_xpath(".//span[@class='_192laR']")
        availSpan = waitNLoad(resElt, 1, 'XPATH', ".//span[@class='_192laR']")
        availS = ("NO" if availSpan else "YES")
    except:
        pass
    finally:
        l.append(availS)

    return l

def parseOne(resElt):
    l = []

    sponS = "DIDNOTLOAD"
    try:
        sponDiv = resElt.find_elements_by_xpath("../..//span[text()='Ad']")
        sponS = ("YES" if len(sponDiv)>0 else "NO")
        pass
    except:
        pass
    finally:
        l.append(sponS)

    titleS = "DIDNOTLOAD"
    try:
        titleS = waitNLoad(resElt, 1, 'XPATH', ".//div[@class='_1MbXnE']").text
    except:
        pass
    finally:
        l.append(titleS)

    starS = "N/A"
    l.append(starS)

    ratingS = "N/A"
    l.append(ratingS)

    priceS = "DIDNOTLOAD"
    try:
        priceDiv = resElt.find_element_by_xpath(".//div[contains(@class,'_3aGlZL')]")
        priceS = priceDiv.text[1:]
    except:
        pass
    finally:
        l.append(priceS)

    availS = "YES"
    try:
        # availSpan = resElt.find_element_by_xpath(".//span[@class='_192laR']")
        availSpan = waitNLoad(resElt, 1, 'XPATH', "../..//div[contains(text(),'unavailable')]")
        availS = ("NO" if availSpan else "YES")
    except:
        pass
    finally:
        l.append(availS)

    return l

def writeScr(term,pgno,outStk,driver,writer):
    writer.writerow(["Sponsored", "Title", "Stars (/5)", "Reviewers", "Price", "Available","Result#","Page#"])
    resCnt = 0
    loop = True
    pincode = int(input(f"[{print_as}] Flipkart Grocery requires a valid pincode (only local results will appear): "))
    for i in range(1,pgno+1):
        urli = getURL(term, outStk, i)
        print(f"\n[{print_as}] Scraping page {i}: {urli}")
        driver.get(urli)
        try:
            # children = None
            # parseOne = None
            # try:
            #     resXpath = "//div[contains(@class,'_3pLy-c')]"
            #     children = driver.find_elements_by_xpath(resXpath)
            #     assert len(children)>0
            #     parseOne = parseOneA
            # except:
            #     resXpath = "//div[contains(@class,'_4ddWXP')]"
            #     children = driver.find_elements_by_xpath(resXpath)
            #     parseOne = parseOneB
            try:
                formElt = driver.find_element_by_xpath("//input[@name='pincode']")
                formElt.send_keys(f"{pincode}")
                formElt.submit()
            except:
                pass
            sleep(5)
            children = driver.find_elements_by_xpath("//div[contains(@class,'_2gX9pM')]")
            numRes = len(children)
            print(f"[{print_as}] {numRes} results found")
            if(numRes==0):
                loop = False
                break
            # print(f"[{print_as}] Progress: ",end='')
            currCnt = 0
            for child in children:
                row = parseOne(child)
                resCnt += 1
                currCnt += 1
                row.extend([resCnt,i])
                writer.writerow(row)
                # if resCnt%(numRes//10)==0:
                #     print('|',end='')                
                progBar(currCnt,numRes)
        except Exception as e:
            print(f" (skipped, {e}) ")
            pass
        finally:
            print(" DONE")
            pass
        if not loop:
            break
        if i<pgno:
            randTime = 0.5+random()
            print(f"[{print_as}] Waiting for {randTime} seconds before loading next page...")
            sleep(randTime)

def getURL(term,outStk,page):
    s = f"https://www.flipkart.com/search?q={term}&page={page}&marketplace=GROCERY"
    if(outStk):
        s += "&p%5B%5D=facets.availability%255B%255D%3DInclude%2BOut%2Bof%2BStock"
    return s

flgrtpl = (folder,writeScr)