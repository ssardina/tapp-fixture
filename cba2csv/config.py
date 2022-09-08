# Winter 2022
CLUB_TEAMS = {"U8 Mixed Purple", "U10 Girls Purple", "U10 Boys Purple", "U10 Boys Gold", "U12 Boys Gold", "U12 Boys Purple", "U12 Girls Gold", "U14 Girls Black", "U14 Boys Gold", "U14 Boys Purple", "U14 Girls Gold", "U14 Girls Purple", "U16 Boys Gold", "U16 Boys Purple", "U16 Girls Gold", "U12 Boys Diamond", "U14 Boys Black", "U10 Girls Gold", "U12 Boys Black", "U12 Girls Black"}

# Summer 2021-2022
# CLUB_TEAMS = {"U8 Mixed Purple", "U10 Girls Purple", "U10 Boys Purple", "U10 Boys Gold", "U12 Boys Gold", "U12 Boys Purple", "U12 Girls Gold", "U12 Girls Purple", "U14 Boys Gold", "U14 Boys Purple", "U14 Girls Gold", "U14 Girls Purple", "U16 Boys Gold", "U16 Boys Purple", "U16 Girls Gold"}


# DESCRIPTION constant must have the following placeholders:
#   {opponent}, {venue}, {address}, {address_tips}
DESCRIPTION = """RSVP is YES by default - if you cannot make it, please let your Team Manager know as soon as possible.

Opponent: {opponent}
Venue: {venue} {court}
Address: {address}{address_tips}

$3 venue entry fee/person (charge for card payment)."""

DESCRIPTION_BYE = "Sorry, no game for the team in this round."

# Dictionary of tuples
# <venue string> : (name of venue, address, tip to address)
VENUES_INFO = {
    "Coburg Basketball Stadium": ("Coburg Basketball Stadium", "25 Outlook Road, Coburg North", None),
    "Dallas":  ("Dallas Brooks", "26-36 King Street, Dallas", None),
    "Dallas Brooks Community Primary School" : "Dallas", # as PLAYHQ
    "Coburg HS": ("Coburg Senior High School", "101 Urquhart Street, Coburg", "Access is via 101 Urquhart St, behind East Coburg Tennis Club."),
    "Coburg Senior High" : "Coburg HS",
    "PVGC": ("Pascoe Vale Girls College", "Lake Avenue, Pascoe Vale", "Access is via Cornwall Rd, Pascoe Vale. Car park is near school crossing. The College Gym is to the right off car park."),
    "PVG": "PVGC",
    "Pascoe Vale Girls College" : "PVGC",
    "Johns": ("St. John's Greek Orthodox College", "21 Railway Place, West Preston", "Entrance to gym & car park (Blanch St, Preston) is via Bell Street."),
    "St John's College (Preston)" : "Johns",
    "Oak Park": ("Oak Park Stadium", "9 Hillcrest Road, Oak Park", None),
    "Oak Park Stadium" : "Oak Park",    # as PLAYHQ
    "Northcote High" : ("Northcote High School", "19–25 St Georges Road, Northcote", None),
    "Northcote High School" : "Northcote High",
    "Mercy" : ("Mercy College", "760 Sydney Road, Coburg", None),
    "Mercy College" : "Mercy"
}

GAME_LENGTH_MIN = 40



TAPP_CSV_HEADER_SCHEDULE = ["event_name",  "team_name", "start_date", "end_date", "start_time", "end_time", "description",
                           "location", "access_groups", "rsvp", "comments", "attendance_tracking", "duty_roster", "ticketing", "reference_id"]


