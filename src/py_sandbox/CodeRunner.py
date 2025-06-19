import io
import contextlib
import ast

# TODO: sanitize this class as much as possible

def create_nothingFunc():
    return ast.FunctionDef(
        name="nothingFunc",
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            vararg=ast.arg(arg="args"),
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=ast.arg(arg="kwargs"),
            defaults=[]
        ),
        body=[
            ast.Expr(value=ast.Call(
                func=ast.Name(id='print', ctx=ast.Load()),
                args=[ast.Constant(value='NothingFuncCalled')],
                keywords=[]
            )),
            ast.Return(value=ast.Constant(value='mocked result'))
        ],
        decorator_list=[]
    )

class CodeRunner:

    def __init__(self):
        pass

    def run_code(self, code_string):
        output_buffer = io.StringIO()
        captured_vars = {}
        # Redirect stdout to the buffer while executing code
        with contextlib.redirect_stdout(output_buffer):
            exec(code_string , {}, captured_vars)
        captured_output = output_buffer.getvalue()
        output_buffer.close()
        return captured_output, captured_vars
    
    def run_tree(self, code_tree, recurring_vars={}):
        output_buffer = io.StringIO()
        # captured_vars = {}
        code_tree.body.insert(0, create_nothingFunc())
        ast.fix_missing_locations(code_tree)
        # print(ast.dump(code_tree))
        # print(f"GLOBALS: {globals_dict}")
        with contextlib.redirect_stdout(output_buffer):
            compiled = compile(code_tree, '<string>', 'exec')
            result = exec(compiled, {}, recurring_vars)
        
        captured_output = output_buffer.getvalue()
        output_buffer.close()
        # print(f"Result: {result}")
        # print(f"Captured Output: {captured_output}")
        # print(f"captured vars: {captured_vars}")
        return captured_output, recurring_vars, result

    def run_interpreter(self):
        pass

    def run_command_line(self):
        pass