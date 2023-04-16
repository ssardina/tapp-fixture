__author__ = "Sebastian Sardina"
__copyright__ = "Copyright 2021-2022"
__credits__ = []
__license__ = "Apache-2.0 license"
__email__ = "ssardina@gmail.com"
# __version__ = "1.0.1"
# __status__ = "Production"


import json
# from sqlite3 import Timestamp
import pandas as pd
import re
import urllib   # https://docs.python.org/3/library/urllib.request.html
import datetime

import logging
import coloredlogs

import utils

LOGGING_LEVEL = 'INFO'
# LOGGING_LEVEL = 'DEBUG'
LOGGING_FMT = '%(asctime)s %(levelname)s %(message)s'
# Set format and level of debug
coloredlogs.install(level=LOGGING_LEVEL, fmt=LOGGING_FMT)

API_URL=f'https://api.playhq.com/v1'
GAMES_COLS = ['team_name', 'status', 'schedule_timestamp', 'venue_name']

########################################################################
# TEAMS APP TRANSLATIONS
########################################################################
TAPP_COLS_CSV = ['event_name', 'team_name', 'start_date', 'end_date', 'start_time', 'end_time', 'description', 'venue', 'location', 'access_groups', 'rsvp', 'comments', 'attendance_tracking', 'duty_roster', 'ticketing']

DESC_BYE_TAPP_DEFAULT = "Sorry, no game for the team in this round."
DESC_TAPP_DEFAULT = """
Opponent: {opponent}
Venue: {venue} {court}
Address: {address} {address_tips}
Google Maps coord: https://maps.google.com/?q={coord}
Waze coord: https://www.waze.com/live-map/directions?to=ll.{coord[0]}%2C{coord[1]}
Check the game in PlayHQ: {url_game}
Check the round in PlayHQ: {url_grade}
"""

###########################################################
# PLAY-HQ MAIN CLASS
###########################################################

class ResponsePHQ:
    def __init__(self, key, x_api_key, x_tenant):
        self.url = f"{API_URL}/{key}"
        self.has_more = True
        self.cursor = None
        self.key = key
        self.x_api_key = x_api_key
        self.x_tenant = x_tenant

    def __iter__(self):
        while self.has_more:
            url_req = self.url
            if self.cursor is not None:
                params = urllib.parse.urlencode({ "cursor": self.cursor})
                url_req = url_req + f"?{params}"

            req = urllib.request.Request(url_req)
            req.add_header('x-api-key', self.x_api_key)
            req.add_header('x-phq-tenant', self.x_tenant)

            content = urllib.request.urlopen(req).read()
            data_json = json.loads(content)

            self.has_more = data_json['metadata']['hasMore']
            if self.has_more:
                self.cursor = data_json['metadata']['nextCursor']

            yield data_json

