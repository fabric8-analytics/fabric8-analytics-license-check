# Docker container that tests the license_check.py

FROM fedora:23

# basic build deps
RUN dnf -y install bash bzip2 coreutils cpio diffutils findutils gawk gcc gcc-c++ grep gzip info make patch redhat-rpm-config rpm-build sed shadow-utils tar unzip util-linux-ng which iso-codes && dnf clean all

# we need to rebuild oslc, so we need quite some other deps
RUN dnf -y install boost-devel file-devel glib2-devel openssl-devel pcre-devel perl-Text-Template php postgresql-devel rpm-devel wget devscripts-minimal && dnf clean all

# install oslc
ADD get_oslc.sh /root/
RUN cd /root && ./get_oslc.sh
ADD new_licences/* /usr/share/oslc-3.0/licenses/

# main worker script that returns JSON
ADD license_check.py /root/

# sources must be available on expected place
CMD ["/root/license_check.py", "/tmp/sources" ]


