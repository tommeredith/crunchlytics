
def calculate_odds(percentage, category):
    odds = 0
    if category == 'favorite':
        odds = int(round((percentage / (1 - (percentage / 100))) * -1))
    elif category == 'dog':
        odds = int(round((100 / (percentage / 100)) - 100))
    return odds
