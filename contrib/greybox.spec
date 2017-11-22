Name: greybox
Version: 0.0.96
Release: 1%{?dist}
Summary: GreyBox: Single-Host Internet Simulator
License: BSD
Url: http://cert.org
Source0: http://download.cert.org/%{name}-%{version}.tar.xz
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires: core-daemon >= 5.0, core-gui
Requires: quagga
Requires: topgen >= 0.0.95
Requires: keepalived, dhcp-server
BuildRequires: systemd-units
BuildArch: noarch

%description
GreyBox is a single-host internet simulator which uses containerized
quagga instances to implement the routing backbone, and a containerized
TopGen application server for HTTP, DNS, email, etc. The container
topology is implemented using the CORE network simulator.

%prep
%setup -q

%build
echo "nothing to build"

%install
NAME=%{name} BUILDROOT=%{buildroot} UNITDIR=%{_unitdir} \
             SYSCONFDIR=%{_sysconfdir} DATADIR=%{_datadir} \
  ./install.sh

%post
%systemd_post greybox.service

%preun
%systemd_preun greybox.service

%postun
%systemd_postun_with_restart greybox.service

%files
%defattr(-,root,root,-)
# miscellaneous doc files and samples:
%doc README.md LICENSE* TODO contrib
# systemd unit file:
%{_unitdir}/greybox.service
# /etc/greybox directory and config file(s):
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/map.imn
# /usr/share/greybox data:
%{_datadir}/%{name}/

%changelog
* Fri Jun 03 2016 Gabriel Somlo <glsomlo at cert.org> 0.1.0-1
- initial fedora package
