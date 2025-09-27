# tests/test_integration_matrix.py
import ast
from pathlib import Path

import pytest

from py_sandbox.CodeAnalyzer import CodeAnalyzer
from py_sandbox.AnalyzerConfig import AnalyzerConfig  # adjust import path if different


# --- Discovery helpers --------------------------------------------------------

def _discover_case_files():
    """Find all Python source files used as integration cases."""
    case_dir = Path(__file__).parent / "integration_cases"
    return sorted(case_dir.glob("*.py"))

def _discover_config_files():
    """Find all YAML config files used to parameterize the analyzer."""
    cfg_dir = Path(__file__).parent / "configs"
    return sorted(list(cfg_dir.glob("*.yaml")) + list(cfg_dir.glob("*.yml")))


CASE_FILES = _discover_case_files()
CONFIG_FILES = _discover_config_files()

if not CASE_FILES:
    pytest.skip("No integration case files found in tests/integration_cases/", allow_module_level=True)
if not CONFIG_FILES:
    pytest.skip("No analyzer config files found in tests/configs/", allow_module_level=True)


# --- Parametrized test: Cartesian product of (config, case) -------------------

@pytest.mark.parametrize("config_path", CONFIG_FILES, ids=lambda p: f"cfg:{p.name}")
@pytest.mark.parametrize("case_path", CASE_FILES, ids=lambda p: f"case:{p.name}")
def test_end_to_end_matrix(config_path, case_path):
    """
    Run CodeAnalyzer on every (config, case) pair.
    Basic sanity assertions always apply.
    Additionally, if the case contains any blacklisted term from the config,
    we expect an alert to be raised.
    """
    # Load source
    source = case_path.read_text(encoding="utf-8")

    # Build analyzer with this config
    config = AnalyzerConfig(config_path=str(config_path))
    analyzer = CodeAnalyzer(config=config)

    # Analyze
    results, tree = analyzer.analyze_code(source)

    # Sanity checks
    assert isinstance(results, dict), "Analyzer must return a results dict"
    assert tree is not None, "Analyzer must return an AST"
    src_after = ast.unparse(tree)
    assert isinstance(src_after, str) and src_after, "Unparsed code should be non-empty"

    # Metrics should exist and be sensible types
    summary = results.get("summary", {})
    metrics = results.get("metrics", {})
    for key in ("imports", "loops", "conditionals", "exceptions"):
        assert isinstance(summary.get(key, 0), int), f"summary['{key}'] must be int"
    assert isinstance(metrics.get("import_diversity", 0), int), "metrics['import_diversity'] must be int"

    # Expectation rule-of-thumb:
    # If any blacklisted name (imports, statements, or functions) appears in the source
    # AND is not in the allowed lists, then we expect an alert.
    # (This is a heuristic to keep the test generic across many cases/configs.)
    blacklist_names = set(config.blacklist)
    allowed_union = set(config.allowed_imports) | set(config.allowed_functions) | set(config.allowed_statements)
    print(f"BlacklistNames: {blacklist_names}")
    offending = [
        name for name in blacklist_names
        if (name not in allowed_union) and (name in source)
    ]

    if offending:
        assert results.get("alert") is True, (
            f"Expected alert=True because these blacklisted names appear in source: {offending}"
        )
        # If imports are blacklisted, a common rewrite is changing bad imports to `this`
        # (Only assert this if the case actually imports that module.)
        if any(x in source for x in config.blacklist_imports):
            # Don't over-constrain; just ensure our rewrite signature shows up somewhere
            assert "import this" in src_after or "from this import" in src_after, \
                "Expected rewritten imports to involve `this`"
    else:
        # If there are no offending names, the analyzer may or may not alert depending on complexity/other rules.
        # Keep this lenient but consistent: it must be a boolean.
        assert isinstance(results.get("alert"), bool), "results['alert'] must be a boolean"
