import ast
import yaml
from flask import render_template

# TODO: how to keep the AST relevant for relevant code models 


class OurNodeVisitor(ast.NodeVisitor):
    def __init__(self, code):
        self.code = code
        self.is_no_no = False
        self.functions = []

    def visit_Call(self, node: ast.AST) -> None:
        """
        handles all function Calls within an ast node visit
        """
        kwargs = {}
        args = []
        
        if isinstance(node.func, ast.Name):
            # is first function call
            function_name = node.func.id
        else:
            # is attribute
            function_name = node.func.attr
        for kwarg in node.keywords:
            kwarg_name = kwarg.arg
            kwarg_value = kwarg.value.value
            kwargs[kwarg_name] = kwarg_value
        for arg in node.args:
            # the functions defined below only take strings
            if isinstance(arg, ast.Str):
                # arg.s is type string
                str_arg = arg.s
                args.append(str_arg)
            # you could look for other types here
            else:
                # argument is not a type that we want
                print("Passing an argument type thats not allowed")
                self.is_no_no = True


        function_package = {function_name: {'args': args, 'kwargs': kwargs}}
        # inserting functions to preserve order
        self.functions.insert(0, function_package)
        self.generic_visit(node)

    def generic_Visit(self, node: ast.AST) -> None:
        print(node)
        self.generic_visit(node)


class py_sandbox:
    # TODO: This could be configurable
    # which functions are allowed to be run
    # create a white list and blacklist 
    # TODO: Use AST to find breakpoints in agentic code to send to different parts of the sandbox
    # How to create dynamic sandboxes that are not persistent
    def __init__(self, configuration: str) -> None:
        """
        :param configuration: sets the configuration for the sandbox
        take in yaml configuration for the sandbox
        """
        if configuration is str:
            parsed_config = yaml.safe_load(configuration)
        else:
            # TODO
            pass

        

        

        

    def single_function(self, function_to_call: str, value=None) -> None:
        """
        :param function_to_call: function defined in this class
        :param inputs: args and kwargs for the functions
        """
        self.user_answer = value
        self.available_functions = {
            "play": self.play,
            "get_song_length": self.get_song_length
        }
        if isinstance(function_to_call, str):
            print(function_to_call)
            parsed_func = ast.parse(function_to_call, mode='exec')  # changed to exec from eval 
            nv = OurNodeVisitor(function_to_call)
            nv.visit(parsed_func)
            if nv.is_no_no:
                # TODO: send notification that there was an escape
                # Here just logs errors, 
                # the sandbox Handler will handle putting them on the Kafka que 
                self.user_answer = render_template("bad_kitty.html")
                return
            self.handle_function(nv.functions)
        else:
            self.handle_function(function_to_call)

        self.analyze_value()


    def handle_function(self, function_package: dict) -> None:
        """
        runs the functions after parsing
        :param function_package: a list of dictionaries which hold the functions and parameters
        """
        for func in function_package:
            if isinstance(func, str):
                transform = self.available_functions.get(func, self.unknown_func)
                transform()
                continue
            for func_name, call_args in func.items():
                transform = self.available_functions.get(func_name, self.unknown_func)
                if 'args' in call_args:
                    transform(*call_args['args'], **call_args["kwargs"])
                else:
                    transform(**call_args)

    def analyze_value(self) -> None:
        # Impliment analytics here
        print(self.user_answer)

    def get_song_length(self, song: str) -> None:
        self.user_answer = str(len(song))

    def play(self, song: str) -> None:
        # loggic to play song
        self.user_answer = f"playing song: {song}"

    def unknown_func(self, *args, **kwargs):
        print("Calling a function not in whitelist")
        self.user_answer = render_template("bad_kitty.html")
        # one could impliment a custom Exception for this
        # return "bad kitty"
        # raise Exception