FROM jess/pulseaudio

LABEL maintainer="dud1337 <grant@dud.li>"

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
EXPOSE 8080

# Install VLC, Pulse Audio, nginx, and supervisor
RUN apt update && apt install -y vlc python3-pip nginx supervisor

# Prepare base directory
RUN mkdir /fm

# Python 3 depenendcies
COPY requirements.txt /fm/requirements.txt
RUN python3 -m pip install -r /fm/requirements.txt --break-system-packages

# Provide morphovum source code
ADD src /fm/src
COPY res/MorphOvum.gif /fm/src/www/MorphOvum.gif

# Copy nginx and supervisor configurations from src/confs
COPY src/confs/nginx.conf /etc/nginx/nginx.conf
COPY src/confs/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Prepare subdirectories
RUN mkdir /fm/ambience /fm/clips /fm/music /fm/playlists /fm/conf
RUN chown pulseaudio:pulseaudio -R /fm \
	&& chmod 775 -R /fm

# Sync time
RUN date

# Create log directories for supervisor
RUN mkdir -p /var/log/supervisor /var/log/nginx

# Set working directory
WORKDIR "/fm/src"

# Use supervisor to manage all services (nginx, pulseaudio, morphovum)
ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
