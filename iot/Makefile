.PHONY: clean all

all: config/template.json

config/template.json: template.json .env
	env $$(cat .env | xargs) envsubst '$$BRAIN,$$ACR,$$USERNAME,$$PASSWORD' < $< > $@;

deploy: config/template.json
	az iot edge set-modules --hub-name advo-iot-hub --device-id m002 --content $<

clean:
	@rm -rf config/template.json
