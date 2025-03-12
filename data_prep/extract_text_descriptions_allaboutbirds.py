import os
import csv
import requests
from time import sleep
from bs4 import BeautifulSoup

api_key = os.environ['EBIRD_API_KEY']
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/58.0.3029.110 Safari/537.3'}


def read_aba_checklist(file_path):
    """
    Reads in a CSV file containing the ABA Checklist and found at https://www.aba.org/aba-checklist/
    The format is as follows:
    "Ducks, Geese, and Swans (Anatidae)",,,,,
    ,Black-bellied Whistling-Duck,Dendrocygne à ventre noir,Dendrocygna autumnalis,BBWD,1
    ,Fulvous Whistling-Duck,Dendrocygne fauve,Dendrocygna bicolor,FUWD,1
    """
    data_structure = {}
    current_section = None
    total_birds = 0

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)

        for row in reader:
            # Check if the row is a section heading (only first column has a value)
            if row[0] and all(cell == '' for cell in row[1:]):
                current_section = row[0]
                data_structure[current_section] = []
            elif current_section and row[5] == '1':  # Check if column 6 == 1 (index 5)
                # Extract columns 2, 4, and 5 (indices 1, 3, 4)
                # English, Scientific, 4-Letter Code
                data_structure[current_section].append((row[1], row[3], row[4]))
                total_birds += 1

    print(f"Read {total_birds} birds from {len(data_structure)} unique families")
    return data_structure

aba_checklist = read_aba_checklist("C:\\Users\\Roger\\Downloads\\ABA_Checklist-8.17.csv")

failed_birds = []
for family, bird_list in aba_checklist.items():
    for name, scientific, code in bird_list:

        # Get the description of the bird
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

        print(f"Wrote description for {name} (desc len={len(bird_description)}: "
              f"{bird_description[:100]}...) to {description_file}")
        sleep(5)

if len(failed_birds) > 0:
    print(f"Failed to extract descriptions of {len(failed_birds)} birds:")
    for bird in failed_birds:
        print(bird)
