from py_sandbox.CodeAnalyzer import CodeAnalyzer
from py_sandbox.CodeRunner import CodeRunner

def sandbox_run(ac, line, recurring_vars):
    compiled_results, tree = CodeAnalyzer(ac).analyze_code(source_code=line)
    if compiled_results["alert"]:
        print(f"Alerts: {compiled_results['alert_types']}")
    captured_output, captured_vars, result = CodeRunner().run_tree(code_tree=tree, recurring_vars=recurring_vars)  
    if captured_output:
        print(captured_output)
    # if captured_vars:
    #     print(f"vars: {captured_vars}")
    if result is not None:
        print(f"result: {result}")
    return captured_vars

def custom_multiline_repl(ac):
    buffer = []
    recurring_vars = {}
    indent = False
    prompt = "sandbox$ "
    
    while True:
        try:
            line = input(prompt)

            if line == '' and indent:
                prompt = "sandbox$ "
                buffer.append(line)
                src = "\n".join(buffer)
                buffer.clear()
                line = src
            elif indent:
                buffer.append(line)
                continue
            indent = False

            recurring_vars =sandbox_run(ac, line, recurring_vars)
        
        except (EOFError, KeyboardInterrupt):
            print("\nExiting REPL.")
            break
        except IndentationError as e:
            if indent:
                print(e)
                indent = False
            else:
                indent = True
                buffer.append(line)
                prompt = ">>> "
                continue
        except SyntaxError as e:
            print(f"After indent: {e}")
            continue
        except Exception as e:
            print(f"{type(e)}: {e}")