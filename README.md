# Team App Game Schedule Builder

This repo contains tools to scrape [PlayHQ](https://www.playhq.com) fixtures via its [REST API](https://support.playhq.com/hc/en-au/sections/4405422358297-PlayHQ-APIs), and produce CSV files for import as Schedule in a club's [TeamApp](https://www.teamapp.com) account. Using this, one can populate the schedule section for the next round or many rounds of games in minutes and with almost no manual work.

**Note:**  before July 2022, the CSV file was built using the [`cba2csv`](cba2csv) form spreadsheets provided by CBA. Using PlayHQ REST API provides a much easier and robust solution, so this is not used anymore.

The script was originally done to support the [Brunswick Magic Basketball Club](https://www.brunswickmagic.com/) (Melbourne, Australia), from [Coburg Basketball Association (CBA)](https://coburgbasketball.org.au/). However, it any club competing in CBA, or more generally under the [PlayHQ](https://bv.playhq.com/) system (even for other sports), should be able to use it.

## Pre-requisites & Setup

Runs on Python 3.8+ as a Jupyter notebook. 

Packages used (e.g., `pandas`, `json`, `pyshorteners`, `coloredlogs`) can be installed as follows:

```shell
$ pip install -r requirements.txt
```

### Team Names and Access Groups

The system assumes _team names_ match _access groups_ names in the TeamApp account of the club. This is important because the CSV file generated will include such team and access group names.

These names generally be very similar to the ones registered in PlayHQ. For example, PlayHQ may have a team "`Magics U14 Boys Gold`", and the club may just use "`U14 Boys Gold`" for the corresponding team AND access group names. A function `tapp_team_name(team_name)` will translate PlayHQ team names to those names in TeamApp (read below).

### Club Configuration File

The first thing to set-up, once per season, is the club configuration file, which defines a few variables.

Make a copy of the template [`config](config_template.py), and complete it according to the Club's details.

Of particular importance are PlayHQ keys to access the Public API:

- Organization id. (e.g., "`8c4d5431-eaa5-4644-82ac-992abe224b88`")
- `x-api-key`: provided by PlayHQ support.
- `x-tenant`: the id of the sport (e.g., `bv` for Basketball Victoria).

There are also variables to set regarding the season name (as per PlayHQ), and text templates to use to populate descriptions fields in TeamApp.

Finally, function `tapp_team_name(team_name)` needs to be implemented to map PlayHQ team names, to the names used in TeamApp for the teams and access groups (remember they need to match one-to-one!).

This configuration file will be designed at the start of the season and remained fixed.

## How to use it

To run the system, open notebook [playhq_scrape.ipynb](playhq_scrape.ipynb) and change/configure the first section, with the name of the configuration file of the club and the interval dates you want to extract games from.

Then, run the system cell by cell, checking on the way all is consistent.

In the last steps, it will generate a `CSV` file ready to be up imported to TeamApp in the Schedule section.

## PlayHQ REST API

This system uses PlayHQ public REST API:

- [PlayHQ API documentation](https://support.playhq.com/hc/en-au/sections/4405422358297-PlayHQ-APIs).
- [PlayHQ API's technical documentation](https://docs.playhq.com/tech).

As stated above, one needs the organization club's id (public), together with the `x-api-key` (private) and `x-tenant` (the id of the sport, `bv` for Basketball Victoria). In addition, to get the fixtures one would need the season name as it appears in PlayHQ (e.g., "Winter 2022").

First set-up your API key and ORG id in environment variables:

```shell
export API_KEY="........."
export ORG_ID="......."
```

We start by **extracting the active seasons for the club** (using its organisation id):

```shell
$ curl -H "x-phq-tenant: bv" -H "x-api-key: $API_KEY" https://api.playhq.com/v1/organisations/$ORG_ID/seasons

{
    "data": [
        {
            "id": "a94981b4-75b7-429f-9005-915182ab6153",
            "name": "Summer 2022/23",
            "status": "UPCOMING",
            "association": {
                "id": "e18085db-c6de-512f-b78b-53d253c65b32",
                "name": "Coburg Basketball Association",
                "url": "https://www.playhq.com/basketball-victoria/org/coburg-basketball-association/e18085db",
                "logo": {
                    "sizes": [
                        {
                            "url": "https://res.cloudinary.com/playhq/image/upload/h_32,w_32/v1/production/bv/e18085db-c6de-512f-b78b-53d253c65b32/1645069189211/logo.jpg",
                            "dimensions": {
                                "width": 32,
                                "height": 32
                            }
                        },
                        {
                            "url": "https://res.cloudinary.com/playhq/image/upload/h_48,w_48/v1/production/bv/e18085db-c6de-512f-b78b-53d253c65b32/1645069189211/logo.jpg",
                            "dimensions": {
                                "width": 48,
                                "height": 48
                            }
                        },
                        {
                            "url": "https://res.cloudinary.com/playhq/image/upload/h_128,w_128/v1/production/bv/e18085db-c6de-512f-b78b-53d253c65b32/1645069189211/logo.jpg",
                            "dimensions": {
                                "width": 128,
                                "height": 128
                            }
                        },
                        {
                            "url": "https://res.cloudinary.com/playhq/image/upload/h_64,w_64/v1/production/bv/e18085db-c6de-512f-b78b-53d253c65b32/1645069189211/logo.jpg",
                            "dimensions": {
                                "width": 64,
                                "height": 64
                            }
                        },
                        {
                            "url": "https://res.cloudinary.com/playhq/image/upload/h_96,w_96/v1/production/bv/e18085db-c6de-512f-b78b-53d253c65b32/1645069189211/logo.jpg",
                            "dimensions": {
                                "width": 96,
                                "height": 96
                            }
                        },
                        {
                            "url": "https://res.cloudinary.com/playhq/image/upload/h_256,w_256/v1/production/bv/e18085db-c6de-512f-b78b-53d253c65b32/1645069189211/logo.jpg",
                            "dimensions": {
                                "width": 256,
                                "height": 256
                            }
                        }
                    ]
                }
            },
            "competition": {
                "id": "81fe8d81-d087-4a63-b4fb-87bc85e9d8ac",
                "name": "Junior Domestic"
            },
            "createdAt": null,
            "updatedAt": null
        }
    ],
    "metadata": {
        "hasMore": false,
        "nextCursor": null
    }
}
```

Season Summer 22/23 has id `a94981b4-75b7-429f-9005-915182ab6153`. We can then **extract all the teams** registered for that season:

```shell
$ curl -H "x-phq-tenant: bv" -H "x-api-key: $API_KEY" https://api.playhq.com/v1/seasons/a94981b4-75b7-429f-9005-915182ab6153/teams
```

This will yield all the teams in the season. We can extract the club's teams by matching their orgasnisation id. Each team will have an id, for example, team "Magic U10 Boys Gold" has id `bce059fc-67a0-4167-80ee-c2a8fcf4faad`. 

We can then **extract all the team fixture** published so far (this may include past, and future games):

```shell
$ curl -H "x-phq-tenant: bv" -H "x-api-key: $API_KEY" https://api.playhq.com/v1/teams/bce059fc-67a0-4167-80ee-c2a8fcf4faad/fixture

{
    "data": [
        {
            "id": "c8d97a11-a603-43bf-b6c7-ea16157d505f",
            "status": "UPCOMING",
            "url": "https://www.playhq.com/basketball-victoria/org/coburg-basketball-association/junior-domestic-summer-2022-23/saturday-u-10-boys-division-4/game-centre/c8d97a11",
            "createdAt": "2022-10-03T01:00:35.000Z",
            "updatedAt": "2022-10-03T01:00:35.000Z",
            "grade": {
                "id": "196be9f8-d7ff-44d2-8989-7f0a90291a5a",
                "name": "Saturday U10 Boys Division 4",
                "url": "https://www.playhq.com/basketball-victoria/org/coburg-basketball-association/junior-domestic-summer-2022-23/saturday-u-10-boys-division-4/196be9f8"
            },
            "round": {
                "id": "334cb7c9-e49e-4096-aace-4bece285d9a6",
                "name": "Round 1",
                "abbreviatedName": "R1",
                "isFinalRound": false
            },
            "pool": null,
            "schedule": {
                "date": "2022-10-08",
                "time": "09:15:00",
                "timezone": "Australia/Melbourne"
            },
            "competitors": [
                {
                    "id": "bce059fc-67a0-4167-80ee-c2a8fcf4faad",
                    "name": "Magic U10 Boys Gold",
                    "isHomeTeam": false
                },
                {
                    "id": "29a5de69-13fe-41e5-99f7-3d1c65cd1828",
                    "name": "Warriors U10 Boys Gold",
                    "isHomeTeam": true
                }
            ],
            "venue": {
                "id": "84783227-07b3-4e74-906e-f318b26b5ea3",
                "name": "Coburg Basketball Stadium",
                "surfaceName": "Court 3",
                "surfaceAbbreviation": "Crt3",
                "address": {
                    "line1": "25 Outlook Road",
                    "postcode": "3058",
                    "suburb": "Coburg North",
                    "state": "VIC",
                    "country": "Australia",
                    "latitude": -37.73315,
                    "longitude": 144.97684
                }
            }
        }
    ],
    "metadata": {
        "hasMore": true,
        "nextCursor": "MaMx"
    }
}
```

The above JSON reply has been formatted for better legibility.

The last `metadata` information of each JSON reply, states whether there are more follow-up pages using a cursor parameter. To get the next page:

```shell
$ curl -H "x-phq-tenant: bv" -H "x-api-key: $API_KEY" https://api.playhq.com/v1/seasons/a94981b4-75b7-429f-9005-915182ab6153/teams?cursor=MaMx
```

The above interaction is done in Python via function `get_json(self, key)`, which provides an iterator with the various response pages, one by one.

## Other info

To access the games in the PlayHQ admin system use:

```shell
https://bv.playhq.com/org/{$ORG_ID}/games?date=<YY_MM_DD>
```

## Contact

All scripts have been developed by Sebastian Sardina (ssardina@gmail.com).
