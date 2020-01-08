from selenium import webdriver
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pandas as pd

link = 'https://play.google.com/store/apps/details?id=com.miso&hl=ko&showAllReviews=true'
driver = webdriver.Chrome('/usr/local/bin/chromedriver')
driver.get(link)

scroll_cnt = 10

for i in range(scroll_cnt):
  driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
  time.sleep(3)
  try:
    load_more = driver.find_element_by_xpath('//*[contains(@class,"U26fgb O0WRkf oG5Srb C0oVfc n9lfJ")]').click()
  except:
    print('Cannot find load more button...')

reviews = driver.find_elements_by_xpath('//*[@jsname="fk8dgd"]//div[@class="d15Mdf bAhLNe"]')
print('There are %d reviews avaliable!' % len(reviews))
print('Writing the data...')

df = pd.DataFrame(columns=['name', 'ratings', 'date', 'helpful', 'comment', 'developer_comment'])

for review in reviews:
  soup = BeautifulSoup(review.get_attribute('innerHTML'), 'html.parser')

  name = soup.find(class_='X43Kjb').text
  ratings = int(soup.find('div', role='img').get('aria-label').replace('별표 5개 만점에', '').replace('개를 받았습니다.', '').strip())

  date = soup.find(class_='p2TkOb').text
  date = datetime.strptime(date, '%Y년 %m월 %d일')
  date = date.strftime('%Y-%m-%d')

  helpful = soup.find(class_='jUL89d y92BAb').text
  if not helpful:
    helpful = 0
  
  comment = soup.find('span', jsname='fbQN7e').text
  if not comment:
    comment = soup.find('span', jsname='bN97Pc').text
  
  developer_comment = None
  dc_div = soup.find('div', class_='LVQB0b')
  if dc_div:
    developer_comment = dc_div.text.replace('\n', ' ')
  
  df = df.append({
    'name': name,
    'ratings': ratings,
    'date': date,
    'helpful': helpful,
    'comment': comment,
    'developer_comment': developer_comment
  }, ignore_index=True)

filename = datetime.now().strftime('result/%Y-%m-%d_%H-%M-%S.csv')
df.to_csv(filename, encoding='utf-8-sig', index=False)
driver.stop_client()
driver.close()

print('Done!')
