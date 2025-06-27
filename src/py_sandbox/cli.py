import argparse
import code
from py_sandbox.CodeAnalyzer import CodeAnalyzer
from py_sandbox.AnalyzerConfig import AnalyzerConfig
from py_sandbox.CodeRunner import CodeRunner


def multiline_repl():
    console = code.InteractiveConsole()
    buffer = []
    while True:
        try:
            prompt = '........ ' if buffer else 'sandbox$ '
            line = input(prompt)
            buffer.append(line)
            source = '\n'.join(buffer)
            if console.push(source):
                # Incomplete — keep collecting input
                print("incomplete")
                continue
            else:
                # Complete — reset buffer
                print("completed")
                buffer.clear()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting REPL.")
            break
        except Exception as e:
            print(f"Error: {e}")
            buffer.clear()

def repl(ac):
    recurring_vars = {}
    while True:
        try:
            line = input("sandbox$ ")
            compiled_results, tree = CodeAnalyzer(ac).analyze_code(source_code=line)
            captured_output, captured_vars, result = CodeRunner().run_tree(code_tree=tree, recurring_vars=recurring_vars)  
            if captured_output:
                print(f"output: {captured_output}")
            if captured_vars:
                print(f"vars: {captured_vars}")
            if result is not None:
                print(f"result: {result}")
            recurring_vars = captured_vars
        except (EOFError, KeyboardInterrupt):
            print("\nExiting REPL.")
            break
        except Exception as e:
            print(f"Error: {e}")


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
        # multiline_repl()
        repl(ac)

    # TODO: returned sanitized code
    if args.file:
        pass
    elif args.code:
        compiled_results, tree= CodeAnalyzer(ac).analyze_code(source_code=args.code)
        CodeRunner().run_tree(code_tree=tree)    


if __name__ == "__main__":
    main()
