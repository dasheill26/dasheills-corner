run:
\tpython main.py

test:
\tpytest -q

test-verbose:
\tpytest -vv

freeze:
\tpip freeze > requirements.txt
