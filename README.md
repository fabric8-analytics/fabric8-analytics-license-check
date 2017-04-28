# License check

Goal of this tool is to find out licences used by project and potentially some licences issues.

There are couple of tools that work with licences, but nothing is much better than others, so this tool combines more approaches to get to better results.

These tools are tested:

* nomossa from fossology (bigger project)
* licorice (python based tool from tradej)
* licensecheck tool that is part of devscripts-minimal (debian)
* oslc (used by new PELC, remade Package Wrangler), it may either use original set of SPDX licences or there is variant with all Fedora licences

Tool `licensecheck` matches licences using regular expression within files header, which is effective but it cannot obviously match everything.

Other tools work on basis of comparing texts of licences by some fulltext algorithm, which may be better in cases the text is long enough and not much changed. However, sometimes there are also false results returned, because texts of some licences are too similar.

## Which tools are used

Currently, this tool combines `oslc` with Fedora licences. The tool also returns specific output for files that include "license" in its name, which usually means this file is a license file.

## Running license-check

For running the tool, you need to have the sources already unpacked in some directory. Then, run:

```
./license_check.py <sources-dir>
```

### Dockerfile for license-check

For easier running the license-check, there is a Dockerfile that can be used to build a container that works like this:

```
docker build -t license-checker-test .
docker run --rm -ti -v /path/to/sources:/tmp/sources license-checker-test
```

### RPMs

RPMs for Fedora are in COPR repo: https://copr.fedorainfracloud.org/coprs/jpopelka/license-check

The same repository also contains oslc.

## Example output of the license check

The command above returns JSON like the following. It uses quite simple structure, so feel free to use the example for describing the structure:

```
{
    "files": [
        {
            "path": "ext/nokogiri/xml_libxml2_hacks.c",
            "result": [
                {
                    "license": "fal-1.3-s",
                    "license_id": "Free Art",
                    "match": 14,
                    "whofound": "oslc"
                }
            ]
        },
        {
            "path": "LICENSE.txt",
            "result": [
                {
                    "license": "mitnfa",
                    "license_id": "MITNFA",
                    "match": 35,
                    "whofound": "oslc"
                }
            ]
        }
    ],
    "license_stats": [
        {
            "count": "1",
            "license": "fal-1.3-s",
            "license_id": "Free Art"
        },
        {
            "count": "1",
            "license": "mitnfa",
            "license_id": "MITNFA"
        }
    ],
    "oslc_stats": {
        "All files": 303,
        "Conflicts (global)": 1,
        "Conflicts (ref)": 0,
        "Distinct licenses": 2,
        "License files": 1,
        "Source files": 68
    },
    "status": "success",
    "summary": {
        "all_files": 303,
        "distinct_licenses": [
            {
                "count": 1,
                "name": "MITNFA"
            },
            {
                "count": 1,
                "name": "Free Art"
            }
        ],
        "licenced_files": 2,
        "license_files": 1,
        "source_files": 68,
        "sure_licenses": [
            "MITNFA",
            "Free Art"
        ]
    }
}
```

## Contributing

See our [contributing guidelines](https://github.com/fabric8-analytics/common/blob/master/CONTRIBUTING.md) for more info.
 
