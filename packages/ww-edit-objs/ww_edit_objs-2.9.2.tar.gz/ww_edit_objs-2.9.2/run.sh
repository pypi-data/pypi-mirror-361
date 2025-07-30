#! /bin/sh

# fail on first error
set -e

# protect cwd
pushd . &> /dev/null

ScriptDir="$( cd "$( dirname "$0" )" && pwd )"
PoetryBin=/Library/Frameworks/Python.framework/Versions/3.11/bin/poetry

# script is at proj_root/
cd "$ScriptDir"
servName=$(basename "$ScriptDir")
$PoetryBin run python src/"$servName"_cli.py "$@"

popd &> /dev/null
