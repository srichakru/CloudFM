FROM python:3.7

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY src/requirements.txt ./

# Install production dependencies.
RUN pip install -r requirements.txt

RUN mkdir -p /etc \
    && mkdir -p /etc/apt
RUN apt-get update -y && apt-get install -y jq bc vim tcpdump

COPY src /app
EXPOSE 6010-6099
# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD ["python", "/app/huawei-ows-http-collect.py"]
