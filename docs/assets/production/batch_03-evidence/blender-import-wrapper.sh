#!/bin/sh
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy exec /usr/bin/blender -noaudio "$@"
