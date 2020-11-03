# FROM command tells docker what "image" is to be used.
FROM python:3.9-alpine
# MAINTAINER is just a name to take note whos coding

# This line of code is just to avoid any complications when running python apps on docker
ENV PYTHONUNBUFFERED 1
# ./requirements.txt refers to our current directory. Itll copy that into docker's own 
COPY ./requirements.txt /requirements.txt
# RUN is basically a command we want to fire to docker
RUN pip install -r /requirements.txt
# ./app refers to our APP and /app refers to dockers /app that we denoted with mkdir
RUN mkdir /app
WORKDIR /app
COPY ./app /app
# the adduser command with "-D" tells docker that we're making a user named "user" and thisll be an account for the application only. note that its not glbal
RUN adduser -D user
# swap to the user we created
USER user