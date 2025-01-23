from selenium import webdriver

driver = webdriver.Firefox()
print("building")
driver.get("https://www.google.com/")
print("builded")
driver.quit()