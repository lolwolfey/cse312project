# FROM python:3.7.4

# ENV HOME /root
# WORKDIR /root

# COPY . .

# EXPOSE $PORT

# RUN pip3 install -r requirements.txt

# CMD export FLASK_APP=app && flask run --port=$PORT --host=0.0.0.0


FROM python:3.9

ENV HOME /root
WORKDIR /root

COPY . . 

RUN pip3 install pymongo
RUN pip3 install flask
RUN pip3 install psycopg2-binary
RUN pip3 install Flask-Login
RUN pip3 install Flask-Migrate
RUN pip3 install requests==2.26.0
EXPOSE 8080
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

# CMD python3 server.py
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

