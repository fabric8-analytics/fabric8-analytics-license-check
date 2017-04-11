#!/bin/sh

set -xe

# get SRPM for oslc from brew and rebuild locally
wget http://download.devel.redhat.com/brewroot/packages/oslc/3.0/5/src/oslc-3.0-5.src.rpm
rpmbuild --rebuild oslc-3.0-5.src.rpm 
dnf -y install /root/rpmbuild/RPMS/noarch/oslc-3.0-5.noarch.rpm

# remove some weird license matches that produce too many false positives
rm -f /usr/share/oslc-3.0/licenses/{crc32,diffmark}.*

