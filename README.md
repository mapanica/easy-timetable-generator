timetable-frequency-creator
===========================

This script generates timetable information for a bus system based on frequencies
to a json suitable for the use with [osm2gtfs](https://github.com/grote/osm2gtfs).
As a starting point, [xamanu/timetable-csv2json](https://github.com/xamanu/timetable-csv2json) has been used,
but then changed quite a lot to support a more general and specific input format.
In some future, could be integrated into [osm2gtfs](https://github.com/grote/osm2gtfs) to support frequency data.

Please make sure you use Python 3 to run it.

Use
------------

* Create a folder inside `data` and put an `input.csv` in it.
* Create your `input.csv` according to the following scheme, separated by commas:
	* `ref` = your public transport route number (as used in OSM)
	* `from` = the first stop (as in OSM)
	* `to` = the last stop (as in OSM)
	* `opening-hours` = opening hours, subset from the OSM opening_hours specification, should look like `{Weekday(-{Weekday})} {start_hour:start_min}-{end_hour:end_min}`, for example `Mo-Sa 07:15-12:30`, separated by a `;`.
	* `duration` = the time the public transport service needs to fulfill the route
	* `frequency` = number of minutes between public transport services on this route
* Run `python3 convert.py`


License
-------

![GNU GPLv3 Image](https://www.gnu.org/graphics/gplv3-127x51.png)

This program is Free Software: You can use, study share and improve it at your
will. Specifically you can redistribute and/or modify it under the terms of the
[GNU General Public License](https://www.gnu.org/licenses/gpl.html) as
published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
