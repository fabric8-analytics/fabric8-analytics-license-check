#!/usr/bin/env python3

# TODO:
# setup.py or PKG-INFO may include interesting information: license="ZPL 2.1"
# we should parse it and similar in other ecosystems
# another source os information can be README

import os
import argparse
import subprocess
import json
import re
from collections import defaultdict

# file is downloaded from https://code.engineering.redhat.com/gerrit/gitweb?p=pelc.git;a=blob;f=pelc/packages/fixtures/license.json;h=6d1c1adeada20b48dc21b4ebf76228c52bc3db43;hb=develop
# there should be up to date infos, for future we should implement way how to download it
# and cache it somehow, because now during each license check I parse it
def parse_pelc_licenses(path):
    variants = defaultdict(set)
    short_names = {}
    file_name = 'pelc-packages-fixtures-license.json'

    if path is None:
        path = os.path.join('/usr/share/license-check/', file_name)

    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), file_name)

    try:
        with open(path) as data_file:
            data = json.load(data_file)
            for d in data:
                if d["model"] == "packages.licensevariant":
                    variants[d["fields"]["license"]].update([d["fields"]["identifier"]])

                if d["model"] == "packages.license":
                    short_names[d["pk"]] = d["fields"]["short_name"]
    except IOError:
        print("Error: Unable to open license mapping file: %r"\
            %os.path.abspath(path))
        exit(1)

    matching = {}
    for it, short_name in short_names.items():
        for v in variants[it]:
            matching[v] = short_name

    return matching

def get_pelc_license_name(lic, pelc_license_mapping):
    lic = lic.strip()
    pelc_license_name = pelc_license_mapping.get(lic)
    if not pelc_license_name:
        print("Error: unknown to PELC license %r" % lic)
        pelc_license_name = lic + " (unknown to PELC)"
    return pelc_license_name

def parse_oslc_output(source, output, result, pelc_license_mapping):
    """
    Output of oslc looks like this:
    oslccli -s -d <abs-source-path>


    Source files:       1
    License files:      0
    All files:          1
    Distinct licenses:  2
    Conflicts (ref):    0
    Conflicts (global): 1

    License        Count   Incompatible with
    mitnfa         1       sgi-b-2.0
    sgi-b-2.0      1       mitnfa


    <rel-path-in-source>: sgi-b-2.0 (67%) incompatible with (mitnfa), mitnfa (35%) incompatible with (sgi-b-2.0)
    ...
    """
    P_BEGIN = 1
    P_STATS = 2
    P_FHEAD = 3
    P_LICENSE_STATS = 4
    P_FILES = 5

    OSLC_TRESHOLD = 0

    status = P_BEGIN
    lnumber = 0

    for line in output:
        line = line.decode('utf-8')
        lnumber += 1

        # skip leading empty lines
        if status == P_BEGIN:
            if len(line.strip()) == 0:
                continue
            else:
                status = P_STATS

        # parse stats
        if status == P_STATS:
            if len(line.strip()) == 0:
                status = P_FHEAD
            else:
                try:
                    (k,v) = line.split(':')
                    result['oslc_stats'][k] = int(v.strip())
                except (KeyError, ValueError):
                    print("Error: bad format of STATS output on line {}:".format(lnumber))
                    print(line)
                    exit(1)
                continue

        # parse license stats header
        if status == P_FHEAD:
            if len(line.strip()) == 0:
                continue
            else:
                status = P_LICENSE_STATS
                continue

        # parse license stats
        if status == P_LICENSE_STATS:
            if len(line.strip()) == 0:
                status = P_FILES
                continue
            try:
                licence_info = line.split()
                variant_id = licence_info[0]
                license_name = get_pelc_license_name(variant_id,
                                                     pelc_license_mapping)
                result['license_stats'].append({'variant_id': variant_id,
                                                'license_name':license_name,
                                                'count': int(licence_info[1])})
            except (KeyError, ValueError):
                print("Error: bad format of LICENSE STATS output on line {}:".format(lnumber))
                print(line)
                exit(1)
            continue

        # parse file list
        if status == P_FILES:
            if len(line.strip()) == 0:
                continue

            try:
                # DEBUG: print(line.strip())
                # split according last ':' character
                lp = line.split(':')
                fname = ':'.join(lp[:-1])
                licences = lp[-1]

                # start with empty list of licences
                result_licences = []

                # Ignore empty lines and those where output indicates no matches
                if (not len(licences.strip()) or
                        re.search(': No matches$', line)):
                    continue

                # split information for particular licenses for specific file
                license_match = None
                per_file_pattern = '([\w\._-]+) \(([0-9]+)%\)( incompatible with \(([^\)*]+)\))?'
                for license_match in re.finditer(per_file_pattern, licences):
                    match = int(license_match.group(2))
                    if match < OSLC_TRESHOLD:
                        continue
                    variant_id = license_match.group(1)
                    license_name = get_pelc_license_name(variant_id,
                                                         pelc_license_mapping)
                    license_info = {'variant_id': variant_id,
                                    'license_name': license_name,
                                    'match': match}
                    result_licences.append(license_info)
                if license_match is None:
                    # sometimes there is no percent from unknown reason, in that case
                    # split it only and check whether it matches some file
                    if licences.find('incompatible') == -1:
                        for lic in licences.split(','):
                            sample_path = '/usr/share/oslc-3.0/licenses/{0}.txt'
                            variant_id = lic.strip()
                            if os.path.exists(sample_path.format(variant_id)):
                                license_name = get_pelc_license_name(variant_id,
                                                                     pelc_license_mapping)
                                license_info = {'variant_id': variant_id,
                                                'license_name': license_name}
                                result_licences.append(license_info)

                if len(result_licences) > 0:
                    # either add license to existing list or create new list
                    if not fname in result['files']:
                        result['files'][fname] = []
                    result['files'][fname] += result_licences

            except (KeyError, ValueError):
                print("Error: bad format of FILES output on line {}:".format(lnumber))
                print(line)
                exit(1)

    return result


