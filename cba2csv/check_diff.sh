#!/bin/bash
#
# Checks the difference time of games between 2 CSV files
#
# Example:
#
#   ❯ ../../../cba2csv/check_diff.sh 2022-02-26.Magic_Round\ 8_SCHEDULE-01.Copy\ of\ Copy\ of\ Saturday\ 26th\ February\ 2022\ v1.csv 2022-02-26.Magic_Round\ 8_SCHEDULE-02.Copy\ of\ Copy\ of\ Saturday\ 26th\ February\ 2022\ v1.csv
#   5a6
#   > U12 Girls Purple - Round 8,U12 Girls Purple,2022-02-26,2022-02-26,08:30:00,09:10:00,"RSVP is YES by default - if you cannot make it, please let your Team Manager know as soon as possible.
#   7d7
#   < U12 Girls Purple - Round 8,U12 Girls Purple,2022-02-26,2022-02-26,09:20:00,10:00:00,"RSVP is YES by default - if you cannot make it, please let your Team Manager know as soon as possible.

##### GET OPTIONS FROM COMMAND-LINE
NO_ARGS=$#   # Get the number of arguments passed in the command line

MY_NAME=${0##*/} 

#echo
#echo "# arguments called with ---->  ${@}     "
#echo "# \$1 ---------------------->  $1       "
#echo "# \$2 ---------------------->  $2       "
#echo "# path to me --------------->  ${0}     "
#echo "# parent path -------------->  ${0%/*}  "
#echo "# my name ------------------>  ${0##*/} "
#echo
#exit

if [ "$NO_ARGS" -lt 2 ]; then
  printf "**** Script by Sebastian Sardina (2022) \n\n"
  printf "usage: ./$MY_NAME CSV_FILE_1 CSV_FILE_2\n"
  exit
fi

##### SCRIPT STARTS HERE
GREP_TEXT="RSVP"    # unique text in the line where the date+time is located to check diff
FILE1=$1
FILE2=$2



diff --color=always <(cat "$FILE1" | grep "$GREP_TEXT")  <(cat "$FILE2" | grep "$GREP_TEXT")


