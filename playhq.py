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
LOGGING_LEVEL = 'INFO'
# LOGGING_LEVEL = 'DEBUG'
LOGGING_FMT = '%(asctime)s %(levelname)s %(message)s'
# Set format and level of debug
coloredlogs.install(level=LOGGING_LEVEL, fmt=LOGGING_FMT)

API_URL=f'https://api.playhq.com/v1'
GAMES_COLS = ['team_name', 'status', 'schedule_timestamp', 'venue_name']

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
    def __init__(self, org_name, org_id, x_api_key, x_tenant, timezone) -> None:
        self.org_name = org_name
        self.org_id = org_id
        self.x_api_key = x_api_key
        self.x_tenant = x_tenant
        self.timezone = timezone

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
        club_teams_df.sort_values('age', ascending=False, inplace=True)
        club_teams_df.reset_index(inplace=True, drop=True)

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
                fixture_df.insert(1, 'team_name', re.search("U.*", team[1]).group(0))
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
