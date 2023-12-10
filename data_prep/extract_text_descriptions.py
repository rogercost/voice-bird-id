import os

import requests
from ebird.api import get_observations

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

# TODO figure out how to get more history, this appears to be no more than a day or a week's worth
print(f"Gathered the following observations from Queens County:")
failed_birds = []
for name, count in observations.items():

    # Get the Wikipedia description of the bird
    wikipedia_name = name[:1] + name[1:].lower()
    wikipedia_name = wikipedia_name.replace(" ", "_")
    wikipedia_response = requests.get('https://en.wikipedia.org/w/api.php', params={
        'action': 'query',
        'format': 'json',
        'titles': wikipedia_name,
        'prop': 'extracts',
        'rvprop': 'content',
        'explaintext': True
    }).json()

    page = next(iter(wikipedia_response['query']['pages'].values()))
    if 'extract' not in page:
        print(f"Warning: Wikipedia description for {name} was not found")
        failed_birds.append(f"{name} => https://en.wikipedia.org/wiki/{wikipedia_name}")
        continue

    bird_description = page['extract']
    if len(bird_description) < 10:
        print(f"Warning: Wikipedia description for {name} was too short: {bird_description}")
        failed_birds.append(f"{name} => https://en.wikipedia.org/wiki/{wikipedia_name}")
        continue

    description_file = f"C:\\Users\\Roger\\bird_descriptions\\{name}.txt"
    with open(description_file, 'w', encoding='utf-8') as f:
        line = f"Name: {name}" + os.linesep + f"Number of observations: {count}" + os.linesep + bird_description
        f.write(line)

    print(f"Wrote description for {name} ({count} obs) (desc len={len(bird_description)}) to {description_file}")

if len(failed_birds) > 0:
    print(f"Failed to extract descriptions of {len(failed_birds)} birds from Wikipedia:")
    for bird in failed_birds:
        print(bird)
