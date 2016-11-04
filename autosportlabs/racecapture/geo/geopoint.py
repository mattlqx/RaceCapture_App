#
# Race Capture App
#
# Copyright (C) 2014-2016 Autosport Labs
#
# This file is part of the Race Capture App
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details. You should
# have received a copy of the GNU General Public License along with
# this code. If not, see <http://www.gnu.org/licenses/>.

import math
RADIUS_EARTH_KM = 6371

class GeoPoint:
    """
    Represents the concept of a Geographic point.
    """
    def __init__(self, **kwargs):
        self.latitude = 0
        self.longitude = 0

    @classmethod
    def fromPoint(cls, latitude, longitude):
        """
        Factory to create a GeoPoint from the specified point
        :param latitude
        :type  latitude float
        :param longitude
        :type longitude float
        :returns the new instance
        :type GeoPoint
        """
        if latitude is None or longitude is None:
            raise ValueError("Latitude and Longitude must be provided")
        g = GeoPoint()
        g.latitude = latitude
        g.longitude = longitude
        return g

    @classmethod
    def is_valid(cls, point):
        return (point is not None and
                 point.latitude is not None and
                 point.longitude is not None and
                 point.latitude != 0 and
                 point.longitude != 0)

    @classmethod
    def fromPointJson(cls, geoPointJson):
        g = None
        if geoPointJson:
            g = GeoPoint()
            g.latitude = geoPointJson[0]
            g.longitude = geoPointJson[1]
        return g

    @classmethod
    def from_string(cls, point_string):
        """
        Construct a GeoPoint from a formatted latitude,longitude string
        @param point_string - latitude,longitude
        @type point_string string
        @return GeoPoint
        """
        try:
            lat_lon = point_string.split(',')
            lat = float(lat_lon[0])
            lon = float(lat_lon[1])
            g = GeoPoint()
            g.latitude = lat
            g.longitude = lon
            return g
        except (ValueError, IndexError) as e:
            raise Exception('GeoPoint: Invalid point string specified {} {}'.format(point_string, e))

    def __str__(self):
        return '{},{}'.format(self.latitude, self.longitude)

    def fromJson(self, geoPointJson):
        try:
            self.latitude = geoPointJson[0]
            self.longitude = geoPointJson[1]
        except:
            print('Malformed GeoPoint: ' + str(geoPointJson))

    def toJson(self):
        return [self.latitude, self.longitude]


    def withinCircle(self, point, radiusDeg):
        rSquared = radiusDeg * radiusDeg
        xdelta = point.longitude - self.longitude
        ydelta = point.latitude - self.latitude
        dsquared = (xdelta * xdelta) + (ydelta * ydelta)
        return rSquared >= dsquared


    def metersToDegrees(self, meters, bearingAngle):
        d = meters / 1000.0
        R = RADIUS_EARTH_KM
        brng = math.radians(bearingAngle)

        lat1 = self.latitude
        lon1 = self.longitude

        lat2 = math.degrees((d / R) * math.cos(brng)) + lat1
        lon2 = math.degrees((d / (R * math.sin(math.radians(lat2)))) * math.sin(brng)) + lon1

        distanceDegrees = math.fabs(math.sqrt(math.pow((lat1 - lat2), 2) + math.pow((lon1 - lon2), 2)))
        return distanceDegrees

    def dist_pythag(self, other_geopoint):
        """
         Finds the distance between the two geopoints using the
         basic Pythagoras' Theorem.  This is only useful for small distances as
         the inaccuracies will increase as the distance does.  However this is
         also one of the fastest methods of calculating this distance.
         :param other_geopoint - the other point to calculate distance from
         :return The distance between the two points in Meters
         """
        d_lat_rad = math.radians(other_geopoint.latitude - self.latitude)
        d_lon_rad = math.radians(other_geopoint.longitude - self.longitude)
        lat_a_rad = math.radians(self.latitude)
        lat_b_rad = math.radians(other_geopoint.latitude)
        tmp = d_lon_rad * math.cos((lat_a_rad + lat_b_rad) / 2)
        return math.sqrt(tmp * tmp + d_lat_rad * d_lat_rad) * (RADIUS_EARTH_KM * 1000.0)

class Region:
    name = None
    points = None
    def __init__(self, **kwargs):
        self.points = []
        self.name = ''
    def fromJson(self, regionJson):
        self.name = regionJson.get('name', self.name)
        pointsNode = regionJson.get('points')
        if pointsNode:
            for pointNode in pointsNode:
                p = GeoPoint()
                p.fromJson(pointNode)
                self.points.append(p)

    def toJson(self):
        pass

    def withinRegion(self, geoPoint):
        inside = False
        if geoPoint:
            n = len(self.points)
            y = geoPoint.latitude
            x = geoPoint.longitude
            firstPoint = self.points[0]
            p1x = firstPoint.longitude
            p1y = firstPoint.latitude
            for i in range(n + 1):
                pt = self.points[i % n]
                p2x = pt.longitude
                p2y = pt.latitude
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xints:
                                inside = not inside
                p1x, p1y = p2x, p2y
        return inside
