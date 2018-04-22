all: deps build

node_modules:
	npm install

build: node_modules
	@npm run build
	@git add -f build/static/*
	@git status build/static


deps: node_modules

run:
	npm start

start: node_modules
	npm run $@

test: node_modules
	npm run test tests/utils/filter_by.spec.js

loop-run:
	@while true; do npm i && npm start; done

.PHONY: all deps build
