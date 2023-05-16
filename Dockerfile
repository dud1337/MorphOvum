FROM jess/pulseaudio

MAINTAINER dud1337 <grant@dud.li>

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
EXPOSE 8138 8139 8140

# Install VLC & Pulse Audio
RUN apt update && apt install -y vlc python3-pip

# Prepare base directory
RUN mkdir /fm

# Python 3 depenendcies
COPY requirements.txt /fm/requirements.txt
RUN python3 -m pip install -r /fm/requirements.txt --break-system-packages

# Provide morphovum source code
ADD src /fm/src
COPY res/MorphOvum.gif /fm/src/www/MorphOvum.gif

# Prepare subdirectories
RUN mkdir /fm/ambience /fm/clips /fm/music /fm/playlists /fm/conf
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
	&& sed -i -r "s/changeme/$MORPH_OVUM_PASSWORD/g" /fm/src/default-config.yaml \
	&& python3 main.py -c /fm/conf/config.yaml
