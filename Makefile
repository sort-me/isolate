# Makefile for Isolate
# (c) 2015--2024 Martin Mares <mj@ucw.cz>
# (c) 2017 Bernard Blackham <bernard@blackham.com.au>
# (c) 2024 Sort Me <guys@sort-me.org>

all: isolate isolate-check-environment

CC=gcc
CFLAGS=-std=gnu99 -Wall -Wextra -Wno-parentheses -Wno-unused-result -Wno-missing-field-initializers -Wstrict-prototypes -Wmissing-prototypes -D_GNU_SOURCE
LIBS=-lcap

VERSION=2.0
YEAR=2024
BUILD_DATE:=$(shell date '+%Y-%m-%d')
BUILD_COMMIT:=$(shell if git rev-parse >/dev/null 2>/dev/null ; then git describe --always --tags ; else echo '<unknown>' ; fi)

PREFIX = $(DESTDIR)/usr/local
VARPREFIX = $(DESTDIR)/var/local
CONFIGDIR = $(PREFIX)/etc
CONFIG = $(CONFIGDIR)/isolate
BINDIR = $(PREFIX)/bin
SBINDIR = $(PREFIX)/sbin
DATAROOTDIR = $(PREFIX)/share
DATADIR = $(DATAROOTDIR)
MANDIR = $(DATADIR)/man
MAN1DIR = $(MANDIR)/man1
BOXDIR = $(VARPREFIX)/lib/isolate

SYSTEMD_CFLAGS := $(shell pkg-config libsystemd --cflags)
SYSTEMD_LIBS := $(shell pkg-config libsystemd --libs)

isolate: isolate.o util.o rules.o cg.o config.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

%.o: %.c isolate.h
	$(CC) $(CFLAGS) -c -o $@ $<

isolate.o: CFLAGS += -DVERSION='"$(VERSION)"' -DYEAR='"$(YEAR)"' -DBUILD_DATE='"$(BUILD_DATE)"' -DBUILD_COMMIT='"$(BUILD_COMMIT)"'
config.o: CFLAGS += -DCONFIG_FILE='"$(CONFIG)"'

clean:
	rm -f *.o
	rm -f isolate
	rm -f docbook-xsl.css

install: isolate isolate-check-environment
	install -d $(BINDIR) $(SBINDIR) $(BOXDIR) $(CONFIGDIR)
	install isolate-check-environment $(BINDIR)
	install -m 4755 isolate $(BINDIR)
	install -m 644 default.cf $(CONFIG)

.PHONY: all clean install install-doc release
