# using image that includes python 3.6  and node 9.11.1
FROM gabrielfalcao/alpine37-python3-node9111

#              _   _                       _ _       _
#             | | | |                     | (_)     (_)
#  _ __  _   _| |_| |__   ___  _ __    ___| |_ _ __  _  ___
# | '_ \| | | | __| '_ \ / _ \| '_ \  / __| | | '_ \| |/ __|
# | |_) | |_| | |_| | | | (_) | | | || (__| | | | | | | (__
# | .__/ \__, |\__|_| |_|\___/|_| |_(_)___|_|_|_| |_|_|\___|
# | |     __/ |
# |_|    |___/

LABEL maintainer="Gabriel Falcão"

EXPOSE  80

VOLUME ["/python-clinic/databases", "/python-clinic/logs"]


ENV PYTHONPATH       /python-clinic/src:$PYTHONPATH

ENV PYTHON_CLINIC_LOGLEVEL                       DEBUG
ENV PYTHON_CLINIC_CONF_PATH                      /python-clinic./config/python-clinic.yaml
ENV PYTHON_CLINIC_GENERATE_DOCS                  true

RUN mkdir -p \
    /python-clinic/config \
    /python-clinic/databases \
    /python-clinic/logs \
    /python-clinic/src

WORKDIR /python-clinic/src
COPY . /python-clinic/src

RUN cp -f /python-clinic/src/container/config/* /python-clinic/config/
RUN pipenv install --skip-lock --dev -r development.txt
RUN pipenv install --skip-lock -r requirements.txt
RUN pipenv run python setup.py install

RUN find /python-clinic/src/container/fs -exec touch {} \; && rsync -putavoz /python-clinic/src/container/fs/ /

CMD gunicorn -c /python-clinic/config/gunicorn.conf -b 0.0.0.0:80 python_clinic:application

ENTRYPOINT ["pipenv", "run"]
