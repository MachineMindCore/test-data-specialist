"""
Prueba Tecnica: Data Specialist
Nombre: Sergio Andres Vargas Mendez
Correo: machine.mind.core@gmail.com
"""


from selenium.common.exceptions import NoSuchDriverException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver

import pandas as pd
import logging
import time

##### Constansts and setup #####
logging.basicConfig(filename='RPA_solana.log', level=logging.INFO)

COINMARKETCAP_URL = 'https://coinmarketcap.com/'


##### Functions #####

def check_cookies():
    """Check if cookies are on the screen"""
    try:
        COOKIES_XPATH = "//*[@id='onetrust-accept-btn-handler']"
        driver.find_element(By.XPATH, COOKIES_XPATH).click()
        time.sleep(1)
    except:
        logging.warning("Cookies didnt show up")


##### PROCESS #####

# Driver and wait setup 
try:
    logging.info('Setting up driver')
    driver = webdriver.Firefox()
    wait = WebDriverWait(driver, timeout=5)
    cookies_wait = WebDriverWait(driver, timeout=5)

except NoSuchDriverException as err:
    context = 'Driver not found'
    raise Exception(f"{context}: {err}")


# Getting base webpage
try:
    logging.info('Getting CoinMarketCap webpage')
    driver.get(COINMARKETCAP_URL)

except WebDriverException as err:
    context = 'CoinMarketCap web could not be reached.'    
    raise Exception(f"{context}: {err}")


# Column panel
try:
    # column button
    COLUMNS_XPATH = "//*[text()='Columns']"
    check_cookies()
    columns_button = wait.until(
        EC.presence_of_element_located((By.XPATH, COLUMNS_XPATH))
    )
    columns_button.click()
    logging.info('Showing columns panel')
    

    # column panel xpaths
    SELECTED_XPATH = "//span[@class='selected']"
    APPLY_XPATH = "//*[contains(text(), 'Apply Changes')]"
    DEL_OPTION_XPATH_TEMPL = "//span[@class='selected' and contains(text(), '{option}')]"
    ADD_OPTION_XPATH_TEMPL = "//span[contains(text(), '{option}')]"

    # wait panel
    wait.until(
        EC.element_to_be_clickable((By.XPATH, APPLY_XPATH))
    )

    # target options
    target_options = {"24h %", "Market Cap", "Volume(24h)", "Circulating Supply", "Dominance %"}
    sorting_mode = "Current Page"    

    # current options
    selected_spans = driver.find_elements(By.XPATH, SELECTED_XPATH)
    current_options = set()
    for span in selected_spans:
        option_label = span.text.strip()
        current_options.add(option_label)
        
    # to select options
    remain_options = current_options ^ target_options
    for option in remain_options:
        template = ADD_OPTION_XPATH_TEMPL if option not in current_options else DEL_OPTION_XPATH_TEMPL
        check_cookies()
        driver.find_element(By.XPATH, template.format(option=option)).click()
        logging.info(f"column option applied: {option}")

    # apply changes
    check_cookies()
    driver.find_element(By.XPATH, APPLY_XPATH).click()
    logging.info("all column options applied")
    
except WebDriverException as err:
    context = "Error in columns panel."
    logging.error(context, err)
    raise Exception(context, err)

# Filter panel
try:
    # filters panel xpaths
    FILTERS_XPATH = "//*[text()='Filters']"
    CHAIN_XPATH = "//*[text()='All Chains']"
    CHAIN_OPT_XPATH = "//*[text()='Solana Ecosystem']"
    APPLY_XPATH = "//*[text()='Apply']"
    
    # filters button
    logging.info('waiting filter panel')
    filters_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, FILTERS_XPATH))
    )
    check_cookies()
    filters_button.click()
    logging.info("showing filters panel")

    # wait panel
    wait.until(
        EC.element_to_be_clickable((By.XPATH, APPLY_XPATH))
    )

    # select options (chain)
    check_cookies()
    driver.find_element(By.XPATH, CHAIN_XPATH).click()
    chain_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, CHAIN_OPT_XPATH))
    )

    check_cookies()
    chain_option.click()
    logging.info("filter selected")
    time.sleep(1) # wait until animation disapear

    # Apply changes
    check_cookies()
    apply = wait.until(
        EC.element_to_be_clickable((By.XPATH, APPLY_XPATH))
    )
    check_cookies()
    apply.click()
    logging.info("all filters option applied")

except WebDriverException as err:
    context = "Error in filters panel"
    logging.error(context)
    raise WebDriverException(context, err)


# Extract table
try:
    # table xpaths
    TABLE_XPATH = "//table[contains(@class, 'cmc-table')]"
    
    # extraction
    logging.info("extracting table")
    
    """
    target_found = False
    while not target_found:
        # Scroll down incrementally
        #driver.execute_script("window.scrollBy(0, 300);")  # Scroll by 300 pixels
        time.sleep(5)  # Pause to allow content to load

        # Check if the target element is now visible
        try:
            WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located((By.XPATH, "//*[text()='Show rows']"))
            )
            print("Target element found!")
            target_found = True  # Set the flag to True to exit the loop
        except:
            pass  # Element not found yet, continue scrolling
    """
            
    #driver.execute_script("window.scrollBy(0, 300);")  # Scroll 300 pixels at a time
    
    #driver.find_element(By.XPATH, "//a[text()='Show rows']/following-sibling::div").click()
    #time.sleep(5)

    table = driver.find_element(By.XPATH, TABLE_XPATH)
    rows = table.find_elements(By.TAG_NAME, "tr")

    # parse table data
    table_data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if not cells:  # Handle header row
            cells = row.find_elements(By.TAG_NAME, "th")
        row_data = [cell.text for cell in cells]
        table_data.append(row_data)
    logging.info("table extracted")

    # Create a DataFrame
    raw_df = pd.DataFrame(table_data)
    raw_df.columns = raw_df.iloc[0]  # set the first row as column names
    df = raw_df[1:]  # drop the header from rows
    df = df.drop(df.columns[[0,1]], axis=1) # drop emoticons and number columns
    df = df.replace("\n", " ", regex=True)
    df.reset_index(drop=True, inplace=True)
    df.to_csv("extraction.csv", index=False)
    logging.info("table exported to csv")

except WebDriverException as err:
    context = "Error in table extraction"
    logging.error(context)
    raise Exception(context, err)

finally:
    logging.info("task done")
    driver.close()