#!/bin/sh

NAME=cucos-license-check

# get version
VERSION_MAJOR=0
VERSION_MINOR=3
VERSION="${VERSION_MAJOR}.${VERSION_MINOR}"

# create dir for archive
archive_dir="${NAME}-${VERSION}"
mkdir -p "$archive_dir/"
cp -r \
   cucos_license_check.py \
   pelc-packages-fixtures-license.json \
   README.md \
   "$archive_dir/"

# create archive
tar czf "${NAME}-${VERSION}.tar.gz" "$archive_dir"

# clean up
rm -rf "$archive_dir"

# report output
echo ${NAME}-${VERSION}.tar.gz
