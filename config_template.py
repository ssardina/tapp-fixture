##############################################################
# CONFIGURATION FILE FOR CLUB <YOUR CLUB's NAME>
##############################################################
CLUB_NAME = "Brunswick Magic Basketball Club"
TIMEZONE = "Australia/Melbourne"

SEASON = "Summer 2022/23"
PLAYHQ_SEASON_URL = "https://bit.ly/bmbc-s22"   # generate this once with bit.ly

# where to save the output files (e.g., fixtures)
OUTPUT_PATH = "Brunswick_Magics/2022.02.Summer_22/fixture"

####################
# PLAYHQ INFORMATION
####################
X_TENANT = "bv"
X_API_KEY = "<YOUR API KEY FROM PLAY-HQ>"
ORG_ID = "<CLUB PLAY-HQ ORGANISATION ID>"   # can be obtained from PlayHQ admin link

####################
# TEAMAPP CONFIGURATIONS
####################
DESC_BYE_TAPP = "Sorry, no game for the team in this round."
DESC_TAPP = """RSVP mandatory for the game.

Opponent: {opponent}
Venue: {venue} ({court})
Address: {address} {address_tips}
Google Maps coord: https://maps.google.com/?q={coord}

- Please ensure you arrive early and ready.
- Remember that shorts should have no pockets, players should not wear bracelets/watch as it is a risk of injury.
- No food in the venue and pickup your rubbish.
- Games will have 2x20 min halves.
- Each team needs to provide a scorer. TMs, please consider a roster.
- Players should not bring balls into the venue - game balls provided by Magic in coach's equipment bag.
- Beginners refs will be wearing green shirts. Please support and respect them through a POSITIVE sideline behaviour.

Check the game in PlayHQ: {url_game}
Check the round in PlayHQ: {url_grade}
All clubs in PlayHQ: PLAYHQ_SEASON_URL
""".replace("PLAYHQ_SEASON_URL", PLAYHQ_SEASON_URL)


def tapp_team_name(team_name):
    """
    Map PlayHQ team name to that used in Teams App

    For example Magic U12 Boys Gold --> U12 Boys Gold
    """
    import re

    return re.search("U.*", team_name).group(0)
