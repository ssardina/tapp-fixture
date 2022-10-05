"""
Configuration file

Modify the constants below for your particular club and season.
"""
import os

__author__ = "Sebastian Sardina"
__copyright__ = "Copyright 2021-2022"
__credits__ = []
__license__ = "Apache-2.0 license"
__email__ = "ssardina@gmail.com"
# __version__ = "1.0.1"
# __status__ = "Production"

#########################################
# CLUB INFORMATION
#########################################
CLUB_NAME = "Brunswick Magic Basketball Club"

X_TENANT="bv"
ORG_ID="8c4d5431-eaa5-4644-82ac-992abe224b88"   # from PlayHQ URL https://bv.playhq.com/org/<ORG_ID>/competitions
TIMEZONE = 'Australia/Melbourne'

# Provide the x-api-key either explicitly or via a file
X_API_KEY = None
if os.path.exists('x_api_key.txt'):
    with open('x_api_key.txt') as f:
        X_API_KEY = f.readlines()[0]


#########################################
# SEASON INFORMATION
#########################################
SEASON = "Summer 2022/23"  # as it appears in PlayHQ
PLAYHQ_CLUB_SEASON="https://bit.ly/bmbc-s22" # short link to PlayHQ team fixtures for the club
DESC_BYE_TAPP = "Sorry, no game for the team in this round."
DESC_TAPP = """RSVP is YES by default - if you cannot make it, please let your Team Manager know as soon as possible.
Opponent: {opponent}
Venue: {venue} ({court})
Address: {address} {address_tips}
Google Maps coord: https://maps.google.com/?q={coord}

- Please ensure you arrive early and ready.
- Remember that shorts should have no pockets, players should not wear bracelets/watch as it is a risk of injury.
- 45 min schedule with 18 min halves.
- Each team needs to provide a scorer. TMs, please consider a roster.
- Players should not bring balls into the venue - game balls provided by Magic in coach's equipment bag.
- Beginners refs will be wearing green shirts. Please support and respect them through a POSITIVE sideline behaviour.

Check the game in PlayHQ: {url_game}
Check the round in PlayHQ: {url_grade}
All clubs in PlayHQ: PLAYHQ_CLUB_SEASON
""".replace("PLAYHQ_CLUB_SEASON", PLAYHQ_CLUB_SEASON)

#########################################
# OTHER
#########################################

# where to save the output files (e.g., fixtures)
OUTPUT_PATH='fixture/'