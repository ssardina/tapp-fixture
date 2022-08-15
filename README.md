# Team App Scheduler Builder

This repo contains tools to build a fixture schedule CSV file ready to be imported into [TeamApp](https://www.teamapp.com) system for a club. Many sport clubs use [TeamApp](https://www.teamapp.com) to run the club's teams, which include distributing the game fixtures for each round.

Entering each game into [TeamApp](https://www.teamapp.com) could become a very demanding and error-prone task as soon as the club has a few teams. This system will allow you to populate the schedule section for the next round of games in minutes and with almost no manual work. Hopefully! :-)

The script was originally done to support the [Brunswick Magic Basketball Club](https://www.brunswickmagic.com/) (Melbourne, Australia), from [Coburg Basketball Association (CBA)](https://coburgbasketball.org.au/). However, it any club competing in CBA, or more generally under the [PlayHQ](https://bv.playhq.com/) system (even for other sports), should be able to use it.

As of July 2022, the system was simplified and moved to Python-based Jupyter notebook that exctacts upcoming games from [PlayHQ](https://bv.playhq.com/)'s Public [API](https://support.playhq.com/hc/en-au/sections/4405422358297-PlayHQ-APIs). This notebook does not require any manual work beforehand (e.g., receiving ad-hoc spreadsheets or exporting fixtures from PlayHQ web interface).

## Pre-requisites

- Python 3.8+ interpreter.
- Jupyter notebooks.
- Non-default packages: `pandas`, `json`, `pyshorteners`, `coloredlogs`:

    ```shell
    $ pip install pandas json pyshorteners coloredlogs
    ```

## How to use it

First, configure your club by editing file `config.py` with the following information:

- PlayHQ keys to access the Public API:
  - Organization id. (e.g., "`8c4d5431-eaa5-4644-82ac-992abe224b88`")
  - `x-api-key`: provided by PlayHQ support.
  - `x-tenant`: the id of the sport (e.g., `bv` for Basketball Victoria).
- Season information, including the name as it appears in PlayHQ.

These constants most often will need to be set once for the club/season.

Finally, to run the system, open notebook [playhq_scrape.ipynb](playhq_scrape.ipynb) and run the system cell by cell, checking on the way all is consistent.

In the last steps, it will generate a `CSV` file ready to be up imported to TeamApp in the Schedule section.

By default, the system extracts game for **next Saturday**, but this can be changed by setting constant `GAME_DATE`.

## Useful resources & Links

- [PlayHQ API documentation](https://support.playhq.com/hc/en-au/sections/4405422358297-PlayHQ-APIs).
- [PlayHQ API's technical documentation](https://docs.playhq.com/tech).

## Contact

All scripts have been developed by Sebastian Sardina (ssardina@gmail.com).
