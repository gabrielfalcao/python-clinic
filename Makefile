# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  _         _ _    _
# | |__ _  _(_) |__| |
# | '_ \ || | | / _` |
# |_.__/\_,_|_|_\__,_|
#               _      _    _
# __ ____ _ _ _(_)__ _| |__| |___ ___
# \ V / _` | '_| / _` | '_ \ / -_|_-<
#  \_/\__,_|_| |_\__,_|_.__/_\___/__/
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# change at your own peril:
# .........................
host			:= 0.0.0.0
port			:= 4242
types			:= unit functional
sed			:= $(shell which gsed || which sed)
example_config		:= example/config.yaml
docker_image		:= docker.python.clinic/website:latest
docker_run		:= docker run --rm -p 4242:80 \
				-v `pwd`/container/databases:/python-clinic/databases \
				-v `pwd`/container/config:/python-clinic/config \
				-v `pwd`:/python-clinic/logs \
				-v `pwd`:/tmp -ti $(docker_image)


#              _                            _
#  ___ _ ___ _(_)_ _ ___ _ _  _ __  ___ _ _| |_
# / -_) ' \ V / | '_/ _ \ ' \| '  \/ -_) ' \  _|
# \___|_||_\_/|_|_| \___/_||_|_|_|_\___|_||_\__|
#               _      _    _
# __ ____ _ _ _(_)__ _| |__| |___ ___
# \ V / _` | '_| / _` | '_ \ / -_|_-<
#  \_/\__,_|_| |_\__,_|_.__/_\___/__/
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
export PYTHONDONTWRITEBYTECODE		:= 1  # prevents annoying __pycache__ generation
export PYTHON_CLINIC_CONF_PATH	:= $(example_config)
export NODE_ENV				:= production
export NODE_PATH			:= $(shell pwd)/frontend/admin-app/src:$(shell pwd)/frontend/admin-app/node_modules


#    ___      _____
#   /_\ \    / / __|
#  / _ \ \/\/ /\__ \
# /_/ \_\_/\_/ |___/
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ensure that no real AWS profiles
# are used during tests
# ................................
unexport AWS_PROFILE
unexport AWS_DEFAULT_REGION

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------



#  ____  _    _ _____ _      _____    _______       _____   _____ ______ _______ _____
# |  _ \| |  | |_   _| |    |  __ \  |__   __|/\   |  __ \ / ____|  ____|__   __/ ____|
# | |_) | |  | | | | | |    | |  | |    | |  /  \  | |__) | |  __| |__     | | | (___
# |  _ <| |  | | | | | |    | |  | |    | | / /\ \ |  _  /| | |_ |  __|    | |  \___ \
# | |_) | |__| |_| |_| |____| |__| |    | |/ ____ \| | \ \| |__| | |____   | |  ____) |
# |____/ \____/|_____|______|_____/     |_/_/    \_\_|  \_\\_____|______|  |_| |_____/
# .....................................................................................
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV


#  ___  ___ ___ _  _   _ _  _____
# |   \| __| __/_\| | | | ||_   _|
# | |) | _|| _/ _ \ |_| | |__| |
# |___/|___|_/_/ \_\___/|____|_|
#  _____ _   ___  ___ ___ _____
# |_   _/_\ | _ \/ __| __|_   _|
#   | |/ _ \|   / (_ | _|  | |
#   |_/_/ \_\_|_\\___|___| |_|
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
all: environment unit docs


#  _    ___   ___   _   _
# | |  / _ \ / __| /_\ | |
# | |_| (_) | (__ / _ \| |__
# |____\___/ \___/_/ \_\____|
#  _  _   _ _____ _____   _____
# | \| | /_\_   _|_ _\ \ / / __|
# | .` |/ _ \| |  | | \ V /| _|
# |_|\_/_/ \_\_| |___| \_/ |___|
#  ___ _  ___   _____ ___  ___  _  _ __  __ ___ _  _ _____
# | __| \| \ \ / /_ _| _ \/ _ \| \| |  \/  | __| \| |_   _|
# | _|| .` |\ V / | ||   / (_) | .` | |\/| | _|| .` | | |
# |___|_|\_| \_/ |___|_|_\\___/|_|\_|_|  |_|___|_|\_| |_|
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tests: check-deps lint $(types)

$(types):
	PYTHON_CLINIC_CONF_PATH=tests/$@/$@-test-config.yaml pipenv run nosetests ./tests/$@

environment: dependencies develop

check-deps:
	@(which pipenv >/dev/null 2>&1) || (echo -e "First, please install pipenv:\n'pip install pipenv'" && exit 1)

develop:
	pipenv run python setup.py develop

dependencies: check-deps
	pipenv install --dev --skip-lock

