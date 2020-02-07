#!/bin/bash

# install GreyBox
# (glsomlo@cert.org, June 2016)

/bin/echo "Installing using the following filesystem locations:"
/bin/echo "NAME         =${NAME:=greybox};"
/bin/echo "BUILDROOT    =${BUILDROOT:=};"
/bin/echo "UNITDIR      =${UNITDIR:=/usr/lib/systemd/system};"
/bin/echo "SYSCONFDIR   =${SYSCONFDIR:=/etc};"
/bin/echo "DATADIR      =${DATADIR:=/usr/share};"

/usr/bin/install -d $BUILDROOT/$UNITDIR
/usr/bin/install -m 0644 -t $BUILDROOT/$UNITDIR systemd/*

/usr/bin/install -m 0644 -D share/maps/backbone.imn \
                            $BUILDROOT/$SYSCONFDIR/$NAME/map.imn

/usr/bin/install -m 0644 -D etc/profile.d_greybox.sh \
                            $BUILDROOT/$SYSCONFDIR/profile.d/$NAME.sh

for i in clipart etc maps; do
  /usr/bin/install -d $BUILDROOT/$DATADIR/$NAME/$i
  /usr/bin/install -m 0644 -t $BUILDROOT/$DATADIR/$NAME/$i share/$i/*
done
