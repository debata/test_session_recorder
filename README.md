# Test Session Recorder
Simple command line tool to record findings during a exploratory test sessions

# Installation

This package can be installed directly from the Python Package Index by executing:

```
pip install test_session
```

**Note:** Installation may require root privileges

Once successfully installed, you can start the application by executing ```testrecorder```.  The 
application will start and display: 
```
                           Test Session Recorder
==========================================================================
```

# Commands

Using the ```help``` command will display all supported commands:
```
>> help

Documented commands (type help <topic>):
========================================
delete  help  list  new  open  quit  report  show
```

Using ``` help <command>``` will display a description for the given command. Eg:
```
>> help list
list
        List all test sessions
```

Similarly, when a session has started, the ```help``` command will display all in-sesssion commands as well. Eg:

```
>> new TestSession
Session Started: TestSession
====================================================================================
SESSION >> help
Available session commandsbug  
mission  
timebox  
pause  
duration  
undo  
areas  
screenshot  
help
SESSION >> help duration
duration 
        Show the current session duration
SESSION >> duration
Duration: 0:00:16
```



