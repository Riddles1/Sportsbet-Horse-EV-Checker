#this code is for the racing promos where you get a bonus bet if your horse runs second or third
import requests
from bs4 import BeautifulSoup
import pandas as pd
BONUS_BET_EV = 0.75
# The URL of the webpage (replace with the actual URL)
url = 'https://www.sportsbet.com.au/horse-racing/australia-nz/randwick/race-3-8265965'

# Fetch the webpage content
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all containers for each horse and their odds
    horse_containers = soup.find_all('div', class_='outcomeDetailsContainer_f13tqi60')
    
    # Initialize a list to store horse names and their odds
    horse_data = []

    for container in horse_containers:
        # Extract the horse name
        horse_name_element = container.find('div', class_='outcomeName_f18x6kvm')
        horse_name = horse_name_element.get_text(strip=True) if horse_name_element else 'Unknown'

        # Extract the odds
        odds_elements = container.find_all('span', class_='size14_f7opyze bold_f1au7gae priceTextSize_frw9zm9')
        odds = []
        for element in odds_elements:
            try:
                odds.append(float(element.get_text(strip=True)))
            except ValueError:
                # Skip non-numeric values (e.g., 'EW')
                pass

        # Ensure we have exactly two odds (win and place) before appending
        if len(odds) == 2:
            horse_data.append([horse_name, odds[0], odds[1]])
    
    race_total_edge = -1
    horse_count = len(horse_data)
    for horse in horse_data:
        race_total_edge += (1/horse[1])
    
    horse_calculations = {"Horse Number": [], "Horse Name":[], "win_odds": [], "place_odds": [], "real_win_prob": [], "second_or_third_real_prob": [], "horse_EV": []}
    for horse in horse_data:
        horse_number = int(horse[0][-3:].replace(")", "").replace("(", ""))
        horse_name = horse[0].split(". ")[1].split("(")[0]
        horse_calculations["Horse Number"].append(horse_number)
        horse_calculations["Horse Name"].append(horse_name)

        horse_calculations["win_odds"].append(horse[1])
        horse_calculations["place_odds"].append(horse[2])

        real_win_prob = 1/(horse[1]*(1+race_total_edge))
        real_place_prob = 1/(horse[2]*(1+race_total_edge))
        real_2nd_or_3rd_prob = real_place_prob - real_win_prob
        horse_calculations["real_win_prob"].append(real_win_prob)
        horse_calculations["second_or_third_real_prob"].append(real_2nd_or_3rd_prob)
        horse_calculations["horse_EV"].append(real_win_prob*horse[1] + real_2nd_or_3rd_prob*BONUS_BET_EV)
    df = pd.DataFrame(horse_calculations)
    sorted_df = df.sort_values(by='horse_EV', ascending=False)
    top_EV_horse = sorted_df.iloc[0]
    print(sorted_df)
    print("\n\n*************************************\nHighest EV Horse:\n")
    print(f"Horse Number: {top_EV_horse['Horse Number']}")
    print(f"Horse Name: {top_EV_horse['Horse Name']}")
    print(f"Win Odds: {top_EV_horse['win_odds']}")
    print(f"Place Odds: {top_EV_horse['place_odds']}")
    print(f"EV: {top_EV_horse['horse_EV']}")
    print("\n*************************************")

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
