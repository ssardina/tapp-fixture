__author__ = "Sebastian Sardina"
__copyright__ = "Copyright 2021-2022"
__credits__ = []
__license__ = "Apache-2.0 license"
__email__ = "ssardina@gmail.com"
# __version__ = "1.0.1"
# __status__ = "Production"

import pyshorteners # https://pyshorteners.readthedocs.io/en/latest/
import json
import datetime
import calendar
import pandas as pd


###########################################################
# TOOLS
###########################################################
def next_day(cal_day=calendar.SATURDAY):
    today = datetime.date.today() #reference point.
    day = today + datetime.timedelta((cal_day-today.weekday()) % 7 )
    return day

def pretty_date(date : datetime.datetime):
    return date.strftime("%A %B %d, %Y (%Y/%m/%d)")

def compact_date(date : datetime.datetime):
    return date.strftime('%Y_%m_%d')


def print_json_pretty(data_json):
    print(json.dumps(data_json, sort_keys=True, indent=4))



# TinyURL shortener service
def shorten_url(url):
    s = pyshorteners.Shortener()
    try:
        return s.tinyurl.short(url)
    except:
        return s.dagd.short(url)


###########################################################
# TEAM APP TOOLS
###########################################################
DESC_TAPP_DEFAULT = """
Opponent: {opponent}
Venue: {venue} {court}
Address: {address} {address_tips}
Google Maps coord: https://maps.google.com/?q={coord}
Check the game in PlayHQ: {url_game}
Check the round in PlayHQ: {url_grade}
"""
DESC_BYE_TAPP_DEFAULT = "Sorry, no game for the team in this round."


TAPP_COLS_CSV = ['event_name', 'team_name', 'start_date', 'end_date', 'start_time', 'end_time', 'description', 'venue', 'location', 'access_groups', 'rsvp', 'comments', 'attendance_tracking', 'duty_roster', 'ticketing']

def to_teamsapp_schedule(games_df : pd.DataFrame, desc_template=DESC_TAPP_DEFAULT, game_duration=45):
    """Translates a game fixture table from PlayHQ data to the format used in TeamApp for CSV Schedule import

    Args:
        games_df (pd.DataFrame): a table of games
        desc_template (str, optional): Text to use in the TeamApp description field of each game

    Returns:
        pd.DataFrame: a dataframe representing CSV file for import into TeamApp Schedule
    """
    # fields used by TeamApp
    TAPP_COLS_CSV = ['event_name', 'team_name', 'start_date', 'end_date', 'start_time', 'end_time', 'description', 'venue', 'location', 'access_groups', 'rsvp', 'comments', 'attendance_tracking', 'duty_roster', 'ticketing'] + ['opponent', 'court']

    def extract_opponent(team_id, competitors):
        if competitors[0]['id'] != team_id:
            return competitors[0]['name']
        else:
            return competitors[1]['name']

    games_tapps_df = games_df.loc[:, ['team_name', 'team_id', 'round_name', 'round_abbreviatedName']]
    games_tapps_df['event_name'] = games_tapps_df['team_name'] + " - " + games_tapps_df['round_name']
    games_tapps_df['opponent'] = games_df.apply(lambda x: extract_opponent(x['team_id'], x['competitors']), axis=1)

    games_tapps_df['schedule_timestamp'] = games_df['schedule_timestamp']
    games_tapps_df['start_date'] = games_df['schedule_timestamp'].dt.date
    games_tapps_df['end_date'] = games_tapps_df['start_date']
    # # team_apps_df['start_time'] = pd.to_datetime(club_upcoming_games_df['schedule.time'], format="%H:%M:%S").dt.time
    games_tapps_df['start_time'] = games_df['schedule_timestamp'].dt.time
    games_tapps_df['end_time'] = (games_df['schedule_timestamp'] + datetime.timedelta(minutes=game_duration)).dt.time

    games_tapps_df['location'] = games_df['venue_address_line1'] + ", " +  games_df['venue_address_suburb']
    # team_apps_df['location'] = club_upcoming_games_df[['venue.address.line1', 'venue.address.suburb']].agg(','.join, axis=1)
    games_tapps_df['access_groups'] = games_tapps_df['team_name']
    games_tapps_df['rsvp'] = 1
    games_tapps_df['comments'] = 1
    games_tapps_df['attendance_tracking'] = 0
    games_tapps_df['duty_roster'] = 1
    games_tapps_df['ticketing'] = 0
    games_tapps_df['reference_id'] = ""


    games_tapps_df['venue'] = games_df['venue_name']
    games_tapps_df['court'] = games_df['venue_surfaceName']
    games_tapps_df['geo'] = "(" + games_df['venue_address_latitude'].astype(str) + "," + games_df['venue_address_longitude'].astype(str) + ")"
    games_tapps_df['game_url'] = games_df.apply(lambda x : shorten_url(x['url']), axis=1)
    games_tapps_df['grade_url'] = games_df.apply(lambda x : shorten_url(x['grade_url']), axis=1)

    games_tapps_df['description'] = games_tapps_df.apply(lambda x: desc_template.format(
                opponent=x['opponent'],
                venue=x['venue'],
                court=x['court'],
                address=x['location'],
                address_tips='',
                coord=x['geo'],
                url_game=x['game_url'],
                url_grade=x['grade_url']), axis=1
    )

    # return the dataframe with just the columns that TeamApp uses for CSV import
    games_tapps_df = games_tapps_df.loc[:, TAPP_COLS_CSV]
    return games_tapps_df


def build_teamsapp_bye_schedule(teams: list, date: datetime, desc_bye=DESC_BYE_TAPP_DEFAULT):

    if teams is None or len(teams) == 0:  # there are BYE games
        return None

    bye_teams_df = pd.DataFrame(teams, columns =['team_name'])
    # bye_teams_df['team_name'] = bye_teams_df.apply(lambda x: re.search("U.*", x['name']).group(0), axis=1)

    bye_teams_df['access_groups'] = bye_teams_df['team_name']
    bye_teams_df['event_name'] = bye_teams_df['team_name'] + " - BYE"
    bye_teams_df['start_date'] = date
    bye_teams_df['end_date'] = date
    bye_teams_df['start_time'] = datetime.time(hour=0,minute=0,second=0)
    bye_teams_df['end_time'] = datetime.time(hour=0,minute=0,second=0)
    bye_teams_df['description'] = desc_bye
    bye_teams_df['location'] = ""
    bye_teams_df['venue'] = "BYE"

    bye_teams_df['rsvp'] = 0
    bye_teams_df['comments'] = 0
    bye_teams_df['attendance_tracking'] = 0
    bye_teams_df['duty_roster'] = 0
    bye_teams_df['ticketing'] = 0
    bye_teams_df['reference_id'] = ""

    bye_teams_df = bye_teams_df[TAPP_COLS_CSV]

    return bye_teams_df


