from .user import UserCreator
from .testrun import TestrunCreator
from .workitem import WorkitemCreator
from .factory import addCreator
from .document import DocumentCreator

addCreator('workitem', WorkitemCreator)
addCreator('testrun', TestrunCreator)
addCreator('user', UserCreator)
addCreator('module', DocumentCreator)
