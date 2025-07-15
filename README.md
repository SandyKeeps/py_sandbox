# Py Sandbox
This library is a framework for running untrusted python. 
## Command line usage:
Install Using pip
```
pip install .
```
Use the Interpriter:
```
$ py_sandbox -i
sandbox$ 
```
Takes in strings
```
$ py_sandbox "print('Hello World')"
$ Hello World
```

## How to controll sandbox settings
Use configuration files that specify what is allowed and what is not allowed.


## Todo
- multiline repl
- take in files from command line
