#!/bin/bash
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


set -e
rm -rf bin
python -m build_tools.build_default_tracks
cp data/images/defaulttheme-0.png .buildozer/android/platform/python-for-android/dist/racecapture/private/lib/python2.7/site-packages/kivy/data/images/defaulttheme-0.png
cp data/images/defaulttheme-0.png .buildozer/android/platform/python-for-android/dist/racecapture/python-install/lib/python2.7/site-packages/kivy/data/images/defaulttheme-0.png
buildozer -v android release
APK=$(ls bin/*.apk)
RELEASE_APK="${APK/unsigned/signed}"
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore $1 -storepass $2 $APK rcpmobile
ZA=`find ~/.buildozer/ -name zipalign -print -quit`
$ZA -f 4 $APK $RELEASE_APK
