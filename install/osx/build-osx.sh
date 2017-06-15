#!/usr/bin/env bash

if [[ $# -eq 0 ]] ; then
    echo 'Please specify version number. usage: build-osx.sh x.y.z'
    exit 1
fi

#Cleanup possible previous builds
rm -rf RaceCapture.app
rm -rf Kivy.App
rm RaceCapture*.dmg

DIR=$( cd ../.. && pwd )

#Kivy's build/packaging tools expect the Kivy app here
if [ ! -f "./Kivy.App" ]; then
	cp -a /Applications/Kivy.app ./Kivy.App
fi

./package-app.sh "$DIR/"

#Use Kivy's 'cleanup app' script
./cleanup_app.sh RaceCapture.app

#Cleanup SDL2
find RaceCapture.app/Contents/Frameworks  -name "Current" | xargs rm -rf

#Cleanup source files
echo "-- Remove all py/pyc"
find -E RaceCapture.app -regex ".*pyc?$" -exec rm {} \;

#Customizations and file size savings
rm -rf RaceCapture.app/Contents/Frameworks/GStreamer.framework
rm -rf RaceCapture.app/Contents/Resources/kivy/examples
rm -rf RaceCapture.app/Contents/Resources/kivy/doc
rm -rf RaceCapture.app/Contents/Resources/kivy/.git
rm -rf RaceCapture.app/Contents/Resources/yourapp/.buildozer
rm -rf RaceCapture.app/Contents/Resources/yourapp/bin
rm -rf RaceCapture.app/Contents/Resources/kivy_stable
rm -rf RaceCapture.app/Contents/Resources/venv/lib/python2.7/site-packages/kivy
rm -rf RaceCapture.app//Contents/Resources/venv/share

#We have to customize their theme so checkboxes show up
cp ../../data/images/defaulttheme-0.png RaceCapture.app/Contents/Resources/kivy/kivy/data/images/
cp ../../data/images/defaulttheme.atlas RaceCapture.app/Contents/Resources/kivy/kivy/data/images/

#Custom icon
cp racecapture.icns RaceCapture.app/Contents/Resources/appIcon.icns

#Customize plist so our name and info shows up
cp Info.plist RaceCapture.app/Contents/

./create-osx-dmg.sh RaceCapture.app

#Rename the file to include the version
echo "-- Rename dmg to include provided version number"
mv RaceCapture.dmg RaceCapture_${1}.dmg
