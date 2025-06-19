def repl():
    globals_dict = {"__builtins__": __builtins__}
    while True:
        try:
            line = input(">>> ")
            try:
                result = eval(line, globals_dict)
                if result is not None:
                    print(result)
            except SyntaxError:
                exec(line, globals_dict)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting REPL.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    repl()
