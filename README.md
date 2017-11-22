# GreyBox Overview #
GreyBox is a single-host Internet simulator for offline exercise and
training networks. It allows a single host (physical or VM) to provide
the illusion of connectivity to the real Internet: a realistic BGP
backbone topology with point-to-point link delays based on physical
distance between the routers' real-world locations, combined with
TopGen's application services (HTTP, DNS, email, etc.).

## Installation ##
GreyBox depends on the following software packages:

        TopGen
        CORE (see https://github.com/coreemu/core)
        quagga
        keepalived
        dhcp (server)

Running the './install.sh' script will copy all components of GreyBox
to the appropriate locations on the filesystem. Also, see
'./contrib/greybox.spec' for instructions on how to build a GreyBox RPM
package.

*FIXME:* Pre-built binary package repositories for various platforms
(Fedora, EPEL, etc.) will be offered in the near future, and will provide
built-in dependency resolution.

## Design ##
GreyBox relies heavily on TopGen (an application service simulator), and
on the CORE container-based network simulator. In essence GreyBox provides
an elaborate network topology configuratin to be simulated by CORE, with
application services to be provide by TopGen. You are encouraged to read
the documentation for both TopGen (included with the package), and for
CORE (at http://downloads.pf.itd.nrl.navy.mil/docs/core/core-html/).

### Networked Containers ###
An LXC container is wrapped around each of several instances of Quagga's
bgpd, to allow running them side by side as processes on the same host,
rather than requiring a dedicated VM, complete with its own running guest
kernel, to be wrapped around each individual bgpd instance.

In addition to providing each containerized bgpd instance with its own
dedicated set of (virtual) network interfaces, the CORE simulator provides
a convenient GUI for visualizing the network topology, facilitates editing
the properties of each container and of the inter-container network links
(implemented as virtual bridges connecting together the virtual interfaces
assigned to several containers), and allows users to start command shells
from inside each container for further configuration and troubleshooting.

While currently popular container orchestration solutions (e.g., Docker)
are mainly targeted at running pre-packaged software bundles in containers
while minimizing the expectations and dependencies required of the hosting
server, CORE is designed to launch multiple instances of native software
already present on the host, and is perfectly suited for GreyBox's frugal,
minimalist use case.

### External Connectivity ###
Network interfaces belonging to the host may be bridged together with
containers' virtual interfaces in a CORE topology map, thus providing
simulated Internet access to external machines.

### Routing & Application Service Reachability ###
TopGen application services are hosted in a dedicated container, which is
linked to every containerized BGP router over a virtual 0-delay Ethernet
bridge, a.k.a. the "FTL" LAN.

As explained in the TopGen's documentation, the TopGen container will
respond to any of a very large set of /32 host IP addresses, all of which
are configured as secondaries on its loopback interface.

Each BGP router announces a set of static routes to its neighbors, with
the next-hop value set to TopGen's FTL network address. Each router will
announce a default route, but also a set of more-specific /8 routes, the
union of which covers all service IPs held by TopGen. The /8 routes
announced by each BGP router have been carefully selected to approximately
match their geographic assignment on the real-world Internet.

The result is that client-originated traffic will travel through a
geographically realistic set of hops before being handed over to TopGen
(via the FTL LAN) by one of the BGP routers announcing the matching /8.

### Return Application Traffic ###
While it is the designated next-hop for *all* routes announced into BGP by
*every* backbone router, TopGen itself does not run any routing software,
and no BGP peerings are set up over the FTL virtual LAN. When a TopGen
service responds to a client request, reply packets are sourced from the
same secondary loopback IP the client traffic was sent to in the first
place. All such traffic is forwarded to a virtual default gateway IP
address on the FTL network, redundantly supported (through VRRP) by all
BGP routers on their FTL network interfaces. In practice, it doesn't
matter how reply traffic from application services is routed back to the
client, since the latter can't even tell, as traceroutes from the client
reflect only hops on the outbound path.

## Getting Started ##
After installing the GreyBox package and its dependencies, follow this
basic process to set up an "Internet-in-a-box" GreyBox server:

### Configure TopGen ###
See the documentation included with the TopGen package for recursively
scraping a collection of web sites, setting up virtual email domains,
and configuring multiple root, top-level, and caching name servers. Do
not enable or start any TopGen services: TopGen will be brought up by the
CORE network simulator as a container, using a different set of startup
scripts.

*NOTE:* To allow TopGen's DNS service to resolve point-to-point BGP router
interfaces, the IP address to FQDN hostname mappings must be loaded into
the DNS database, using the following command:

        topgen-mkdns.sh -f -x /usr/share/greybox/etc/backbone.hosts

### Configure Nameserver(s) on GreyBox Host ###
It is recommended that name servers in '/etc/resolv.conf' be set to
8.8.8.8 and/or 8.8.4.4. CORE containers retain access to most of the host
filesystem (except for explicitly assigned, dedicated subdirectories, e.g.
'/var/log/'), and will thus refer to the TopGen-provided 8.8.8.8 and
8.8.4.4 addresses for in-game DNS resolution. If the GreyBox host retains
access to the *real* Internet, processes not part of the simulation will
be directed to the real Google-provided caching DNS servers at the same
addresses, by the same '/etc/resolv.conf' file.

### Load a GreyBox Network Map ###
The GreyBox package ships with two Internet simulation maps (in the
'/usr/share/greybox/maps/' folder):

        backbone.imn: an entirely self-contained Internet simulation, with
                      69 BGP backbone router containers, a TopGen service
                      container, and two "client laptop" containers for
                      running tests (e.g. traceroute, dns resolution, text
                      mode email with mailx or mutt, etc.).

        backbone_ext.imn: same as above, except with one of the "client"
                          containers replaced with an RJ-45 "ethernet"
                          port, which may be mapped to one of the GreyBox
                          host's network interfaces, which allows the
                          Internet simulation to be accessed over the
                          network from outside the GreyBox machine itself.
                          *NOTE:* This file must be edited before use, to
                          replace "ethX" with the name of one of the real
                          network interfaces available on the GreyBox host.

First, ensure that the CORE daemon service is running:

        systemctl start core-daemon

Then, from a terminal window, load a simulation map into the CORE GUI:

        core-gui /usr/share/greybox/maps/backbone.imn

When the GUI is up, press the green "play" button to start the simulation.
Once the simulation is fully underway, right-click on any of the container
icons to select "Shell Window -> bash" to get a terminal window from the
inside perspective of that specific container. On containers representing
BGP routers, one may select "Shell Window -> vtysh" for direct access to
the Cisco-like user interface exposed by the Quagga software.

### Loading a GreyBox Map at Boot ###
The GreyBox package also ships with a systemd service which, when enabled:

        systemctl enable greybox

will load and start a simulation map when the GreyBox host machine boots.
The default map, '/etc/greybox/map.imn', ships as an identical clone of
the self-contained '/usr/share/greybox/maps/backbone.imn', and, as such,
can be used immediately without modification. However, if external access
to the simulation is required, one must edit '/etc/greybox/map.imn' using
e.g., '/usr/share/greybox/maps/backbone_ext.imn' as a starting point.

### External Connectivity Considerations ###
Recent Linux installs tend to use unpredictable naming conventions for
the host's network interfaces, from the traditional 'eth0' to names like
'ens32' or 'enp11s0'. Before using a network map file designed for outside
connectivity (e.g., '/usr/share/greybox/maps/backbone_ext.imn'), be sure
to replace the placeholder string "ethX" with the name of the real host
interface you wish to dedicate to the simulation.

Additionally, ensure that interfaces dedicated to the simulation are not
managed by any host networking sybsystem (e.g., NetworkManager on RedHat
flavored distributions). In the simplest case, if *all* host interfaces
are assigned to the simulation, NetworkManager may be turned off entirely:

        systemctl stop NetworkManager
        systemctl disable NetworkManager

Alternatively, any interface dedicated to the simulation can be marked as
off-limits to NetworkManager by adding the line "NM_CONTROLLED=no" to its
'/etc/sysconfig/network-scripts/ifcfg-ethX' config file. Similar steps
exist (and should be followed) on distributions which are not following
RedHat/Fedora conventions.
