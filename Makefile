.PHONY: dev check verify

dev:
	DOCS7_RENDERER_VERSION=0.1.9 npx --yes @upstash/docs7@0.1.1 dev .

check:
	python3 scripts/check-docs.py

verify:
	python3 scripts/check-docs.py --url http://localhost:3333
