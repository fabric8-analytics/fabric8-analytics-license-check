%global oslc_ver 3.0
%global oslc_licenses_dir %{_datadir}/oslc-%{oslc_ver}/licenses/

Summary: Tool to find out project's licences
Name:    license-check
Version: 0.3
Release: 3%{?dist}
License: ASL 2.0
URL:     https://github.com/fabric8-analytics/license-check

# ./make_archive.sh
Source0: license-check-%{version}.tar.gz

BuildArch: noarch

Requires: oslc

%description
Goal of this tool is to find out licences used by project and potentially some licences issues.

%prep
%setup -q

%install
mkdir -p %{buildroot}%{_bindir}
cp -av license_check.py %{buildroot}%{_bindir}

mkdir -p %{buildroot}%{_datadir}/%{name}
cp -av pelc-packages-fixtures-license.json %{buildroot}%{_datadir}/%{name}

%posttrans
# remove some weird license matches that produce too many false positives
rm -f %{oslc_licenses_dir}{crc32,diffmark}.*

%files
%doc README.md
%{_bindir}/license_check.py
%{_datadir}/%{name}/pelc-packages-fixtures-license.json

%changelog
* Fri May 05 2017 Jiri Popelka <jpopelka@redhat.com> - 0.3-3
- Remove 'Forbidden Phrase'
- Raise OSLC_TRESHOLD

* Thu Apr 27 2017 Jiri Popelka <jpopelka@redhat.com> - 0.3-2
- renamed to license-check

* Tue Sep 13 2016 Slavek Kabrda <bkabrda@redhat.com> - 0.3-1
- 'details.license_stats[N].count` is now integer, not string

* Wed May 18 2016 Nick Coghlan <ncoghlan@redhat.com> - 0.2-1
- Switched to the v2-0-0 license schema
- 'license' field renamed to 'variant_id'
- 'license_id' field renamed to 'license_name'
- 'name' field renamed to 'license_name'
- 'licenced_files' renamed to 'licensed_files'

* Tue May 17 2016 Nick Coghlan <ncoghlan@redhat.com> - 0.1-4
- Remove remnants of previous licensecheck usage

* Tue Apr 26 2016 Jiri Popelka <jpopelka@redhat.com> - 0.1-3
- Python 3, no 'incompatibility' in output, README update

* Tue Apr 19 2016 Pavel Kajaba <pkajaba@redhat.com> - 0.1-2
- Dumped new_licenses folder, Added license mapping files into /usr/share

* Fri Feb 19 2016 Jiri Popelka <jpopelka@redhat.com> - 0.1-1
- initial release
