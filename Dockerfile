FROM jess/pulseaudio

MAINTAINER Dudley Grant <grant@dud.li>

#            █████            
#         ███     ███         
#       ███         ███       
#     ███             ███     
#   ███                 ███   
#  ██   ┌┬┐┌─┐┬─┐┌─┐┬ ┬   ██  
#██     ││││ │├┬┘├─┘├─┤     ██
#██     ┴ ┴└─┘┴└─┴  ┴ ┴     ██
#███      _      ._ _      ███
#  ███   (_)\/|_|| | |   ███  
#    ███               ███    
#       ███         ███       
#          █████████          
#

USER root
EXPOSE 8138 8139

# Install VLC & Pulse Audio
RUN apt update && apt install -y vlc python3-pip

# Prepare base directory
RUN mkdir /fm

# Python 3 depenendcies
COPY requirements.txt /fm/requirements.txt
RUN pip install -r /fm/requirements.txt

# Provide morphovum source code
ADD src /fm/src

# Prepare subdirectories
RUN mkdir /fm/ambience /fm/clips /fm/music /fm/playlists
RUN chown pulseaudio:pulseaudio -R /fm \
	&& chmod 775 -R /fm

# Sync time
RUN date

# Switch user, prepare Pulse Audio virtual sink, set admin pw, and run Morph Ovum
USER pulseaudio
WORKDIR "/fm/src"
ENTRYPOINT pulseaudio -D \
	&& pacmd load-module module-null-sink sink_name=virtual sink_properties=device.description=virtual \
	&& pacmd set-default-sink virtual \
	&& sed -i -r "s/changeme/$MORPHOVUM_PASSWORD/g" /fm/src/config.yaml \
	&& python3 main.py

