import ast
import sys
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any, Optional
import json

class CodeAnalyzer(ast.NodeVisitor):
    """
    A comprehensive Python code analyzer using AST.
    Extracts various metrics and information from Python source code.
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all analysis data"""
        self.functions = []
        self.classes = []
        self.imports = []
        self.variables = set()
        self.function_calls = []
        self.complexity_score = 0
        self.line_count = 0
        self.docstrings = []
        self.decorators = []
        self.exceptions = []
        self.loops = []
        self.conditionals = []
        self.current_class = None
        self.current_function = None
        self.scope_stack = []
    
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """Analyze a Python file and return comprehensive metrics"""
        # TODO: take in string
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source_code = f.read()
            return self.analyze_code(source_code, filepath)
        except Exception as e:
            return {"error": f"Failed to analyze {filepath}: {str(e)}"}
    
    def analyze_code(self, source_code: str, filename: str = "None") -> Dict[str, Any]:
        """Analyze Python source code and return comprehensive metrics"""
        self.reset()
        
        try:
            tree = ast.parse(source_code, mode='eval')
            self.line_count = len(source_code.splitlines())
            self.visit(tree)
            
            return self._compile_results()
            
        except SyntaxError as e:
            return {
                "error": f"Syntax error in {filename}: {str(e)}",
                "line": e.lineno,
                "offset": e.offset
            }
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def visit_FunctionDef(self, node):
        """Analyze function definitions"""
        func_info = {
            "name": node.name,
            "line": node.lineno,
            "args": [arg.arg for arg in node.args.args],
            "returns": ast.unparse(node.returns) if node.returns else None,
            "decorators": [ast.unparse(dec) for dec in node.decorator_list],
            "docstring": ast.get_docstring(node),
            "complexity": self._calculate_function_complexity(node),
            "class": self.current_class
        }
        
        self.functions.append(func_info)
        
        # Track decorators
        for decorator in node.decorator_list:
            self.decorators.append({
                "decorator": ast.unparse(decorator),
                "target": node.name,
                "line": decorator.lineno
            })
        
        # Track docstrings
        if func_info["docstring"]:
            self.docstrings.append({
                "type": "function",
                "name": node.name,
                "docstring": func_info["docstring"],
                "line": node.lineno
            })
        
        old_function = self.current_function
        self.current_function = node.name
        self.scope_stack.append(f"function:{node.name}")
        
        self.generic_visit(node)
        
        self.current_function = old_function
        self.scope_stack.pop()
    
    def visit_AsyncFunctionDef(self, node):
        """Handle async function definitions"""
        self.visit_FunctionDef(node)  # Same analysis as regular functions
    
    def visit_ClassDef(self, node):
        """Analyze class definitions"""
        class_info = {
            "name": node.name,
            "line": node.lineno,
            "bases": [ast.unparse(base) for base in node.bases],
            "decorators": [ast.unparse(dec) for dec in node.decorator_list],
            "docstring": ast.get_docstring(node),
            "methods": []
        }
        
        self.classes.append(class_info)
        
        # Track docstrings
        if class_info["docstring"]:
            self.docstrings.append({
                "type": "class",
                "name": node.name,
                "docstring": class_info["docstring"],
                "line": node.lineno
            })
        
        old_class = self.current_class
        self.current_class = node.name
        self.scope_stack.append(f"class:{node.name}")
        
        self.generic_visit(node)
        
        self.current_class = old_class
        self.scope_stack.pop()
    
    def visit_Import(self, node):
        """Track import statements"""
        for alias in node.names:
            self.imports.append({
                "type": "import",
                "module": alias.name,
                "alias": alias.asname,
                "line": node.lineno
            })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Track from...import statements"""
        for alias in node.names:
            self.imports.append({
                "type": "from_import",
                "module": node.module,
                "name": alias.name,
                "alias": alias.asname,
                "line": node.lineno
            })
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Track function calls"""
        try:
            func_name = ast.unparse(node.func)
            self.function_calls.append({
                "function": func_name,
                "line": node.lineno,
                "args": len(node.args),
                "kwargs": len(node.keywords),
                "context": self._get_current_context()
            })
        except:
            pass  # Skip complex calls that can't be unparsed
        
        self.generic_visit(node)
    
    def visit_Name(self, node):
        """Track variable names"""
        if isinstance(node.ctx, ast.Store):
            self.variables.add(node.id)
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Track for loops"""
        self.loops.append({
            "type": "for",
            "line": node.lineno,
            "context": self._get_current_context()
        })
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Track while loops"""
        self.loops.append({
            "type": "while",
            "line": node.lineno,
            "context": self._get_current_context()
        })
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_If(self, node):
        """Track if statements"""
        self.conditionals.append({
            "type": "if",
            "line": node.lineno,
            "has_else": bool(node.orelse),
            "context": self._get_current_context()
        })
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_Try(self, node):
        """Track try-except blocks"""
        self.exceptions.append({
            "type": "try",
            "line": node.lineno,
            "handlers": len(node.handlers),
            "has_finally": bool(node.finalbody),
            "context": self._get_current_context()
        })
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        """Track exception handlers"""
        exc_type = ast.unparse(node.type) if node.type else "Exception"
        self.exceptions.append({
            "type": "except",
            "exception": exc_type,
            "line": node.lineno,
            "context": self._get_current_context()
        })
        self.generic_visit(node)
    
    def _calculate_function_complexity(self, func_node):
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _get_current_context(self):
        """Get the current scope context"""
        return "::".join(self.scope_stack) if self.scope_stack else "global"
    
    def _compile_results(self):
        """Compile all analysis results into a comprehensive report"""
        return {
            "summary": {
                "total_lines": self.line_count,
                "functions": len(self.functions),
                "classes": len(self.classes),
                "imports": len(self.imports),
                "variables": len(self.variables),
                "function_calls": len(self.function_calls),
                "complexity_score": self.complexity_score,
                "loops": len(self.loops),
                "conditionals": len(self.conditionals),
                "exceptions": len(self.exceptions)
            },
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "variables": sorted(list(self.variables)),
            "function_calls": self.function_calls,
            "decorators": self.decorators,
            "docstrings": self.docstrings,
            "loops": self.loops,
            "conditionals": self.conditionals,
            "exceptions": self.exceptions,
            "metrics": self._calculate_metrics()
        }
    
    def _calculate_metrics(self):
        """Calculate additional code metrics"""
        total_funcs = len(self.functions)
        documented_funcs = sum(1 for f in self.functions if f["docstring"])
        
        return {
            "documentation_ratio": documented_funcs / total_funcs if total_funcs > 0 else 0,
            "average_function_complexity": sum(f["complexity"] for f in self.functions) / total_funcs if total_funcs > 0 else 0,
            "most_complex_function": max(self.functions, key=lambda f: f["complexity"]) if self.functions else None,
            "import_diversity": len(set(imp["module"] for imp in self.imports if imp["module"])),
            "decorator_usage": len(self.decorators),
            "exception_handling_ratio": len(self.exceptions) / self.line_count if self.line_count > 0 else 0
        }


