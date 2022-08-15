# Translate Coburg Bball Schedule to TeamApp CSV file

This is the original system, used in 2021, to extract fixtures from  either:

1. a 2007-Office 365 `.xlsx` spreadsheet containing the game schedule from [Coburg Basketball Association](https://coburgbasketball.org.au/); or
2. a CSV report from [PlayHQ](http://playhq.com); and

produce CSV files ready to import into [TeamApp](https://www.teamapp.com) for generating either game events or schedules.

The script was originally done for the [Brunswick Magic Club](https://www.brunswickmagic.com/) but it can extract games for any club.

**Note:** The Excel sheet usually provided contains the schedule for all games in the weekend in the CBA. The sheet is often in the old `.xls` version, so the first thing is to open it with Office or LibreOffice and save it with the new Office 365 `.xlsx` version.

## Pre-requisites

This script requires Python 3.9+ and the following modules:

```shell
$ pip install openpyxl pandas coloredlogs
```

## Naming conventions

The script assumes that the Club TeamAPP is set-up with both Teams and Access Groups *having the same names* based on age group, gender, and colour; for example *"U12 Magic Gold"* or *"U10 Warriors White"*.

The teams and access groups must have been already created in TeamApp or an error will arise when importing the corresponding CSV files produced by this script.
## Example run

To extract all games for club "Magic" for the game "Grading 1" and using the text in file `description.txt` to fill the description box in each event:

```python
$ python cba2csv.py cba_test_fixture-Grading_1.xlsx Magic --id "Grading 1" --description description.txt
```

This will generate two files:

1. One CSV file to import as TeamApp **event**. An event is NOT associated to a particular team, except in that the event will be associated to an TeamAPP Access Group carrying the same name as the team.
2. One CSV file to import as TeamApp **schedule**. A schedule will link each game to an actual team that has the same name as the team. The full CSV file can be imported in TeamApp under `Schedule / All Entries` to populate all games in each team.

The files will start with the date of the games in the schedule, for example, `2021-11-06.Magic_Grading 1_SCHEDULE-cba_test_fixture-Grading_1.csv`

In each game event, the name of the event will be the team name plus the ID provided, e.g., *"U12 Boys Purple - Grading 1"*.

## Description text & venues

The description text will be used to populate the description box of each game event in TeamApp. There is a simple default version in the script, but a text file can be provided via option `--description` as above. 

The text file must mention four place-holders:  `{opponent}`, `{venue}`, `{address}` and `{address_tips}`.

The list of possible venues and their address information is hard-coded inside the script as a dictionary.

## What do I do if script breaks half-way?

The script tries to extract the information of games from the spreadsheet as smartly as possible, but given the nature of the spreadsheet design itself, typos or non-standard entries in the spreadsheet could break the script. For example:

```shell
$ python ../../cba2csv/cba2csv.py R05/Copy\ of\ Saturday\ 5th\ February\ 2022.xlsx Magic --id "Round 5" --description description.txt

2022-01-31 15:47:12 WARNING Extracted year (this is very fragile!): 2022
Traceback (most recent call last):
  File "../../cba2csv/cba2csv.py", line 288, in <module>
    games_cba += extract_cba_games(sheet)
  File "../../cba2csv/cba2csv.py", line 175, in extract_cba_games
    game_dict["league"] = get_team_id(league.value)
  File "../../cba2csv/cba2csv.py", line 58, in get_team_id
    age = re.search("\d+", league.split()[0]).group(0)
AttributeError: 'NoneType' object has no attribute 'group'
```

Here there was an issue extracting the age category from the league string read in the sheet.

What we need to do is find the glitch in the spreadsheet, fix it, and re-run the script. To find the issue in the spreadsheet, we run the command with option `--debug`:

```shell
$ python ../../cba2csv/cba2csv.py R05/Copy\ of\ Saturday\ 5th\ February\ 2022.xlsx Magic --id "Round 5" --description description.txt --debug

.....
.....
2022-01-31 15:58:30 DEBUG Processing game Panthers Green vs St.Fids White in cell <Cell '5th Feb External Venues'.C6>.
2022-01-31 15:58:30 DEBUG 	Game Panthers Green vs St.Fids White in cell <Cell '5th Feb External Venues'.C6> processed successfully.
2022-01-31 15:58:30 DEBUG Processing game Magic Gold vs  Stars PH in cell <Cell '5th Feb External Venues'.D6>.
Traceback (most recent call last):
  File "../../cba2csv/cba2csv.py", line 288, in <module>
    games_cba += extract_cba_games(sheet)
  File "../../cba2csv/cba2csv.py", line 175, in extract_cba_games
    game_dict["league"] = get_team_id(league.value)
  File "../../cba2csv/cba2csv.py", line 58, in get_team_id
    age = re.search("\d+", league.split()[0]).group(0)
AttributeError: 'NoneType' object has no attribute 'group'
```

Before the error we can see the problem was reading cell `D6` in sheet `5th Feb External Venues`. Inspecting that cell manually, we can see it says: "`u/ 12 boys Div2`" which has a dummy space and should read "`u/12 boys Div2`" so that the age category is extracted as `U12`. We open the sheet, fix cell `D6` and re-run the script.

### No gender associated to a game: mixed?

Sometimes a cell will not state the gender type of the game, like `u/16 Div 1/2`. In that case, the script will assume it is a `MIXED` game report it as a warning:

```
2022-01-31 16:22:59 DEBUG Processing game Rebels Red  vs  Magic Gold in cell <Cell '5th Feb External Venues'.H18>.
2022-01-31 16:22:59 WARNING Could not extract gender on text: u/16 Div 1/2 - Assuming MIXED
```

If this corresponds to a known (mixed) team in the club, all will be fine. But if this was indeed an error in the sheet and there is no team `U16 Mixed` in the club, then the script will later report that there is a game for a team that is not known:

```
2022-01-31 16:22:59 INFO Teams having BYE (i.e., have not found any game for club team):
	 U16 Girls Gold
2022-01-31 16:22:59 ERROR Found game for NON-EXISTENT CLUB team U16 Mixed Gold: against Rebels Red at 12:40:00 in Oak Park
2022-01-31 16:22:59 ERROR Check if this would correspond to some BYE team above. Fix the sheet and re-run script
```

Here it is clear that the game was not a MIXED one, but it corresponded to the "`U16 Girls Gold`". So, we open the spreadsheet and update the game in `<Cell '5th Feb External Venues'.H18>` (see log above when game was assumed as MIXED) and change text "`u/16 Div 1/2`" to "`u/16 girls Div 1/2`". Then, we re-run the script and in this case there will be no BYE for any team!

## Schedule changes and updates

Very often CBA will send a new updated spreadsheet. We can save it and generate its corresponding CSV file and check for changes for the club team using script `check_diff.sh`:

```shell
$ ../../../cba2csv/check_diff.sh 2022-02-26.Magic_Round\ 8_SCHEDULE-01.Copy\ of\ Copy\ of\ Saturday\ 26th\ February\ 2022\ v1.csv 2022-02-26.Magic_Round\ 8_SCHEDULE-02.Copy\ of\ Copy\ of\ Saturday\ 26th\ February\ 2022\ v1.csv
5a6
> U12 Girls Purple - Round 8,U12 Girls Purple,2022-02-26,2022-02-26,08:30:00,09:10:00,"RSVP is YES by default - if you cannot make it, please let your Team Manager know as soon as possible.
7d7
< U12 Girls Purple - Round 8,U12 Girls Purple,2022-02-26,2022-02-26,09:20:00,10:00:00,"RSVP is YES by default - if you cannot make it, please let your Team Manager know as soon as possible.
```

This tell us that the only game that change its time was U12 Girls Purple, from 9:20am (first schedule file) to 8:30am (second schedule file).

## Contact

For information about this script, contact Sebastian Sardina at ssardina@gmail.com
