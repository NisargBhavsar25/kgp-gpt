import os
from bs4 import BeautifulSoup
import requests

def scraper(url, year):
    for month in range(1, 13):
        if month in [1, 3, 5, 7, 8, 10, 12]:
            n_days = 31
        elif month in [4, 6, 9, 11]:
            n_days = 30
        else:
            n_days = 28

        for day in range(1, n_days + 1):
            month_str, day_str = str(month).zfill(2), str(day).zfill(2)
            date = f'{month_str}/{day_str}/{year}'
            archive_url = f'{url}/archive/{year}/{month_str}/{day_str}'

            page = requests.get(archive_url)
            soup = BeautifulSoup(page.text, 'html.parser')

            stories = soup.find_all('div', class_='streamItem streamItem--postPreview js-streamItem')
            for idx, story in enumerate(stories, 1):
                story_url = story.find('a', class_='button button--smaller button--chromeless u-baseColor--buttonNormal')['href']
                story_page = requests.get(story_url)
                story_soup = BeautifulSoup(story_page.text, 'html.parser')

                paragraphs = story_soup.find_all('p')
                story_content = "\n".join([p.get_text() for p in paragraphs])

                # Write content to a text file
                filename = f"article_{date.replace('/', '-')}_{idx}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(story_content)

                print(f'Article {idx} scraped on {date}.')

    print("All articles scraped.")

scraper("https://example.com", 2023)
