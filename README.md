# python-polarion

This package allows access to a Polarion server.
Note that this is the first release and that updates will change the interface in the near future.

# Installation

```
pip install polarion
```

# Getting started

Creating the Polarion client and getting workitems or test runs:

```python
from polarion import polarion
client = polarion.Polarion('http://example.com/polarion', 'user', 'password')
project = client.getProject('Python')
workitem = project.getWorkitem('PYTH-510')
run = project.getTestRun('SWQ-0001')
```


More examples to be found in the quick start section of the documentation.
[Go to the documentation](https://python-polarion.readthedocs.io/en/latest/index.html)

# Known issues or missing features
No way of knowing the test run possible statuses.
Sessions not being checked on validity
No access to the live docs


