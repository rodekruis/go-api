FROM python:3.6.3-jessie

EXPOSE 2222 80

RUN \
	apt-get update; \
	apt-get install -y nginx postgresql-client mdbtools vim; \
	apt-get install -y cron --no-install-recommends; \
        apt-get install -y --no-install-recommends openssh-server; \
        echo "root:Docker!" | chpasswd; \
        rm -rf /var/lib/apt/lists*; \
        apt-get clean

COPY sshd_config /etc/ssh/

ENV HOME=/home/ifrc
WORKDIR $HOME

COPY requirements.txt $HOME/requirements.txt
RUN \
	pip install gunicorn; \
	pip install -r requirements.txt

COPY main/nginx.conf /etc/nginx/sites-available/
RUN \
	ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled; \
	echo "daemon off;" >> /etc/nginx/nginx.conf

COPY main/runserver.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/runserver.sh

COPY ./ $HOME/go-api/
WORKDIR $HOME/go-api/

RUN service ssh start
CMD "/usr/local/bin/runserver.sh"