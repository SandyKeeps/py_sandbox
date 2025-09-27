import ast
import textwrap
import pytest
from dataclasses import dataclass, field

from py_sandbox.CodeAnalyzer import CodeAnalyzer

@dataclass
class FakeConfig:
    allowed_complexity: int = 10
    allowed_imports: list = field(default_factory=list)
    blacklist_imports: list = field(default_factory=lambda: ["os"])
    allowed_functions: list = field(default_factory=list)
    blacklist: list = field(default_factory=lambda: ["requests"])
    no_exec: bool = True


@pytest.fixture
def analyzer():
    return CodeAnalyzer(config=FakeConfig())


def test_end_to_end_ast_rewrites_and_metrics(analyzer):
    source = textwrap.dedent(
        """
        import math
        import os                 # blacklisted by import blacklist -> becomes `this`
        from random import randint

        # requests is blacklisted in config.blacklist (used below via attribute)
        def run():
            for i in range(2):
                pass
            if randint() > 0:
                pass
            try:
                pass
            except Exception:
                pass

        # attribute access on a blacklisted name should set alert + rename base
        ref = requests.get

        # attribute call on blacklisted base should rewrite to alertFunc
        x = requests.post('http://example.com')

        # plain name call not in blacklist should be kept
        y = randint()
        """
    )
    results, tree = analyzer.analyze_code(source)
    # Alerts include both imports and function/attr issues
    assert results["alert"] is True
    assert any(t in results["alert_types"] for t in ["Imports", "Function", "Function From Bad Import"])

    # Imports: os should be rewritten
    src = ast.unparse(tree)
    assert "import this" in src

    # The call on blacklisted base should be alertFunc(...)
    assert "alertFunc('http://example.com')" in src

    # Metrics/summaries make sense
    summary = results["summary"]
    assert summary["imports"] >= 2
    assert summary["loops"] >= 1
    assert summary["conditionals"] >= 1
    assert summary["exceptions"] >= 1
    assert isinstance(results["metrics"]["import_diversity"], int)
