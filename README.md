# Team App Scheduler Builder

This repo contains tools to build CSV files with fixtures schedules to import into [TeamApp](https://www.teamapp.com) system for a club. Many sport clubs use the [TeamApp](https://www.teamapp.com) platform to run the club's teams, which include distributing the game fixtures for each round.

Entering each game into [TeamApp](https://www.teamapp.com) could become a very demanding and error-prone task as soon as the club has a few teams. This system will allow you to populate the schedule for the next round of games in minutes and with almost no manual work. Hopefully! :-)

The script was originally done to support the [Brunswick Magic Basketball Club](https://www.brunswickmagic.com/) (Melbourne, Australia), from [Coburg Basketball Association (CBA)](https://coburgbasketball.org.au/). The tools should be usable for any club competing in CBA or under the [PlayHQ](https://bv.playhq.com/) system (even for other sports).

As of July 2022, the system was simplified and moved to Python-based Jupyter notebook [playhq_scrape.ipynb](playhq_scrape.ipynb) and direct interaction with the [PlayHQ](https://bv.playhq.com/)'s Public [API](https://support.playhq.com/hc/en-au/sections/4405422358297-PlayHQ-APIs). This notebook does not require any manual work beforehand (e.g.,receiving a spreadsheet or exporting fixture from Pl and can produce CSV files that are ready to be imported into TeamApp.

To run the system the following is needed:

- PlayHQ keys to access the Public API:
    - Organization id. (e.g., "`8c4d5431-eaa5-4644-82ac-992abe224b88`")
    - `x-api-key`: provided by PlayHQ support.
    - `x-tenant`: the id of the sport (e.g., `bv` for Basketball Victoria).

- Python 3.8+ interpreter.
- Jupyter notebooks.
- Non-default packages: `pandas`, `json`, `pyshorteners`, `coloredlogs`:

    ```shell
    $ pip install pandas json pyshorteners coloredlogs
    ```

Just open notebook [playhq_scrape.ipynb](playhq_scrape.ipynb) and 

## The original cba2csv system

The original system, used in 2021-2022, can be found under folder [cba2csv/](cba2csv/). 

That system is able to parse either:

1. [CBA](https://coburgbasketball.org.au/) fixture spreadsheets (provided by CBA on Wednesdays before each round);
2. CSV fixtures files directly exported from [PlayHQ](https://bv.playhq.com/) administration site, 

and produce CSV files ready to be imported as schedules or events into the Club's [TeamApp](https://www.teamapp.com) site.

Please read [cba2csv/README.md](cba2csv/README.md) for more information and instructions how to use it.
## Contact

All scripts have been developed by Sebastian Sardina (ssardina@gmail.com).
