# python-polarion

This package allows access to a Polarion server.
Note that this is the first release and that updates will change the interface in the near future.

# Examples
Documentation is lacking in this test release, so here are some snippets to get you going.

Creating the Polarion client:

```python
client = polarion.Polarion('http://example.com/polarion', 'user', 'password')
```

Opening a project using the project name:
```python
project = client.getProject('Python')
```

Load a workitem:
```python
workitem = project.getWorkitem('PYTH-510')
```

Modify a workitem:
```python
x = workitem.getVailableActions() # x will be an array of actions
workitem.preformAction(x[1])
```
or:
```python
x = workitem.getVailableStatus() #this forces the new state ignoring any rules set in Polarion
workitem.setStatus(x[1])
```
or:
```python
workitem.setDescription('Some description..')
workitem.addComment('test comment', 'sent from Python')
workitem.addHyperlink('google.com', workitem.HyperlinkRoles.EXTERNAL_REF)
```
Getting options for this type of workitem:
```python
workitem.getResolutionEnum() # these return an empty array of no workitem specific options are set
workitem.getSeverityEnum()
workitem.getStatusEnum()
```
You can modify any property and call the save method. Some require a certain structure, which methods like setDescription handle for you, not adhering to it will cause an exception.

Load a test run:
```python
run = project.getTestRun('SWQ-0001')
```
or
```python
runs = project.searchTestRuns('SWQ*') #this is a query and will work the same as in Polarion
```

Modifying a test record:
Load a workitem:
```python
run = project.getTestRun('SWQ-0001')
run.records[0].setResult(record.Record.ResultType.PASSED, ' Comment with test result')
```

# Known issues or missing features
No way of knowing the test run possible statuses.


