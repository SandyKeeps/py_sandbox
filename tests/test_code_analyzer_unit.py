import ast
import json
import sys
from dataclasses import dataclass, field
import pathlib
import textwrap
import pytest


from py_sandbox.CodeAnalyzer import CodeAnalyzer

# ---- Minimal stub so tests don't depend on your project’s AnalyzerConfig ----
@dataclass
class FakeConfig:
    allowed_complexity: int = 2**31 - 1
    allowed_imports: list = field(default_factory=list)        # if non-empty, acts as whitelist
    blacklist_imports: list = field(default_factory=list)
    allowed_functions: list = field(default_factory=list)      # if non-empty, acts as whitelist
    blacklist: list = field(default_factory=list)
    no_exec: bool = True


@pytest.fixture
def analyzer():
    return CodeAnalyzer(config=FakeConfig())


def unparse(tree):
    # Helper for consistent unparse across tests
    return ast.unparse(tree)


def test_analyze_code_basic_counts(analyzer):
    code = textwrap.dedent(
        """
        import math

        x = 1
        for i in range(3):
            x += i
        if x > 0:
            x -= 1
        try:
            y = 10
        except Exception:
            y = 0
        """
    )
    results, tree = analyzer.analyze_code(code)
    # Summary counts (note: functions/classes are 0 because visit_FunctionDef is commented out)
    s = results["summary"]
    assert s["imports"] == 1
    assert s["variables"] >= 2
    assert s["loops"] == 1
    assert s["conditionals"] == 1
    assert s["exceptions"] >= 1
    assert s["complexity_score"] >= 3  # for + if + try


def test_import_blacklist_via_whitelist_import(analyzer):
    # When whitelist is provided, anything not whitelisted should become "this" and trigger alert
    analyzer.config.allowed_imports = ["math"]
    code = textwrap.dedent(
        """
        import os
        import math
        from random import randint
        """
    )
    results, tree = analyzer.analyze_code(code)
    # Two imports are not in whitelist -> alert
    assert results["alert"] is True
    assert "Imports" in results["alert_types"]
    # Ensure the AST received substitutions for disallowed imports
    src = unparse(tree)
    # `import os` should be rewritten to `import this`
    assert "import this" in src
    # From-import disallowed name should also be rewritten
    assert "random" not in src

def test_import_blacklist_via_blacklist_imports(analyzer):
    analyzer.config.allowed_imports = []  # whitelist disabled
    analyzer.config.blacklist_imports = ["os", "randint"]
    code = textwrap.dedent(
        """
        import os
        from random import randint
        import math
        """
    )
    results, tree = analyzer.analyze_code(code)
    assert results["alert"] is True
    assert "Imports" in results["alert_types"]
    src = unparse(tree)
    assert "import this" in src
    assert "randint" not in src


def test_call_blacklisted_name_rewrites_to_alertFunc(analyzer):
    # Blacklist a function name
    analyzer.config.blacklist = ["danger"]
    code = "result = danger(1, 2)"
    results, tree = analyzer.analyze_code(code)
    src = unparse(tree)
    assert "alertFunc(1, 2)" in src
    assert results["alert"] is True
    assert "Function" in results["alert_types"]


def test_call_blacklisted_attribute_owner_rewrites_to_alertFunc(analyzer):
    # Blacklist a module/object; attribute call should be rewritten
    analyzer.config.blacklist = ["os"]
    code = "x = os.system('ls')"
    results, tree = analyzer.analyze_code(code)
    src = unparse(tree)
    # The Call should be replaced to alertFunc('ls')
    assert "alertFunc('ls')" in src
    assert results["alert"] is True
    assert "Function" in results["alert_types"]


def test_attribute_from_blacklisted_import_marks_alert(analyzer):
    # visit_Attribute should mark alert and rewrite base id to 'this-attr'
    analyzer.config.blacklist = ["requests"]
    code = "ref = requests.get"
    results, tree = analyzer.analyze_code(code)
    assert results["alert"] is True
    assert "Function From Bad Import" in results["alert_types"]
    # Confirm the attribute base got changed
    # Re-unparsing may fail due to invalid identifier "this-attr", so instead walk the tree
    attr_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Attribute)]
    assert len(attr_nodes) == 1
    assert isinstance(attr_nodes[0].value, ast.Name)
    assert attr_nodes[0].value.id == "this-attr"


def test_allowed_functions_whitelist_blocks_others(analyzer):
    # When allowed_functions is set, anything not in it should rewrite to alertFunc
    analyzer.config.allowed_functions = ["safe"]
    code = textwrap.dedent(
        """
        safe(1)
        not_safe(2)
        """
    )
    results, tree = analyzer.analyze_code(code)
    src = unparse(tree)
    assert "safe(1)" in src
    assert "alertFunc(2)" in src
    assert results["alert"] is True
    assert "Function" in results["alert_types"]


def test_complexity_check_method_sets_alert_when_exceeded(analyzer):
    # Complexity is recorded during analyze_code but check_complexity_score isn't auto-called;
    # call it manually to verify the behavior.
    analyzer.config.allowed_complexity = 1
    code = textwrap.dedent(
        """
        for i in range(2):
            pass
        if True:
            pass
        """
    )
    results, tree = analyzer.analyze_code(code)
    # Now check the checker toggles alerts when threshold exceeded
    analyzer.check_complexity_score()
    assert analyzer.alert is True
    assert "Complexity" in analyzer.alert_types


def test_analyze_file_success_and_error(tmp_path, analyzer):
    ok = tmp_path / "ok.py"
    ok.write_text("import math\nx=1\n", encoding="utf-8")
    results, tree = analyzer.analyze_file(str(ok))
    assert isinstance(results, dict)
    assert "summary" in results

    # Non-existent file should return an error dict (not a tuple)
    missing = tmp_path / "missing.py"
    err = analyzer.analyze_file(str(missing))
    assert isinstance(err, dict)
    assert "error" in err


def test_pretty_print_writes_json(tmp_path, monkeypatch, analyzer):
    # pretty_print expects sys.argv[1] to be a .py path to derive output filename
    py = tmp_path / "sample.py"
    py.write_text("print('hi')", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["prog", str(py)])

    code = "x=1"
    results, tree = analyzer.analyze_code(code)
    analyzer.pretty_print(results)

    out = tmp_path / "sample_analysis.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert "summary" in data
