#!/bin/bash

is_pulseaudio_running() {
    pgrep pulseaudio > /dev/null
}

# Start PulseAudio if it's not running
if ! is_pulseaudio_running; then
    echo "Starting PulseAudio..."
else
    echo "PulseAudio is already running."
fi

rm -rf /var/run/pulse /var/lib/pulse /home/pulseaudio/.config/pulse
# See https://superuser.com/questions/1539634/pulseaudio-daemon-wont-start-inside-docker/1545361#1545361
pulseaudio -D

pacmd load-module module-null-sink sink_name=virtual sink_properties=device.description=virtual
pacmd set-default-sink virtual
sed -i -r "s/changeme/$MORPH_OVUM_PASSWORD/g" /fm/src/default-config.yaml

python3 main.py -c /fm/conf/config.yaml
