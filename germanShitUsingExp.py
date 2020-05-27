import pandas as pd
import numpy as np
import argparse


def run_predictions(season, table, game_week):
    sims_to_run = 100000
    df = pd.DataFrame(columns=["week", "homeTeam", "awayTeam", "homeWins", "awayWins", "draws", "homeScore", "awayScore"])
    # only use games before the game_week we want to predict
    historical = season.loc[season["Wk"] < game_week]
    # make sure we only use games that have valid scores
    historical = historical.loc[season["HomeScore"] > -1]

    # get average home and away scores for entire competition
    home_avg = historical["xHomeGoals"].mean()
    away_avg = historical["xAwayGoals"].mean()

    # games to predict
    to_predict = season.loc[season["Wk"] == game_week]
    # loop through predicting games
    another_i = 1

    for i in to_predict.index:

        home_team = to_predict.loc[i, "Home"]
        away_team = to_predict.loc[i, "Away"]

        # average goals scored and goals conceded for home team
        home_team_exp_goals_for = historical.loc[season["Home"] == home_team, "xHomeGoals"].mean()
        home_team_exp_goals_against = historical.loc[season["Home"] == home_team, "xAwayGoals"].mean()

        # average goals scored and goals conceded for away team
        away_team_exp_goals_for = historical.loc[season["Away"] == away_team, "xAwayGoals"].mean()
        away_team_exp_goals_against = historical.loc[season["Away"] == away_team, "xHomeGoals"].mean()

        home_team_expected_to_actual_for = table.loc[table["Squad"] == home_team, "GF"].sum() / table.loc[table["Squad"] == home_team, "xG"].sum()
        home_team_expected_to_actual_against = table.loc[table["Squad"] == home_team, "GA"].sum() / table.loc[table["Squad"] == home_team, "xGA"].sum()

        away_team_expected_to_actual_for = table.loc[table["Squad"] == away_team, "GF"].sum() / table.loc[table["Squad"] == away_team, "xG"].sum()
        away_team_expected_to_actual_against = table.loc[table["Squad"] == away_team, "GA"].sum() / table.loc[table["Squad"] == away_team, "xGA"].sum()

        # calculate home and away offense and defense strength
        home_team_offense_strength = (home_team_exp_goals_for * home_team_expected_to_actual_for) / home_avg
        home_team_defense_strength = (home_team_exp_goals_against * home_team_expected_to_actual_against) / away_avg

        away_team_offense_strength = (away_team_exp_goals_for * away_team_expected_to_actual_for) / away_avg
        away_team_defense_strength = (away_team_exp_goals_against * away_team_expected_to_actual_against) / home_avg

        home_team_expected_goals = home_team_offense_strength * away_team_defense_strength * home_avg
        away_team_expected_goals = away_team_offense_strength * home_team_defense_strength * away_avg

        home_team_poisson = np.random.poisson(home_team_expected_goals, sims_to_run)
        away_team_poisson = np.random.poisson(away_team_expected_goals, sims_to_run)

        home_wins = np.sum(home_team_poisson > away_team_poisson) / sims_to_run * 100
        away_wins = np.sum(away_team_poisson > home_team_poisson) / sims_to_run * 100
        draws = np.sum(home_team_poisson == away_team_poisson) / sims_to_run * 100

        home_score_actual = to_predict.loc[i, "HomeScore"]
        away_score_actual = to_predict.loc[i, "AwayScore"]

        df.loc[another_i] = {
            "week": game_week,
            "homeTeam": home_team,
            "awayTeam": away_team,
            "homeWins": home_wins,
            "awayWins": away_wins,
            "draws": draws,
            "homeScore": home_score_actual,
            "awayScore": away_score_actual
        }
        another_i = another_i + 1

    return df


def run_tests(season, table, game_week):
    print('running accuracy check')
    best_score = 0
    best_threshold = 0
    games_used = 0
    for threshold in range(45, 95, 5):
        correct = 0
        total_games = 0
        possible_games = 0
        games_wrong = 0
        games_totally_wrong = 0
        for wk in range(game_week):
            if wk >= 3:
                predictions = run_predictions(season, table, wk)

                for i in predictions.index:
                    home_score = predictions.loc[i, "homeScore"]
                    away_score = predictions.loc[i, "awayScore"]
                    home_win = predictions.loc[i, "homeWins"]
                    away_win = predictions.loc[i, "awayWins"]
                    draws = predictions.loc[i, "draws"]

                    if home_score == away_score and draws > home_win and draws > away_win and draws >= threshold:
                        correct += 1
                    if home_score > away_score and home_win > draws and home_win > away_win and home_win > threshold:
                        correct += 1
                    if away_score > home_score and away_win > draws and away_win > home_win and away_win > threshold:
                        correct += 1
                    if draws > threshold or away_win > threshold or home_win > threshold:
                        total_games += 1
                    if home_score > away_score and away_win > draws and away_win > home_win and away_win > threshold:
                        games_totally_wrong += 1
                    if away_score > home_score and home_win > draws and home_win > away_win and home_win > threshold:
                        games_totally_wrong += 1

                    if away_win > home_win and away_win > draws and (home_score > away_score or home_score == away_score) and away_win > threshold:
                        games_wrong += 1

                    if home_win > away_win and home_win > draws and (away_score > home_score or away_score == home_score) and home_win > threshold:
                        games_wrong += 1

                    if draws > home_win and draws > away_win and (away_score > home_score or home_score > away_score) and draws > threshold:
                        games_wrong += 1

                    possible_games += 1

        if total_games > 0:
            score = correct / total_games * 100
        else:
            score = 0
        print('----------')
        print('threshold: ', threshold)
        print('score: ', score)
        print('games used: ', total_games)
        print('games wrong: ', games_wrong)
        print('games totally wrong', games_totally_wrong)
        print('----------')

        if (score > best_score or (
                score == best_score and total_games > games_used)) and total_games >= possible_games / 10:
            best_score = score
            best_threshold = threshold
            games_used = total_games
    print('')
    print('')
    print('!!!!!!=====================!!!!!!!!!!!')
    print('best threshold: ', best_threshold)
    print('score: ', best_score)
    print('games used: ', games_used)
    print('!!!!!!=====================!!!!!!!!!!!')


def print_predictions(predictions_data):
    for i in predictions_data.index:
        print('=============================')
        print('home team: ', predictions_data.loc[i, "homeTeam"])
        print('away team: ', predictions_data.loc[i, "awayTeam"])
        print('home wins: ', predictions_data.loc[i, "homeWins"])
        print('away wins: ', predictions_data.loc[i, "awayWins"])
        print('draws: ', predictions_data.loc[i, "draws"])
        print('=============================')


# initialise parser object to read from command line
parser = argparse.ArgumentParser()

# script arguments
parser.add_argument('-wk', '--week', default=100, type=int, help='put that week in, you hot bitch')
parser.add_argument('-r', '--run', action='store_true', help='run that shit')
parser.add_argument('-t', '--test', action='store_true', help='run tests to check accuracy')

args = parser.parse_args()

week = args.week
run = args.run

season_csv = pd.read_csv('csv_stats/matches.csv')

table_csv = pd.read_csv('csv_stats/table.csv')

if args.run and args.week:
    predictions = run_predictions(season_csv, table_csv, week)
    print_predictions(predictions)
elif args.test and args.week:
    run_tests(season_csv, table_csv, week)
else:
    print('need to add -r to that shit and add a week')