html-docs: develop
	PYTHON_CLINIC_GENERATE_DOCS=true make functional html-docs-only

html-docs-only:
	cp -f example/config.yaml ./docs/source/_static/example-config.yaml
	cd docs && pipenv run make html
	rsync -putaoz docs/build/html/ python_clinic/docs/

docs: html-docs
	open docs/build/html/index.html

js:
	(cd frontend/admin-app && make test build)
	git add -f frontend/admin-app/build/static/*

release: unit functional html-docs
	@rm -rf dist build
	@pipenv run python setup.py build sdist

clean:
	@rm -rf `find . -type d -name '__pycache__'`
	@find . -type f -name '*.pyc' -delete
	@rm -rf python_clinic.egg-info build dist docs/build

run:
	reset && pipenv run python-clinic web --debug --port=$(port) --host=$(host)



#  _____ ___   ___  _    ___
# |_   _/ _ \ / _ \| |  / __|
#   | || (_) | (_) | |__\__ \
#   |_| \___/ \___/|____|___/
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ngrok:
	ngrok start python_clinic

tunnel-run: docker-image

gunicorn:
	gunicorn -c gunicorn.conf -b 0.0.0.0:4242 python_clinic.web:application

notify:
	@osascript -e 'display notification "target completed $(MAKECMDGOALS)" with title "Python Clinic Makefile"'
	@say "I am done with the makefile target \"$(MAKECMDGOALS)\""

shell:
	pipenv run ipython

lint:
	pipenv run flake8 python_clinic tests

aws-tail-logs:
	AWS_PROFILE=develop_devops awslogs get /ecs/python-clinic '.*' --start='30m ago' -w -G  --timestamp



#  ___   ___   ___ _  _____ ___
# |   \ / _ \ / __| |/ / __| _ \
# | |) | (_) | (__| ' <| _||   /
# |___/ \___/ \___|_|\_\___|_|_\
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# run tests, build docs and the react app prior to building docker image
# ......................................................................

docker-image: lint develop unit html-docs docker-image-only

docker-push:
	@printf "\033[38;5;197m$$(figlet PENDING TASK)\033[0m\n"
	@printf "\033[38;5;176mcreate ECS-like deploy on DO\033[0m\n"

docker-image-only:
	docker build . -t $(docker_image)

docker-tests:
	$(docker_run) make lint unit functional

docker-build-documentation:
	$(docker_run) make html -C docs

docker-web:
	$(docker_run)

docker-shell:
	$(docker_run) bash

docker-release: docker-image docker-push notify

docker: docker-image docker-tests docker-build-documentation docker-web
deploy-to-ecs: release docker-image docker-push notify




#   ___ ___  _  _ _____ ___ _  _ _   _  ___  _   _ ___
#  / __/ _ \| \| |_   _|_ _| \| | | | |/ _ \| | | / __|
# | (_| (_) | .` | | |  | || .` | |_| | (_) | |_| \__ \
#  \___\___/|_|\_| |_| |___|_|\_|\___/ \___/ \___/|___/
#
#  ___ _  _ _____ ___ ___ ___    _ _____ ___ ___  _  _
# |_ _| \| |_   _| __/ __| _ \  /_\_   _|_ _/ _ \| \| |
#  | || .` | | | | _| (_ |   / / _ \| |  | | (_) | .` |
# |___|_|\_| |_| |___\___|_|_\/_/ \_\_| |___\___/|_|\_|
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

init: docker-image-only
test: docker-tests


#  ___  ___ ___ _    _____   ____  __ ___ _  _ _____
# |   \| __| _ \ |  / _ \ \ / /  \/  | __| \| |_   _|
# | |) | _||  _/ |_| (_) \ V /| |\/| | _|| .` | | |
# |___/|___|_| |____\___/ |_| |_|  |_|___|_|\_| |_|


deploy: clean
	ansible-playbook -vvvv -i provisioning/inventory provisioning/playbook.yml
	make online-check


vault-edit:
	ansible-vault edit provisioning/python-clinic-vault.yml

provision: clean
	ansible-playbook -i provisioning/inventory provisioning/playbook.yml
	ssh root@python.clinic /etc/cron.weekly/dehydrated


#  ___   _ _____ _   ___   _   ___ ___ ___
# |   \ /_\_   _/_\ | _ ) /_\ / __| __/ __|
# | |) / _ \| |/ _ \| _ \/ _ \\__ \ _|\__ \
# |___/_/ \_\_/_/ \_\___/_/ \_\___/___|___/


db: drop-db
	@echo "CREATE DATABASE IF NOT EXISTS pythonclinic" | mysql -uroot
	pipenv run alembic upgrade head

drop-db:
	@echo "DROP DATABASE IF EXISTS pythonclinic" | mysql -uroot


.PHONY: docs tests $(types) provisioning