class PlayHQ(object):
    def __init__(self, org_name, org_id, x_api_key, x_tenant, timezone, tapp_team_name, tapp_game_name) -> None:
        self.org_name = org_name
        self.org_id = org_id
        self.x_api_key = x_api_key
        self.x_tenant = x_tenant
        self.timezone = timezone
        self.tapp_team_name = tapp_team_name
        self.tapp_game_name = tapp_game_name

    def get_json(self, key, cursor=None):
        return iter(ResponsePHQ(key, self.x_api_key, self.x_tenant))

    def get_season_id(self, season: str):
        # get competition id
        season_id = None
        competition_id = None
        for data_json in self.get_json(f"organisations/{self.org_id}/seasons"):
            # print(json.dumps(data_json, sort_keys=True, indent=4))

            for x in data_json['data']:
                if x['name'] == season:
                    season_id = x['id']
                    # competition_id = x['competition']['id']
                    logging.debug(f'Seasons *{season}* found with id: {season_id}')
                    return season_id

    def get_season_teams(self, season_id):
        teams_dfs = []
        for data_json in self.get_json(f"seasons/{season_id}/teams"):
            # print(data_json)
            # print(json.dumps(data_json, sort_keys=True, indent=4))
            teams_dfs.append(pd.json_normalize(data_json['data']))

        # put all teams together for the season and extract club's teams
        teams_df = pd.concat(teams_dfs)
        club_teams_df = teams_df.loc[teams_df['club.id'] == self.org_id]

        columns = ['id', 'name', 'grade.id', 'grade.name', 'grade.url']
        club_teams_df = club_teams_df[columns]
        club_teams_df.dropna(inplace=True)
        club_teams_df['age'] = club_teams_df['name'].apply(lambda x: re.search("U(\d*)", x).group(1) )
        # club_teams_df = club_teams_df.sort_values('age', ascending=False)
        # club_teams_df.reset_index(inplace=True, drop=True)

        return club_teams_df

    def get_team_fixture(self, team_id) -> pd.DataFrame:
        """Extract a df that encodes the whole fixture of a team from the JSON data.
        Note: Games can only be obtained per team in the public API.
        It is not possible to list all games of organisation

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
        # https://docs.playhq.com/tech#tag/Teams/paths/~1v1~1teams~1:id~1fixture/get
        fixture_dfs = []
        for data_json in self.get_json(f"teams/{team_id}/fixture"):
            fixture_dfs.append(pd.json_normalize(data_json['data']))
        fixture_df = pd.concat(fixture_dfs)

        # Drop games that have no date (some games are not yet scheduled fully)
        #   maybe we can check using the id and GET games: https://docs.playhq.com/tech#tag/Games/paths/~1partner~1v1~1games~1:id~1summary/get
        ids_empty_date = fixture_df[fixture_df['schedule.date'] == '']['id'].to_list()
        if ids_empty_date:
            logging.warning(f"Games with ids {ids_empty_date} have no date. They will be dropped")
            fixture_df = fixture_df[fixture_df['schedule.date'] != '']

        # replace full stops in column names for _ (full stops are problematic in .query())
        fixture_df.columns = fixture_df.columns.str.replace('.', '_', regex=False)

        fixture_df['createdAt'] = pd.to_datetime(fixture_df['createdAt']).dt.tz_convert(self.timezone)
        fixture_df['updatedAt'] = pd.to_datetime(fixture_df['updatedAt']).dt.tz_convert(self.timezone)

        # add column with full game timestamp from date + time + timezone
        fixture_df.loc[fixture_df['schedule_time'] == "", 'schedule_time'] = "00:00:00" # handle empty times
        fixture_df.loc[fixture_df['schedule_timezone'] == "", 'schedule_timezone'] = self.timezone
        fixture_df['schedule_timestamp'] = fixture_df.apply(lambda x: pd.to_datetime(f"{x['schedule_date']} {x['schedule_time']}").tz_localize(x['schedule_timezone']).tz_convert(self.timezone), axis=1)


        return fixture_df


    def get_games(self, teams_df: pd.DataFrame, from_date : pd.Timestamp, to_date : pd.Timestamp=None, status=None) -> pd.DataFrame:
        """ Build df with all teams's games with status (default is UPCOMING games) and within interval dates

        Args:
            teams_df (pd.DataFrame): teams to extract games
            from_date (pd.Timestamp): games from this date (inclusive)
            to_date (pd.Timestamp): games until this date (inclusive)
            status: (String): the status of games to scrape (default "UPCOMING")

        Returns:
            pd.DataFrame: a df with games of all the teams within the dates and with status (if any)
        """
        if to_date is None: # assume 1 day interval
            to_date = from_date + pd.Timedelta(days=1)

        club_upcoming_games = []
        for team in teams_df[['id', 'name']].to_records(index=False):
            logging.debug(f"Extracting games for team: {team}")

            fixture_df = self.get_team_fixture(team[0])

            # filter wrt date interval
            fixture_df = fixture_df.query('schedule_timestamp >= @from_date and schedule_timestamp <= @to_date')

            if status is not None:  # need to filter by status
                # fixture_df = fixture_df.loc[fixture_df['status'] == status]
                fixture_df = fixture_df.query('status in @status')
            if fixture_df.empty:
                logging.info(f"No games for team: {team[1]}")
            else:
                logging.info(f"Games extracted for team: {team[1]}")
                # fixture_df.insert(1, 'team_name', self.tapp_team_name(team[1])) # translate the team name
                fixture_df.insert(1, 'team_name', team[1])
                fixture_df.insert(2, 'team_id', team[0])
                club_upcoming_games.append(fixture_df)

        club_games_df = None
        if club_upcoming_games: # list is not empty
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

    def to_teamsapp_schedule(self, games_df : pd.DataFrame, desc_template=DESC_TAPP_DEFAULT, game_duration=45) -> pd.DataFrame:
        """Translates a game fixture table from PlayHQ data to the format used in TeamApp for CSV Schedule import

        Args:
            games_df (pd.DataFrame): a table of games as per PlayHQ
            desc_template (str, optional): Text to use in the TeamApp description field of each game
            game_duration (int, optional): minutes per game to allocate

        Returns:
            pd.DataFrame: a dataframe representing CSV file for import into TeamApp Schedule
        """
        def extract_opponent(team_id, competitors):
            if competitors[0]['id'] != team_id:
                return competitors[0]['name']
            else:
                return competitors[1]['name']

        games_tapps_df = games_df.loc[:, ['team_name', 'team_id', 'round_name', 'round_abbreviatedName']]

        games_tapps_df['team_name'] = games_tapps_df.apply(lambda x: self.tapp_team_name(x['team_name']), axis=1) # translate the team name
        games_tapps_df['opponent'] = games_df.apply(lambda x: extract_opponent(x['team_id'], x['competitors']), axis=1)

        # Set the name of the game event, e.g., "Game 12.1 Round 1"
        # games_tapps_df['event_name'] = games_tapps_df['team_name'] + " - " + games_tapps_df['round_name']
        games_tapps_df['event_name'] = games_tapps_df.apply(lambda x: self.tapp_game_name(x['team_name'], x['opponent'], x['round_name']), axis=1)

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
        games_tapps_df['lat'] = games_df['venue_address_latitude']
        games_tapps_df['lon'] = games_df['venue_address_longitude']
        games_tapps_df['game_url'] = games_df.apply(lambda x : utils.shorten_url(x['url']), axis=1)
        games_tapps_df['grade_url'] = games_df.apply(lambda x : utils.shorten_url(x['grade_url']), axis=1)

        games_tapps_df['description'] = games_tapps_df.apply(lambda x: desc_template.format(
                    opponent=x['opponent'],
                    venue=x['venue'],
                    court=x['court'],
                    address=x['location'],
                    address_tips='',
                    lat=x['lat'],
                    lon = x['lon'],
                    url_game=x['game_url'],
                    url_grade=x['grade_url']), axis=1
        )

        # return the dataframe with just the columns that TeamApp uses for CSV import
        games_tapps_df = games_tapps_df.loc[:, TAPP_COLS_CSV + ['opponent', 'court']]
        return games_tapps_df

    def build_teamsapp_bye_schedule(self, teams: list, date: datetime, desc_bye=DESC_BYE_TAPP_DEFAULT) -> pd.DataFrame:
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


