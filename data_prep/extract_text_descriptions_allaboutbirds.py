import os
import requests
from time import sleep
from bs4 import BeautifulSoup
from utils import read_aba_checklist

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/58.0.3029.110 Safari/537.3'}

aba_checklist = read_aba_checklist("C:\\Users\\Roger\\Dropbox\\DOCUMENTS\\voice-bird-id\\ABA_Checklist-8.17.csv")

failed_birds = []
for family, bird_list in aba_checklist.items():
    for name, scientific, code in bird_list:

        # Get the description of the bird
        url_name = name.replace(" ", "_").replace("'", "")

        # Known breaks
        if url_name == "American_Herring_Gull_(Herring_Gull)":
            url_name = "American_Herring_Gull"
        elif url_name == "(American)_Barn_Owl":
            url_name = "Barn_Owl"
        elif url_name == "(Northern)_House_Wren":
            url_name = "House_Wren"
        elif url_name == "Common_Redpoll_(Redpoll)":
            url_name = "Common_Redpoll"

        # Temporary: rerun to shim broken birds above. For a full run, remove this.
        else:
            continue

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
        description_file = f"C:\\Users\\Roger\\Dropbox\\DOCUMENTS\\voice-bird-id\\bird_descriptions\\{name}.txt"
        with open(description_file, 'w', encoding='utf-8') as f:
            line = f"Name: {name}" + os.linesep + f"Description:" + os.linesep + bird_description
            f.write(line)

        print(f"Wrote description for {name} (desc len={len(bird_description)}: "
              f"{bird_description[:100]}...) to {description_file}")
        sleep(5)

if len(failed_birds) > 0:
    print(f"Failed to extract descriptions of {len(failed_birds)} birds:")
    for bird in failed_birds:
        print(bird)
