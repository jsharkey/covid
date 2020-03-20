#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
    Copyright 2020, Jeff Sharkey

    Licensed under the Apache License, Version 2.0 (the "License"); 
    you may not use this file except in compliance with the License. 
    You may obtain a copy of the License at 

        http://www.apache.org/licenses/LICENSE-2.0 

    Unless required by applicable law or agreed to in writing, software 
    distributed under the License is distributed on an "AS IS" BASIS, 
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
    See the License for the specific language governing permissions and 
    limitations under the License.
'''

import sys
import csv
import numpy as np
import datetime
import collections
import numpy

from matplotlib import pyplot as plt

# path to latest local copy of https://github.com/CSSEGISandData/COVID-19
if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = "../COVID-19/"

fig = plt.figure(num=None, figsize=(8, 4), dpi=200, facecolor='w', edgecolor='k')

start = datetime.datetime.strptime("1/1/20", "%m/%d/%y")
x_data_ext = np.array(range(60, 100))

def plot(country=lambda c: True, state=lambda s: True, color=None, label=None):
    res = collections.defaultdict(lambda: 0)

    with open("%s/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv" % (path)) as f:
        r = csv.DictReader(f)
        for row in r:
            if not country(row["Country/Region"]): continue
            if not state(row["Province/State"]): continue

            # ignore cities, counties
            if ", " in row["Province/State"]: continue
            if "Princess" in row["Province/State"]: continue

            for k, v in row.iteritems():
                try:
                    k = (datetime.datetime.strptime(k, "%m/%d/%y") - start).days
                    v = int(v)
                    if v > 0 and k >= 60:
                        res[k] += v
                except ValueError:
                    continue

    x_data = np.array(sorted(res.keys()))
    y_data = np.array([res[k] for k in x_data])

    log_x_data = np.log(x_data)
    log_y_data = np.log(y_data)

    curve_fit = np.polyfit(x_data, log_y_data, 2)

    det = 0
    if True:
        x = x_data
        y = log_y_data
        p = numpy.poly1d(curve_fit)
        yhat = p(x)
        ybar = numpy.sum(y)/len(y)
        ssreg = numpy.sum((yhat-ybar)**2)
        sstot = numpy.sum((y - ybar)**2)
        det = ssreg / sstot

    print(curve_fit)

    #y = np.exp(curve_fit[0]*x_data_ext) * np.exp(curve_fit[1])
    y = np.exp(curve_fit[0]*x_data_ext*x_data_ext) * np.exp(curve_fit[1]*x_data_ext) * np.exp(curve_fit[2])

    plt.plot(x_data, y_data, "%so" % (color))
    plt.plot(x_data_ext, y, color, label=u"%s [r\u00B2=%0.2f]" % (label, det))

plot(country=lambda c: c == "US", state=lambda s: s == "Colorado",   color="C0", label="Colorado")
plot(country=lambda c: c == "US", state=lambda s: s == "Minnesota",  color="C1", label="Minnesota")
plot(country=lambda c: c == "US", state=lambda s: s == "California", color="C2", label="California")
plot(country=lambda c: c == "US", state=lambda s: s == "New York",   color="C3", label="New York")

plot(country=lambda c: c == "US",                                    color="k",  label="US")
plot(country=lambda c: c == "Italy",                                 color="C7", label="Italy")

plt.xticks(x_data_ext, [ datetime.datetime.strftime(start+datetime.timedelta(d), "%m-%d") for d in x_data_ext ], rotation=90)
plt.yscale("log")
plt.legend(loc="lower right")

plt.grid(axis="both")
plt.title("COVID-19 Regression Analysis\nhttps://github.com/jsharkey/covid, Johns Hopkins CSSE")
plt.ylim(bottom=0)

plt.show()