# gather some interesting stats
def get_stats(result):
    result['summary']['source_files'] = result['oslc_stats']['Source files']
    result['summary']['all_files'] = result['oslc_stats']['All files']
    result['summary']['license_files'] = result['oslc_stats']['License files']
    result['summary']['licensed_files'] = len(result['files'].keys())
    sure_licenses = set()
    distinct_licenses = {}
    for f in result['files']:
        distinct_licenses_file = set()
        for l in result['files'][f]:
            if not l['license_name'] in distinct_licenses:
                distinct_licenses[l['license_name']] = 0
            distinct_licenses[l['license_name']] += 1
            distinct_licenses_file.add(l['license_name'])
        if len(result['files'][f]) >= 1 and len(distinct_licenses_file) == 1:
            sure_licenses.add(l['license_name'])
    result['summary']['sure_licenses'] = list(sure_licenses)
    result['summary']['distinct_licenses'] = [{"license_name": k, "count": v}
                                              for k, v in distinct_licenses.items()]

    return result

def print_result(result, pretty=False):
    if pretty:
        print (json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        print (json.dumps(result))
#    print ("Files with license: {}".format(len(result['files'])))
#     for f in result['files'].keys():
#         print(f)

def run_oslc(source, result, pelc_license_mapping):
    cmd = ['oslccli', '-s', '-d', os.path.abspath(source)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.stdout.readlines()

    # oslc returns 1 if conflicts were found, which doesn't mean the scan
    # failed, so don't check exit code
    retval = p.wait()

    return parse_oslc_output(source, output, result, pelc_license_mapping)

def main():
    parser = argparse.ArgumentParser(description='License check tool')
    parser.add_argument('source', metavar='path',
                        help='path to sources dir')
    parser.add_argument('--only-stats', help='Show only stats', action='store_true')
    parser.add_argument('--only-license', help='Show only best guessed license', action='store_true')
    parser.add_argument('--pretty', help='Show nicely formatted output', action='store_true')
    parser.add_argument('--mapping-path', help='Specify where is license mapping stored')
    args = parser.parse_args()
    result = {'oslc_stats':{}, 'summary':{}, 'files': {}, 'license_stats':[]}
    pelc_license_mapping = parse_pelc_licenses(args.mapping_path)
    result = run_oslc(args.source, result, pelc_license_mapping)
    result = get_stats(result)

    new_files = []
    for k, v in result['files'].items():
        new_files.append({"path": k, "result": v})
    result['files'] = new_files

    result['status'] = 'success'
    if args.only_license:
        if len(result['summary']['sure_licenses']) > 0:
            print(', '.join(result['summary']['sure_licenses']))
        else:
            print('No good match')
    elif args.only_stats:
        print_result(result['summary'], args.pretty)
    else:
        print_result(result, args.pretty)

if __name__ == "__main__":
    main()

