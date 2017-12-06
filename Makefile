publish:
	rm -fr build dist .egg requests.egg-info
	pip install 'twine>=1.5.0'
	python setup.py sdist
	python setup.py bdist_wheel --universal
	twine upload dist/*
	rm -fr build dist .egg requests.egg-info
