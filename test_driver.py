from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument('--headless=new')

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options,
)

driver.get('https://www.google.com')
print('Title:', driver.title)
driver.quit()
