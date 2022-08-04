import json
from sqlite3 import Timestamp
import pandas as pd
import re
from urllib.request import urlopen
import urllib
import pyshorteners # https://pyshorteners.readthedocs.io/en/latest/
import datetime

import logging
import coloredlogs
# LOGGING_LEVEL = 'INFO'
LOGGING_LEVEL = 'DEBUG'
LOGGING_FMT = '%(asctime)s %(levelname)s %(message)s'
# Set format and level of debug
coloredlogs.install(level=LOGGING_LEVEL, fmt=LOGGING_FMT)


API_URL=f'https://api.playhq.com/v1'

GAMES_COLS = ['team_name', 'status', 'schedule_timestamp', 'venue_name']

###########################################################
# PLAY-HQ MAIN CLASS
###########################################################
class PlayHQ(object):
    def __init__(self, org_name, org_id, x_api_key, x_tenant, timezone) -> None:
        self.org_name = org_name
        self.org_id = org_id
        self.x_api_key = x_api_key
        self.x_tenant = x_tenant
        self.timezone = timezone


    def get_json(self, key):
        FULL_URL=f"{API_URL}/{key}"
        req = urllib.request.Request(FULL_URL)
        req.add_header('x-api-key', self.x_api_key)
        req.add_header('x-phq-tenant', self.x_tenant)

        content = urlopen(req).read()
        data_json = json.loads(content)

        return data_json


    def get_season_id(self, season: str):
        data_json = self.get_json(f"organisations/{self.org_id}/seasons")
        # print(data_json)
        # print(json.dumps(data_json, sort_keys=True, indent=4))

        # get competition id
        season_id = None
        competition_id = None
        for x in data_json['data']:
            if x['name'] == season:
                season_id = x['id']
                competition_id = x['competition']['id']

        logging.debug(f'Seasons id for season *{season}*: {season_id}')
        logging.debug(f'Competition id for season *{season}*: {competition_id}')

        return season_id

    def get_season_teams(self, season_id):
        data_json = self.get_json(f"seasons/{season_id}/teams")
        # print(data_json)
        # print(json.dumps(data_json, sort_keys=True, indent=4))

        teams_df = pd.json_normalize(data_json['data'])
        club_teams_df = teams_df.loc[teams_df['club.id'] == self.org_id]

        columns = ['id', 'name', 'grade.id', 'grade.name', 'grade.url']
        club_teams_df = club_teams_df[columns]
        club_teams_df.dropna(inplace=True)
        club_teams_df['age'] = club_teams_df['name'].apply(lambda x: re.search("U(\d*)", x).group(1) )
        club_teams_df.sort_values('age', ascending=False, inplace=True)
        club_teams_df.reset_index(inplace=True, drop=True)

        return club_teams_df

    def get_team_fixture_df(self, team_id) -> pd.DataFrame:
        """Extract a df that encodes the whole fixture of a team from the JSON data

        The original dataframe converted from the json data has these columns:

            Index(['id', 'status', 'url', 'createdAt', 'updatedAt', 'pool', 'competitors',
        'grade.id', 'grade.name', 'grade.url', 'round.id', 'round.name',
        'round.abbreviatedName', 'round.isFinalRound', 'schedule.date',
        'schedule.time', 'schedule.timezone', 'venue.id', 'venue.name',
        'venue.surfaceName', 'venue.surfaceAbbreviation', 'venue.address.line1',
        'venue.address.postcode', 'venue.address.suburb', 'venue.address.state',
        'venue.address.country', 'venue.address.latitude',
        'venue.address.longitude'],
        dtype='object')

        The returned df has in addition:

            1. createdAt and updatedAt as Timestamp with self.timezone
            2. new field schedule.timezone combining schedule.date and schedule.time and self.timezone
            3. replace full stops in column names for _ (full stops are problematic in .query())

        Args:
            team_id (str): the PlayHQ id of the team to scrape all its games

        Returns:
            pd.DataFrame: a dataframe representing the fixture of the team
        """
        data_json = self.get_json(f"teams/{team_id}/fixture") # https://docs.playhq.com/tech#tag/Teams/paths/~1v1~1teams~1:id~1fixture/get
        fixture_df = pd.json_normalize(data_json['data'])

        # replace full stops in column names for _ (full stops are problematic in .query())
        fixture_df.columns = fixture_df.columns.str.replace('.', '_', regex=False)


        fixture_df['createdAt'] = pd.to_datetime(fixture_df['createdAt']).dt.tz_convert(self.timezone)
        fixture_df['updatedAt'] = pd.to_datetime(fixture_df['updatedAt']).dt.tz_convert(self.timezone)

        # add column with full game timestamp from date + time + timezone
        fixture_df.loc[fixture_df['schedule_time'] == "", 'schedule_time'] = "00:00:00" # handle empty times
        fixture_df.loc[fixture_df['schedule_timezone'] == "", 'schedule_timezone'] = self.timezone
        fixture_df['schedule_timestamp'] = fixture_df.apply(lambda x: pd.to_datetime(f"{x['schedule_date']} {x['schedule_time']}").tz_localize(x['schedule_timezone']).tz_convert(self.timezone), axis=1)


        return fixture_df


    def get_games(self, teams_df: pd.DataFrame, from_date : Timestamp, to_date : Timestamp=None, status=None) -> pd.DataFrame:
        """ Build df with all teams's games with status (default is upcoming games)

        Args:
            teams_df (pd.DataFrame): teams to extract games

        Returns:
            pd.DataFrame: a df with games of all the teams within the dates and with status (if any)
        """
        if to_date is None: # assume 1 day interval
            to_date = from_date + pd.Timedelta(days=1)

        club_upcoming_games = []
        for team in teams_df[['id', 'name']].to_records(index=False):
            logging.debug(f"Extracting games for team: {team}")

            fixture_df = self.get_team_fixture_df(team[0])

            # filter wrt date interval
            fixture_df = fixture_df.query('schedule_timestamp >= @from_date and schedule_timestamp <= @to_date')

            if status is not None:  # need to filter by status
                # fixture_df = fixture_df.loc[fixture_df['status'] == status]
                fixture_df = fixture_df.query('status in @status')
            if fixture_df.empty:
                logging.info(f"No games for team: {team[1]}")
            else:
                logging.info(f"Games extracted for team: {team[1]}")
                fixture_df.insert(1, 'team_name', re.search("U.*", team[1]).group(0))
                fixture_df.insert(2, 'team_id', team[0])
                club_upcoming_games.append(fixture_df)
        club_games_df = pd.concat(club_upcoming_games)
        club_games_df.reset_index(drop=True, inplace=True)

        # club_upcoming_games_df.columns
        # (['id', 'status', 'url', 'createdAt', 'updatedAt', 'pool', 'competitors',
        #        'grade.id', 'grade.name', 'grade.url', 'round.id', 'round.name',
        #        'round.abbreviatedName', 'round.isFinalRound', 'schedule.date',
        #        'schedule.time', 'schedule.timezone', 'venue.id', 'venue.name',
        #        'venue.surfaceName', 'venue.surfaceAbbreviation', 'venue.address.line1',
        #        'venue.address.postcode', 'venue.address.suburb', 'venue.address.state',
        #        'venue.address.country', 'venue.address.latitude',
        #        'venue.address.longitude', 'venue'],
        #       dtype='object')

        return club_games_df






