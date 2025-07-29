test:
	python runtests.py

testc:
	coverage run runtests.py
	coverage report -m

clean:
	rm -rf dist
	rm -rf django_wikiwikiweb.egg-info

build: clean
	python -m build

publish: build
	twine upload dist/*

