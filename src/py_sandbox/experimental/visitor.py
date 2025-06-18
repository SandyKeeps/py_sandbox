import ast
 
 
class FunctionFinderVisitor(ast.NodeVisitor):
   def __init__(self, code):
       self.code = code
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
               # arguement is not a type that we want
               print("Passing an argument type thats not allowed")
 
       function_package = {function_name: {'args': args, 'kwargs': kwargs}}
       # inserting functions to preserve order
       self.functions.insert(0, function_package)
       self.generic_visit(node)