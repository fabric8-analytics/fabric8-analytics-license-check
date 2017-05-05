#!/bin/sh

set -xe

dnf -y copr enable jpopelka/license-check
dnf -y install oslc

# remove some weird license matches that produce too many false positives
rm -f /usr/share/oslc-3.0/licenses/{crc32,diffmark}.*

