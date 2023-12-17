import os

import requests
from ebird.api import get_observations
from time import sleep
from bs4 import BeautifulSoup

api_key = os.environ['EBIRD_API_KEY']

# Get all observations from Queens County
observations = {}
records = get_observations(api_key, 'US-NY-081')
for record in records:
    common_name = record['comName']
    if common_name not in observations:
        observations[common_name] = 1
    else:
        observations[common_name] = observations[common_name] + 1

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# TODO figure out how to get more history, this appears to be no more than a day or a week's worth
print(f"Gathered {len(observations)} observations from Queens County:")
failed_birds = []
for name, count in observations.items():

    # Get the Wikipedia description of the bird
    url_name = name.replace(" ", "_").replace("'", "")
    url = f'https://www.allaboutbirds.org/guide/{url_name}/id'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        failed_birds.append(f"{name} => {url}")
        print(f"Error: Response from {url} was {response}")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    description_texts = []
    for description_div in soup.find_all('div', class_='annotation-txt'):
        p_element = description_div.find('p')
        if p_element is not None:
            description_texts.append(description_div.find('p').text)

    if len(description_texts) == 0:
        failed_birds.append(f"{name} => {url}")
        print(f"Warning: Description not found in HTML from {url}")
        continue

    bird_description = " ".join(description_texts)
    description_file = f"C:\\Users\\Roger\\bird_descriptions\\{name}.txt"
    with open(description_file, 'w', encoding='utf-8') as f:
        line = f"Name: {name}" + os.linesep + f"Description:" + os.linesep + bird_description
        f.write(line)

    print(f"Wrote description for {name} ({count} obs) (desc len={len(bird_description)}: "
          f"{bird_description[:100]}...) to {description_file}")
    sleep(5)

if len(failed_birds) > 0:
    print(f"Failed to extract descriptions of {len(failed_birds)} birds:")
    for bird in failed_birds:
        print(bird)
