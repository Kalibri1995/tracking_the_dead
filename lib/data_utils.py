import os
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup


def create_list_of_deceased(current_date):
    yesterday_date = (datetime.now() - timedelta(days=1))

    # Check if the file for the current date exists, and create it if it doesn't
    if not os.path.exists(f"{current_date.date()}.txt"):
        open(f"{current_date.date()}.txt", "w").close()

    # Delete the file for yesterday's date if it exists
    if os.path.exists(f"{yesterday_date.date()}.txt"):
        os.remove(f"{yesterday_date.date()}.txt")


def get_deceased_persons():
    current_date = datetime.now()
    create_list_of_deceased(current_date)

    # URL of the page listing deceased individuals
    url = os.environ.get("DEATHS_BASE_URL", "https://en.wikipedia.org/wiki/Deaths_in_2023")

    # Send a request to fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    h3_elements = soup.find_all('h3')  # Find all h3 elements

    for h3 in h3_elements:
        if h3.span and h3.span.get('id') == str(current_date.day):  # Check if there's an h3 element with id matching the current day
            next_element = h3.find_next(['ul', 'h3'])  # Find the next ul or h3 element after the current h3

            if next_element.name == 'h3':  # If the next element is an h3
                return []  # Return an empty list
            elif next_element.name == 'ul':
                ul_element = next_element
                if ul_element:
                    li_elements = ul_element.find_all('li')  # Find all li elements inside ul_element
                    if li_elements:
                        # Read information from the file
                        with open(f"{current_date.date()}.txt", "r") as file:
                            processed_names = file.read().splitlines()

                        new_li_elements = []
                        for li_element in li_elements:
                            a_tag = li_element.find('a')
                            name = a_tag.get_text()
                            link = a_tag['href']
                            age = li_element.get_text().split(',')[1].split()[0]

                            if name not in processed_names:
                                new_li_elements.append((name, link, age))
                                processed_names.append(name)

                        # Write processed names to the file
                        with open(f"{current_date.date()}.txt", "a") as file:
                            for name in new_li_elements:
                                file.write(name[0] + "\n")  # Write only the name

                        return new_li_elements


def get_deceased_person_info(link):
    # URL of the page for individual deceased person
    url = f"{os.environ.get('DEATHS_BASE_URL', 'https://en.wikipedia.org/wiki/Deaths_in_2023')}{link}"

    # Send a request to fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    body_content = soup.find('div', class_='mw-parser-output')
    content_text = body_content.find('p', class_=False)
    person_info = content_text.get_text()
    if person_info != 'Other reasons this message may be displayed:\n':
        div_ru = soup.find('a', class_='interlanguage-link-target', hreflang='ru')
        if div_ru:
            # Get the href attribute value of the link
            ru_link = div_ru['href']
            return person_info, ru_link
        else:
            return person_info, url
    else:
        return None
