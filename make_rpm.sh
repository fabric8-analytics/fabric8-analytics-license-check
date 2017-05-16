#!/bin/sh

usage() {
    echo "Usage: $(basename "$0") --source|--binary"
    exit 1
}

if [ $# -ne 1 ] ; then
    usage
fi

NAME=license-check
RPMBUILD_DIR=~/rpmbuild

tar=$(./make_archive.sh)
mkdir -p "${RPMBUILD_DIR}/SOURCES/" "${RPMBUILD_DIR}/SPECS/"
cp "$tar" "${RPMBUILD_DIR}/SOURCES/"
cp -f $NAME.spec "${RPMBUILD_DIR}/SPECS/"
rm "${RPMBUILD_DIR}/SPECS/SRPMS/license-check-*.src.rpm"

if [ "$1" == "--source" ] ; then
    echo "rpmbuild -bs ${RPMBUILD_DIR}/SPECS/$NAME.spec"
    rpmbuild -bs "${RPMBUILD_DIR}/SPECS/$NAME.spec"
elif [ "$1" == "--binary" ] ; then
    echo "rpmbuild -bb ${RPMBUILD_DIR}/SPECS/$NAME.spec"
    rpmbuild -bb "${RPMBUILD_DIR}/SPECS/$NAME.spec"
else
    usage
fi
