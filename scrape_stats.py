import requests
from bs4 import BeautifulSoup

def generate_urls(base_url, num_pages):
    urls = []
    for page_num in range(1, num_pages + 1):
        urls.append(f"{base_url}?page={page_num}")
    return urls

def scrape_teams_info(urls, output_file):
    teams_info = []

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        team_group = soup.find('div', class_='table-group')

        if team_group:
            team_elements = team_group.find_all('div', class_='table-row')
            for team_element in team_elements:
                team_info = {}

                team_name_element = team_element.find('div', class_='table-cell team')
                if team_name_element:
                    team_name_span = team_name_element.find('span', class_='team-name')
                    if team_name_span:
                        team_name = team_name_span.text.strip()
                        team_info['name'] = team_name

                points_element = team_element.find('div', class_='table-cell points').find('p')
                if points_element:
                    points = points_element.text.strip()
                    team_info['points'] = points

                if team_info:
                    teams_info.append(team_info)

    # Запись результатов в файл
    with open(output_file, 'a', encoding='utf-8') as file:
        for team_info in teams_info:
            file.write(f"Информация о команде: {team_info}\n")

base_url = 'https://bo3.gg/ru/teams/valve-rankings/world'
num_pages = 7
output_file = 'teams_info.txt'

urls = generate_urls(base_url, num_pages)
scrape_teams_info(urls, output_file)