# INSTRUCTION arguments
# Tells Docker to interpret code as Python
FROM python:3
# will set the env variable to ensure python output stdout stderr streams are sent straight to terminal
# no buffer to time to show up in terminal
ENV PYTHONUNBUFFERED 1
# sets the working directory for any command that you use
WORKDIR /app
# copies requirements.txt over to WORKDIR
COPY . .
# install all requirements that are copied over to requirements.txt
RUN pip install -r requirements.txt
# runs server at localhost (port is optional)
CMD gunicorn --bind 0.0.0.0:8000 conference_go.wsgi
