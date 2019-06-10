# Conifer Development Guide


## Environment setup and Testing

Conifer supports Python 2.7 and Python 3.6 - you should have both of these in your environment for testing.

Virtualenv is recommended for interactive testing, but `tox` is required for automated test coverage.


```bash
virtualenv ~/.virtualenvs/conifer
source ~/.virtualenvs/conifer/bin/activate

pip install -e .[test]

tox
```
