#!/bin/bash

underline=`tput smul`
noUnderline=`tput rmul`
bold=`tput bold`
normal=`tput sgr0`

scriptName=$(basename $0)
scriptDir=$(dirname $0)
listName="$scriptDir/$scriptName-list.txt"

error() {
	# echo error message if one has been provided
	if [ $# -gt 0 ]; then
		echo "$0: $1"
	fi

	echo "Incorrect usage of $scriptName"
	echo "Please use -h or --help option for further information"
}

help() {
	echo "$scriptName calls the help function of the supplied command iff the"\
			"script for the command exists in $scriptDir"
	echo
	echo "${bold}Usage${normal}: $scriptName [option] command"
	echo "${bold}command${normal} is the name of the script you want to call" \
			"help on e.g. weblink, eh"
	echo
	echo "${bold}NOTE: Script must have a -h option for this command to work" \
			"as intended${normal}"
	echo
	echo "Options:"
	echo " - ${bold}h${normal}        Print this help"
}

callHelp() {
	cmdName=$1
	$cmdName -h
}

while getopts "h" option; do
	case $option in
		h)
			help
			exit;;
		\?)
			error
			exit;;
	esac
done

# determine if an argument has been passed
if [ $# -gt 0 ]; then
	callHelp $1
else
	error "an argument is required"
fi