###########################################################
# TOOLS
###########################################################
DESC_TAPP_DEFAULT = """
Opponent: {opponent}
Venue: {venue} {court}
Address: {address} {address_tips}
Google Maps coord: https://maps.google.com/?q={coord}
Check the game in PlayHQ: {url_game}
Check the round in PlayHQ: {url_grade}
"""
GAME_DUR=45

def print_json_pretty(data_json):
    print(json.dumps(data_json, sort_keys=True, indent=4))


# TinyURL shortener service
def shorten_url(url):
    s = pyshorteners.Shortener()
    try:
        return s.tinyurl.short(url)
    except:
        return s.dagd.short(url)



def to_teamsapp_schedule(games_df, desc_template=DESC_TAPP_DEFAULT):
    def extract_opponent(team_id, competitors):
        if competitors[0]['id'] != team_id:
            return competitors[0]['name']
        else:
            return competitors[1]['name']

    games_tapps_df = games_df.loc[:, ['team_name', 'team_id', 'round.name', 'round.abbreviatedName']]
    games_tapps_df['event_name'] = games_tapps_df['team_name'] + " - " + games_tapps_df['round.name']
    games_tapps_df['opponent'] = games_df.apply(lambda x: extract_opponent(x['team_id'], x['competitors']), axis=1)
    games_tapps_df['start_date'] = pd.to_datetime(games_df['schedule.date'])
    games_tapps_df['end_date'] = pd.to_datetime(games_df['schedule.date'])
    # team_apps_df['start_time'] = pd.to_datetime(club_upcoming_games_df['schedule.time'], format="%H:%M:%S").dt.time
    games_tapps_df['start_time'] = pd.to_datetime(games_df['schedule.time']).dt.time
    games_tapps_df['end_time'] = (pd.to_datetime(games_df['schedule.time']) + datetime.timedelta(minutes=GAME_DUR)).dt.time
    games_tapps_df['location'] = games_df['venue.address.line1'] + ", " +  games_df['venue.address.suburb']
    # team_apps_df['location'] = club_upcoming_games_df[['venue.address.line1', 'venue.address.suburb']].agg(','.join, axis=1)
    games_tapps_df['access_groups'] = games_tapps_df['team_name']
    games_tapps_df['rsvp'] = 1
    games_tapps_df['comments'] = 1
    games_tapps_df['attendance_tracking'] = 0
    games_tapps_df['duty_roster'] = 1
    games_tapps_df['ticketing'] = 0
    games_tapps_df['reference_id'] = ""


    games_tapps_df['venue'] = games_df['venue.name']
    games_tapps_df['court'] = games_df['venue.surfaceName']
    games_tapps_df['geo'] = "(" + games_df['venue.address.latitude'].astype(str) + "," + games_df['venue.address.longitude'].astype(str) + ")"
    games_tapps_df['game_url'] = games_df.apply(lambda x : shorten_url(x['url']), axis=1)
    games_tapps_df['grade_url'] = games_df.apply(lambda x : shorten_url(x['grade.url']), axis=1)

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

    return games_tapps_df

import calendar
def next_day(cal_day=calendar.SATURDAY):
    today = datetime.date.today() #reference point. 
    day = today + datetime.timedelta((cal_day-today.weekday()) % 7 )
    return day

