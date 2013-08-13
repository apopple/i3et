===========
DESCRIPTION
===========

This collection of python scripts can be used as a notification daemon
for i3bar to display notifications on the status bar.

========
PROGRAMS
========

./i3et.py

This program sets up a FIFO in /tmp/i3et to listen for incoming JSON
data from either the notification program or i3status. It can also be
used to multiplex data from other programs onto the status bar using
the format described below.

./notifications.py

Listens on the org.freedesktop.Notifications DBus name for DBus
notifications and outputs JSON formatted data to the i3et FIFO
(/tmp/i3et by default).

===========
JSON FORMAT
===========

The i3et program accepts JSON formatted output in a format similar to
that of the i3status program with some enhancements as described
below.

Example format:
[{"module": "notify"},
 {"color": "#ffffff", "_id": "Test", "full_text": "hello", "_display_for": 10}]

module:
	This parameter identifies a block of output that will be
	grouped together as a single block on the status bar in the
	order each subsequent dictionary appears in the JSON list.

_id:
	Used as unique identity for this output. Subsequent blocks
	with this identity will overwrite this block.

_display_for:
	How long (in seconds) to show the output for. After this
	time the output will be removed from the status bar.
