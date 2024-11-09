#!/bin/bash

# nice oneliner for buiding the app on mac
# run this from reed_reviewer_app

pyinstaller --icon './app_images/oboeapp.icns' \
    --onefile \
    --windowed \
    --add-binary './portaudio-binaries/libportaudio.dylib:.' \
    --name 'Reed Tracker' \
    entry_point.py
