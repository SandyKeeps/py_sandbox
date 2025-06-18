# src/mypkg/cli.py (argparse version)
import argparse
from py_sandbox.CodeAnalyzer import CodeAnalyzer
from py_sandbox.AnalyzerConfig import AnalyzerConfig
from py_sandbox.CodeRunner import CodeRunner

def main():
    parser = argparse.ArgumentParser(prog="py_sandbox")

    parser.add_argument("code")

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

    # TODO: returned sanitized code
    if args.file:
        pass
    else:
        assert args.code, "Need code via argument or file"
        compiled_results, tree= CodeAnalyzer(ac).analyze_code(source_code=args.code)
        CodeRunner().run_tree(code_tree=tree)    


if __name__ == "__main__":
    main()
