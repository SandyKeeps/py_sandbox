from py_sandbox.CodeAnalyzer import CodeAnalyzer
from py_sandbox.AnalyzerConfig import AnalyzerConfig
from py_sandbox.CodeRunner import CodeRunner

ac = AnalyzerConfig()

compiled_results, tree= CodeAnalyzer(ac).analyze_code(source_code="print('Hello World')")

if compiled_results["alert"]:
    print("Alerts:")
    print(compiled_results["alert_types"])
    if compiled_results["config_no_exec"]:
        print("Not Executing Code")
else:
    captured_output, captured_vars, result = CodeRunner().run_tree(code_tree=tree)
    if captured_output:
        print(f"output: {captured_output}")
    if captured_vars:
        print(f"vars: {captured_vars}")
    if result is not None:
        print(f"result: {result}") 