# def main():
#     """Example usage of the CodeAnalyzer"""
#     if len(sys.argv) != 2:
#         print("Usage: python analyzer.py <python_file>")
#         return
    
#     analyzer = CodeAnalyzer()
#     results = analyzer.analyze_file(sys.argv[1])
    
#     if "error" in results:
#         print(f"Error: {results['error']}")
#         return
    
#     # Pretty print results
#     print("=" * 60)
#     print(f"CODE ANALYSIS REPORT")
#     print("=" * 60)
    
#     # Summary
#     summary = results["summary"]
#     print(f"\nSUMMARY:")
#     print(f"  Lines of code: {summary['total_lines']}")
#     print(f"  Functions: {summary['functions']}")
#     print(f"  Classes: {summary['classes']}")
#     print(f"  Imports: {summary['imports']}")
#     print(f"  Variables: {summary['variables']}")
#     print(f"  Function calls: {summary['function_calls']}")
#     print(f"  Complexity score: {summary['complexity_score']}")
    
#     # Metrics
#     metrics = results["metrics"]
#     print(f"\nMETRICS:")
#     print(f"  Documentation ratio: {metrics['documentation_ratio']:.2%}")
#     print(f"  Average function complexity: {metrics['average_function_complexity']:.2f}")
#     if metrics['most_complex_function']:
#         print(f"  Most complex function: {metrics['most_complex_function']['name']} (complexity: {metrics['most_complex_function']['complexity']})")
    
#     # Functions
#     if results["functions"]:
#         print(f"\nFUNCTIONS:")
#         for func in results["functions"]:
#             print(f"  {func['name']} (line {func['line']}, complexity: {func['complexity']})")
    
#     # Classes
#     if results["classes"]:
#         print(f"\nCLASSES:")
#         for cls in results["classes"]:
#             print(f"  {cls['name']} (line {cls['line']})")
    
#     # Save detailed results to JSON
#     output_file = sys.argv[1].replace('.py', '_analysis.json')
#     with open(output_file, 'w') as f:
#         json.dump(results, f, indent=2)
#     print(f"\nDetailed analysis saved to: {output_file}")

# if __name__ == "__main__":
#     main()