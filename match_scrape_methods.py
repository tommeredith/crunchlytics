from bs4 import BeautifulSoup


def get_team_ids(page):
    teams = page.find_all('div', {'itemprop': 'performer'})
    team_ids = {}
    for index in range(len(teams)):
        team_link = teams[index].find('a', {'itemprop': 'name'})
        if index == 1:
            team_ids["home"] = team_link.get('href').split('/')[3]
        else:
            team_ids["away"] = team_link.get('href').split('/')[3]

    return team_ids


def get_team_stats_by_id(team_id, page, prefix):
    team_stats = {prefix + "_id": team_id}
    stats_table = page.find('table', {'id': 'stats_' + team_id + '_summary'})
    stats_table_foot = stats_table.find('tfoot').find('tr')
    shots = stats_table_foot.find('td', {'data-stat': 'shots_total'}).get_text()
    shots_on_target = stats_table_foot.find('td', {'data-stat': 'shots_on_target'}).get_text()
    touches = stats_table_foot.find('td', {'data-stat': 'touches'}).get_text() if stats_table_foot.find('td', {'data-stat': 'touches'}) else ''
    pass_pct = stats_table_foot.find('td', {'data-stat': 'passes_pct'}).get_text() if stats_table_foot.find('td', {'data-stat': 'passes_pct'}) else ''
    assists = stats_table_foot.find('td', {'data-stat': 'assists'}).get_text() or ''

    team_stats[prefix + "_shots"] = shots
    team_stats[prefix + "_shots_on_target"] = shots_on_target
    team_stats[prefix + "_touches"] = touches
    team_stats[prefix + "_pass_pct"] = pass_pct
    team_stats[prefix + "_assists"] = assists

    return team_stats
