Name: greybox
Version: 0.0.97
Release: 1%{?dist}
Summary: GreyBox: Single-Host Internet Simulator
License: BSD
Url: https://github.com/cmu-sei/%{name}
Source0: http://github.com/cmu-sei/%{name}/archive/master/%{name}-master.tar.xz
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires: core-daemon >= 6.0, core-gui
Requires: frr
Requires: topgen >= 0.0.97
Requires: keepalived, dhcp-server
Requires: iodine
BuildRequires: systemd-units
BuildArch: noarch

%description
GreyBox is a single-host internet simulator which uses containerized router
instances (e.g., FRR or Quagga) to implement the backbone network routing
infrastructure, and a containerized TopGen server for applications such as
HTTP, DNS, email, etc. The container topology is based on the CORE network
simulator.

%prep
%setup -q -n %{name}-master

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
# (bash) shell settings:
%{_sysconfdir}/profile.d/%{name}.sh
# /usr/share/greybox data:
%{_datadir}/%{name}/

%changelog
* Fri Feb 07 2020 Gabriel Somlo <glsomlo at cert.org> 0.0.97-1
- initial fedora package
