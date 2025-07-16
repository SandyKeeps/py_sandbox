# Py Sandbox
Py Sandbox is a framework for running untrusted Python code. 

## What is a Code Sandbox?

A code sandbox is an isolated environment where code can be executed safely without affecting the host system. It is particularly useful for running untrusted code, as it restricts the code's access to the system's resources, preventing potential security risks such as unauthorized data access or system damage. By using a sandbox, developers can test and execute code snippets with confidence, knowing that any malicious or harmful actions are contained within the sandbox environment. Within py_sandbox code that is identified as harmful via a declared ruleset in a yaml file is systematically removed and alerted back to the developers. 

## How Py Sandbox Works

Py Sandbox operates by creating a controlled environment where Python code can be executed with limited permissions. It uses configuration files to specify what operations are allowed and which are restricted. This ensures that potentially harmful actions, such as file system access or network requests, are blocked unless explicitly permitted. When those actions are tried then the sandbox has an alerting system, which can be configured for the popular monitoring systems. 


### Code Analysis

Py Sandbox utilizes Python's Abstract Syntax Tree (AST) to perform code analysis, identifying potentially malicious code patterns. The analysis is guided by a YAML configuration file that specifies rules and patterns to look for. When a match is found, the sandbox blocks execution of the harmful code and alerts the user. The non harmful parts of the code continue to be run, so core logic of the task continue to be executed.

This approach allows Py Sandbox to detect and neutralize threats before the code is executed, providing an additional layer of security. By leveraging the AST, the sandbox can understand the structure of the code and make informed decisions about its security posture.

### Traditional Sandbox Security Measures that should be hardened around this core code

- **Resource Limitation**: Limits the amount of memory and CPU time that the code can use, preventing denial-of-service attacks.
- **Access Control**: Restrict access to the file system and network, ensuring that the code cannot read or modify sensitive data.
- **Process Isolation**: Each code execution runs in a separate process, isolating it from other processes and the host system.
- **Monitoring and Logging**: The sandbox monitors the code execution and logs any suspicious activities for further analysis. Set up connection to your monitoring services via yaml.

## Command Line Usage
### Installation

To install using pip, fist clone the repo and run the following command:
```
git clone github.com/SandyKeeps/py_sandbox
pip install .
```
### Using the Interpreter
```bash
$ py_sandbox -i
sandbox$ 
```
### Running Python Code

The interpreter can take in strings directly:
```bash
$ py_sandbox "print('Hello World')"
$ Hello World
```

## How to Control Sandbox Settings
Use configuration files that specify what is allowed and what is not allowed.


## To-Do
- multiline repl
- take in files from command line
- resource limitation
- access control
- process isolation
- monitor and logging
- deploy to pip 