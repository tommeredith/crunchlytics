import requests
from bs4 import BeautifulSoup
from match_scrape_methods import get_team_ids, get_team_stats_by_id
import csv
from stash_csv_in_db import stash_in_db, stash_standings_in_db
import argparse
from selenium import webdriver

def get_league_table(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    league_table = soup.find("table", {"class": "stats_table"})
    teams = league_table.tbody.find_all('tr')
    team_id_dict = {}
    team_table_stats = []
    index = 1
    for team in teams:
        team_link = team.find('td', {'data-stat': 'squad'}).find('a')
        team_id = team_link.get('href').split('/')[3]
        team_name = team_link.get_text()
        team_id_dict[team_id] = team_name
        indiv_team = {"id": index, "team_name": team_name, "team_id": team_id, "wins": team.find('td', {'data-stat': 'wins'}).get_text(),
                      "draws": team.find('td', {'data-stat': 'draws'}).get_text(),
                      "losses": team.find('td', {'data-stat': 'losses'}).get_text(),
                      "goals_for": team.find('td', {'data-stat': 'goals_for'}).get_text(),
                      "goals_against": team.find('td', {'data-stat': 'goals_against'}).get_text(),
                      "xg_for": team.find('td', {'data-stat': 'xg_for'}).get_text(),
                      "xg_against": team.find('td', {'data-stat': 'xg_against'}).get_text(),
                      "xg_diff_per90": team.find('td', {'data-stat': 'xg_diff_per90'}).get_text()}
        index += 1
        team_table_stats.append(indiv_team)

    return team_id_dict, team_table_stats


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
        return {"home_score": "", "away_score": ""}
    split_score = score.split('–')
    formatted_score["home_score"] = split_score[0]
    formatted_score["away_score"] = split_score[1]
    return formatted_score


def get_match_expected_goals(match):
    formatted_expected_goals = {}
    expected_goals_home = match.find('td', {'data-stat': 'xg_a'}).get_text()
    expected_goals_away = match.find('td', {'data-stat': 'xg_b'}).get_text()
    if not expected_goals_away or not expected_goals_home:
        return {"home_expected_goals": "", "away_expected_goals": ""}
    formatted_expected_goals["home_expected_goals"] = expected_goals_home
    formatted_expected_goals["away_expected_goals"] = expected_goals_away
    return formatted_expected_goals


def convert_match_stats_to_csv(stats, league):
    print('============ CONVERTING match stats TO CSV ===============')
    print('')
    print('')
    keys = stats[0].keys()
    with open('full_match_stats_' + league + '.csv', 'w') as output:
        dict_writer = csv.DictWriter(output, keys)
        dict_writer.writeheader()
        dict_writer.writerows(stats)


def convert_league_table_to_csv(table, league):
    print('============ CONVERTING league table TO CSV ===============')
    print('')
    print('')
    keys = table[0].keys()
    with open('league_table_' + league + '.csv', 'w') as output:
        dict_writer = csv.DictWriter(output, keys)
        dict_writer.writeheader()
        dict_writer.writerows(table)


def scrape_matches_like_a_thug(url, league, table_url):
    all_match_stats = []
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    chrome_path = r'/usr/local/bin/chromedriver'
    browser = webdriver.Chrome(chrome_path, options=options)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    matches = get_matches(soup)
    team_id_dict, team_table_stats = get_league_table(table_url)
    print('============== SCRAPING ==================')
    print('')
    print('')
    for index in range(len(matches)):
        if matches[index].has_attr('class'):
            if 'spacer' in matches[index]['class'] or 'thead' in matches[index]['class']:
                continue
        match_stats = {"wk": matches[index].find('th', {'data-stat': 'gameweek'}).get_text()}
        match_score = get_match_score(matches[index])
        match_expected_goals = get_match_expected_goals(matches[index])
        match_stats.update(match_score)
        match_stats.update(match_expected_goals)
        match_url = get_match_urls(matches[index])

        if not match_url:
            empty_stats = {"home_shots": "", "home_shots_on_target": "", "home_touches": "", "home_pass_pct": "",
                           "home_assists": "", "away_shots": "", "away_shots_on_target": "", "away_touches": "",
                           "away_pass_pct": "", "away_assists": ""}
            home_data = matches[index].find('td', {'data-stat': 'squad_a'})
            away_data = matches[index].find('td', {'data-stat': 'squad_b'})
            home_team = {"home_team": home_data.find('a').get_text(), "home_id": home_data.find('a').get('href').split('/')[3]}
            away_team = {"away_team": away_data.find('a').get_text(), "away_id": away_data.find('a').get('href').split('/')[3]}
            empty_stats.update(home_team)
            empty_stats.update(away_team)
            match_stats.update(empty_stats)
            print('no match data for ' + home_data.find('a').get_text() + ' vs ' + away_data.find('a').get_text())
            print('')
        if match_url:
            print('scraping match: ', match_url)
            browser.get('https://fbref.com' + match_url)
            html = browser.page_source
            match_report_soup = BeautifulSoup(html, 'html.parser')
            team_ids = get_team_ids(matches[index])
            away_team_stats = get_team_stats_by_id(team_ids["away"], match_report_soup, 'away')
            home_team_stats = get_team_stats_by_id(team_ids["home"], match_report_soup, 'home')

            home_team_name = {"home_team": team_id_dict[team_ids["home"]]}
            away_team_name = {"away_team": team_id_dict[team_ids["away"]]}

            match_stats.update(away_team_stats)
            match_stats.update(home_team_stats)
            match_stats.update(home_team_name)
            match_stats.update(away_team_name)
            print('')
        all_match_stats.append(match_stats)

    browser.quit()
    print('============== DONE SCRAPING ==================')
    print('')
    convert_league_table_to_csv(team_table_stats, league)
    convert_match_stats_to_csv(all_match_stats, league)
    stash_in_db(all_match_stats, league)
    stash_standings_in_db(team_table_stats, league)
    print('=========== DONEZO ==============')


# initialise parser object to read from command line
parser = argparse.ArgumentParser()

# script arguments
parser.add_argument('-lg', '--league', default='', type=str, help='put that league in, you hot bitch')
parser.add_argument('-s', '--stash', action='store_true', help='just stash in db')
parser.add_argument('-standings', '--standings', action='store_true', help='grab and stash standings')
parser.add_argument('-past', '-p', action='store_true', help='grab and stash past standings and match data')
args = parser.parse_args()

league = args.league
stash = args.stash
standings = args.standings
past = args.past

print(league)
if league == 'bundesliga':
    fixtures_url = 'https://fbref.com/en/comps/20/schedule/Bundesliga-Fixtures'
    table_url = 'https://fbref.com/en/comps/20/Bundesliga-Stats'
if league == 'premier':
    fixtures_url = 'https://fbref.com/en/comps/9/schedule/Premier-League-Fixtures'
    table_url = 'https://fbref.com/en/comps/9/Premier-League-Stats'
if league == 'liga':
    fixtures_url = 'https://fbref.com/en/comps/12/schedule/La-Liga-Fixtures'
    table_url = 'https://fbref.com/en/comps/12/La-Liga-Stats'
if league == 'seriea':
    fixtures_url = 'https://fbref.com/en/comps/11/schedule/Serie-A-Fixtures'
    table_url = 'https://fbref.com/en/comps/11/Serie-A-Stats'

if standings:
    team_id_dict, team_table_stats = get_league_table(table_url)
    convert_league_table_to_csv(team_table_stats, league)
    stash_standings_in_db(team_table_stats, league)
elif stash:
    with open("full_match_stats_" + league + ".csv", "r") as f:
        reader = csv.DictReader(f)
        match_stats_list = list(reader)
        stash_in_db(match_stats_list, league)
    with open("league_table_" + league + ".csv", "r") as f:
        reader = csv.DictReader(f)
        table_list = list(reader)
        stash_standings_in_db(table_list, league)
else:
    scrape_matches_like_a_thug(fixtures_url, league, table_url)
