FROM jess/pulseaudio

MAINTAINER Dudley Grant <grant@dud.li>

USER root
EXPOSE 8138 8139

# VLC & Pulse Audiot
RUN apt update && apt install -y vlc python3-pip

# Prepare base directory
RUN mkdir /fm
# Python 3 depenendcies
COPY requirements.txt /fm/requirements.txt
RUN pip install -r /fm/requirements.txt

# provide morphovum source code
ADD src /fm/src

RUN mkdir /fm/ambience /fm/clips /fm/music /fm/playlists
RUN chown pulseaudio:pulseaudio -R /fm \
	&& chmod 775 -R /fm
RUN date

USER pulseaudio
WORKDIR "/fm/src"
ENTRYPOINT pulseaudio -D \
	&& pacmd load-module module-null-sink sink_name=virtual sink_properties=device.description=virtual \
	&& pacmd set-default-sink virtual \
	&& python3 main.py
