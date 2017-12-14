easy-timetable-generator
========================

This script generates timetable information for a bus system based on frequencies
to a json suitable for the use with [osm2gtfs](https://github.com/grote/osm2gtfs).
As a starting point, [xamanu/timetable-csv2json](https://github.com/xamanu/timetable-csv2json) has been used,
but then changed quite a lot to support a more general and specific input format.
In some near future, could be integrated into [osm2gtfs](https://github.com/grote/osm2gtfs) to support frequency data.

Please make sure you use Python 3 to run it.

Use
------------

* Create a folder `<folder>` inside `data` and put an `frequencies.csv` and an `header.json` in it.
* Create your `frequencies.csv` according to the following scheme, separated by commas:
	* `ref` = your public transport route number (as used in OSM)
	* `from` = the first stop (as in OSM)
	* `to` = the last stop (as in OSM)
	* `via` = an intermediate stop (as in OSM)
	* `intermediates` = intermediate stop names (as in OSM), separated by a `;`
	* `opening-hours` = opening hours, subset from the OSM opening_hours specification, should look like `{Weekday(-{Weekday})} {start_hour:start_min}(-{end_hour:end_min})`, for example `Mo-Sa 07:15-12:30` or `Tu 15:15`, separated by a `;`
	* `exceptions` = the dates (ISO 8601) which are excluded from the service, separated by a `;`
	* `duration` = the time the public transport service needs to fulfill the route
	* `intermediate-durations` = the time the public transport service needs from the first stop to the respective intermediate stop, separated by a `;`, has to be exactly as long as the `intermediates` list
	* `frequency` = number of minutes between public transport services on this route
* The `header.json` file follows the specification [here](https://github.com/grote/osm2gtfs/wiki/Schedule), without the `lines` and the `updated` keys
* Run `python3 convert.py -f <folder>`

There is also an alternative method of expressing frequencies: by the times, the public transport service passes in one hour.
This alternative approach can be used with the `-h` or `--per_hour` flag when running the script (but you have to be sure, that all the rows for `frequency` inside `frequencies.csv` follow this approach)


License
-------

![GNU GPLv3 Image](https://www.gnu.org/graphics/gplv3-127x51.png)

This program is Free Software: You can use, study share and improve it at your
will. Specifically you can redistribute and/or modify it under the terms of the
[GNU General Public License](https://www.gnu.org/licenses/gpl.html) as
published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
