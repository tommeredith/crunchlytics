from bs4 import BeautifulSoup


def get_team_ids(match):
    home_team = match.find('td', {'data-stat': 'squad_a'})
    away_team = match.find('td', {'data-stat': 'squad_b'})
    team_ids = {'home': home_team.find('a').get('href').split('/')[3], 'away': away_team.find('a').get('href').split('/')[3]}

    return team_ids


def get_team_stats_by_id(team_id, page, prefix):
    team_stats = {prefix + "_id": team_id}
    stats_table = page.find('table', {'id': 'stats_' + team_id + '_summary'})
    stats_table_foot = stats_table.find('tfoot').find('tr')
    if not stats_table_foot:
        return
    shots = stats_table_foot.find('td', {'data-stat': 'shots_total'}).get_text()
    shots_on_target = stats_table_foot.find('td', {'data-stat': 'shots_on_target'}).get_text()
    touches = stats_table_foot.find('td', {'data-stat': 'touches'}).get_text() if stats_table_foot.find('td', {'data-stat': 'touches'}) else ''
    pass_pct = stats_table_foot.find('td', {'data-stat': 'passes_pct'}).get_text() if stats_table_foot.find('td', {'data-stat': 'passes_pct'}) else ''
    assists = stats_table_foot.find('td', {'data-stat': 'assists'}).get_text() if stats_table_foot.find('td', {'data-stat': 'assists'}) else ''

    team_stats[prefix + "_shots"] = shots
    team_stats[prefix + "_shots_on_target"] = shots_on_target
    team_stats[prefix + "_touches"] = touches
    team_stats[prefix + "_pass_pct"] = pass_pct
    team_stats[prefix + "_assists"] = assists

    return team_stats
