import argparse
from py_sandbox.repl import custom_multiline_repl
from py_sandbox.CodeAnalyzer import CodeAnalyzer
from py_sandbox.AnalyzerConfig import AnalyzerConfig
from py_sandbox.CodeRunner import CodeRunner

def main():
    parser = argparse.ArgumentParser(prog="py_sandbox")

    parser.add_argument("--code")
    parser.add_argument("-i", "--interactive", action='store_true')

    parser.add_argument(
        "-f", "--file", 
        help="path to python file",
        type=str,
        required=False)
    
    parser.add_argument(
        "-c", "--config", 
        help="Config File for sandbox",
        type=str,
        required=False)
    args = parser.parse_args()

    if args.config:
        ac = AnalyzerConfig(config_path=args.config)
    else:
        ac = AnalyzerConfig()

    if args.interactive:
        custom_multiline_repl(ac)

    # TODO: returned sanitized code
    if args.file:
        pass
    elif args.code:
        compiled_results, tree= CodeAnalyzer(ac).analyze_code(source_code=args.code)
        # TODO: Do this better and in a more generic place:
        if compiled_results["config_no_exec"] and compiled_results["alert"]:
            print("Not Executing Code")
            print(compiled_results["alert_types"])
        else:
            captured_output, captured_vars, result = CodeRunner().run_tree(code_tree=tree)
            if captured_output:
                print(f"output: {captured_output}")
            if captured_vars:
                print(f"vars: {captured_vars}")
            if result is not None:
                print(f"result: {result}") 


if __name__ == "__main__":
    main()
