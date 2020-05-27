import requests
from bs4 import BeautifulSoup
from match_scrape_methods import get_team_ids, get_team_stats_by_id
import csv
from stash_csv_in_db import stash_in_db


def get_matches(page):
    match_table = page.find("table", {"class": "stats_table"})
    matches = match_table.tbody.find_all('tr')

    return matches


def get_match_urls(match):

    match_url_cell = match.find('td', {'data-stat': 'match_report'})
    match_url_link = match_url_cell.find('a')
    if not match_url_link:
        return
    match_url = match_url_link.get('href')
    return match_url


def get_match_score(match):
    formatted_score = {}
    score = match.find('td', {'data-stat': 'score'}).get_text()
    if score == "":
        return
    split_score = score.split('–')
    formatted_score["home_score"] = split_score[0]
    formatted_score["away_score"] = split_score[1]
    return formatted_score


def get_match_expected_goals(match):
    formatted_expected_goals = {}
    expected_goals_home = match.find('td', {'data-stat': 'xg_a'}).get_text()
    expected_goals_away = match.find('td', {'data-stat': 'xg_b'}).get_text()
    formatted_expected_goals["home_expected_goals"] = expected_goals_home
    formatted_expected_goals["away_expected_goals"] = expected_goals_away
    return formatted_expected_goals


def convert_to_csv(stats):
    print('============ CONVERTING TO CSV ===============')
    print('')
    print('')
    keys = stats[0].keys()
    with open('full_match_stats.csv', 'w') as output:
        dict_writer = csv.DictWriter(output, keys)
        dict_writer.writeheader()
        dict_writer.writerows(stats)



def scrape_that_shit():
    all_match_stats = []
    fixtures_url = 'https://fbref.com/en/comps/20/schedule/Bundesliga-Fixtures'
    page = requests.get(fixtures_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    matches = get_matches(soup)
    print('============== SCRAPING ==================')
    print('')
    print('')
    for index in range(len(matches)):
        if matches[index].has_attr('class'):
            if 'spacer' in matches[index]['class'] or 'thead' in matches[index]['class']:
                continue
        match_stats = {"wk": matches[index].find('th', {'data-stat': 'gameweek'}).get_text()}
        match_score = get_match_score(matches[index])
        if not match_score:
            continue
        match_expected_goals = get_match_expected_goals(matches[index])
        match_stats.update(match_score)
        match_stats.update(match_expected_goals)
        match_url = get_match_urls(matches[index])

        print('scraping match: ', match_url)
        match_report = requests.get('https://fbref.com' + match_url)
        match_report_soup = BeautifulSoup(match_report.content, 'html.parser')
        team_ids = get_team_ids(match_report_soup)

        away_team_stats = get_team_stats_by_id(team_ids["away"], match_report_soup, 'away')
        home_team_stats = get_team_stats_by_id(team_ids["home"], match_report_soup, 'home')

        match_stats.update(away_team_stats)
        match_stats.update(home_team_stats)

        all_match_stats.append(match_stats)
        print('')

    print('============== DONE SCRAPING ==================')
    print('')
    convert_to_csv(all_match_stats)
    stash_in_db(all_match_stats)
    print('=========== DONEZO ==============')


scrape_that_shit()
