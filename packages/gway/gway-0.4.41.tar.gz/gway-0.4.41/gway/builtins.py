# file: gway/builtins.py

import os
import re
import sys
import html
import code
import random
import inspect
import collections.abc
from collections.abc import Mapping, Sequence
from typing import Any, Optional, Type, List


# Avoid importing Gateway at the top level in this file specifically (circular import)
# Instead, use "from gway import gw" inside the function definitions themselves
# Keep comments and names to a minimum. This module will get long.

def hello_world(name: str = "World", *, greeting: str = "Hello", **kwargs):
    """Smoke test function."""
    from gway import gw
    version = gw.version()
    message = f"{greeting.title()}, {name.title()}!"
    if hasattr(gw, "hello_world"):
        if not gw.silent:
            print(message)
        else:
            print(f"{gw.silent=}")
    else:
        print("Greeting protocol not found ((serious smoke)).")

    # Only return simple fields to avoid huge recursive HTML when rendered
    return {
        "greeting": greeting,
        "name": name,
        "message": message,
        "version": version,
    }

def abort(message: str, *, exit_code: int = 13) -> int:
    """Abort with error message."""
    from gway import gw
    gw.critical(message)
    print(f"Halting: {message}")
    raise SystemExit(exit_code)

def envs(filter: str = None) -> dict:
    """Return all environment variables in a dictionary."""
    if filter:
        filter = filter.upper()
        return {k: v for k, v in os.environ.items() if filter in k}
    else: 
        return os.environ.copy()

def version(check=None) -> str:
    """Return the version of the package."""
    from gway import gw

    def parse_version(vstr):
        parts = vstr.strip().split(".")
        if len(parts) == 1:
            parts = (parts[0], '0', '0')
        elif len(parts) == 2:
            parts = (parts[0], parts[1], '0')
        if len(parts) > 3:
            raise ValueError(f"Invalid version format: '{vstr}', expected 'major.minor.patch'")
        return tuple(int(part) for part in parts)

    # Get the version in the VERSION file
    version_path = gw.resource("VERSION")
    if os.path.exists(version_path):
        with open(version_path, "r") as version_file:
            current_version = version_file.read().strip()

        if check:
            current_tuple = parse_version(current_version)
            required_tuple = parse_version(check)
            if current_tuple < required_tuple:
                raise AssertionError(f"Required version >= {check}, found {current_version}")

        return current_version
    else:
        gw.critical("VERSION file not found.")
        return "unknown"

def normalize_ext(e):
    return e if e.startswith('.') else f'.{e}'

def resource(*parts, touch=False, check=False, text=False, dir=False):
    """
    Locate or create a resource by searching in:
    1. Current working directory
    2. GWAY_ROOT environment variable
    3. User home directory

    If not found, returns the path in the CWD (which may not exist) unless check=True, in which case aborts.

    Arguments:
    - touch: if True, create the file (and parents) if it does not exist.
    - dir: if True, create the final path as a directory, not a file.
    - text: if True, return file contents as text, not a Path.
    - check: if True, abort if resource does not exist.
    """
    import os
    import pathlib
    from gway import gw

    rel_path = pathlib.Path(*parts)
    tried = []

    # 1. Current working directory
    candidate = pathlib.Path.cwd() / rel_path
    if candidate.exists() or touch or dir:
        path = candidate
    else:
        tried.append(str(candidate))
        env_root = os.environ.get("GWAY_ROOT")
        if env_root:
            candidate = pathlib.Path(env_root) / rel_path
            if candidate.exists() or touch or dir:
                path = candidate
            else:
                tried.append(str(candidate))
                # 3. Home directory
                candidate = pathlib.Path.home() / rel_path
                if candidate.exists() or touch or dir:
                    path = candidate
                else:
                    tried.append(str(candidate))
                    path = pathlib.Path.cwd() / rel_path
        else:
            # 3. Home directory
            candidate = pathlib.Path.home() / rel_path
            if candidate.exists() or touch or dir:
                path = candidate
            else:
                tried.append(str(candidate))
                path = pathlib.Path.cwd() / rel_path

    # Safety check
    if not (touch or dir) and check and not path.exists():
        gw.abort(f"Required resource {path} missing. Tried: {tried}")

    # Ensure parents exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # If dir=True, create final directory (even if doesn't exist)
    if dir:
        path.mkdir(parents=True, exist_ok=True)
    elif touch:
        # Optionally create the file (not directory)
        if not path.exists():
            path.touch()

    # Return text contents or path
    if text:
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            gw.abort(f"Failed to read {path}: {e}")
    return path.resolve()

def resource_list(*parts, ext=None, prefix=None, suffix=None):
    """
    List all files in a resourced directory that match optional filters.

    This builds a path just like `resource`, but treats it as a directory,
    then lists all files inside that match the given extension, prefix, and/or suffix.

    Args:
        *parts: Path components like ("subdir",).
        ext (str): Optional file extension to match, e.g., ".txt".
        prefix (str): Optional filename prefix to match.
        suffix (str): Optional filename suffix to match.

    Returns:
        list[pathlib.Path]: Sorted list of matching files by creation time (oldest first).
    """
    from gway import gw

    # Build the base directory path using resource
    base_dir = resource(*parts)
    if not base_dir.exists() or not base_dir.is_dir():
        gw.abort(f"Resource directory {base_dir} does not exist or is not a directory")

    # Gather matching files
    matches = []
    for item in base_dir.iterdir():
        if not item.is_file():
            continue
        name = item.name
        if ext and not name.endswith(ext):
            continue
        if prefix and not name.startswith(prefix):
            continue
        if suffix and not name.endswith(suffix):
            continue
        matches.append(item)

    # Sort by creation time (ascending)
    matches.sort(key=lambda p: p.stat().st_ctime)
    return matches

def is_test_flag(name: str) -> bool:
    """Return True if ``name`` is present in ``GW_TEST_FLAGS`` environment variable."""
    import os
    flags = os.environ.get("GW_TEST_FLAGS", "")
    active = {f.strip() for f in flags.replace(",", " ").split() if f.strip()}
    return name in active

def test(*, root: str = 'tests', filter=None, on_success=None, on_failure=None, coverage: bool = False, flags=None):
    """Execute all automatically detected test suites.

    Args:
        root: Directory containing test files.
        filter: Optional filename substring to select tests.
        on_success: Action when tests pass (e.g., "clear" removes log file).
        on_failure: Action when tests fail ("abort" exits immediately).
        coverage: Enable coverage reporting using ``coverage`` module.
        flags: Optional iterable or comma/space separated string of feature
            flags. These are stored in the ``GW_TEST_FLAGS`` environment
            variable so individual tests can check ``is_test_flag("name")``.
    """
    import unittest
    import os
    import time
    from gway import gw
    from gway.logging import use_logging
    if flags:
        if isinstance(flags, str):
            flag_list = [f.strip() for f in flags.replace(',', ' ').split() if f.strip()]
        else:
            flag_list = list(flags)
        os.environ['GW_TEST_FLAGS'] = ','.join(flag_list)
        gw.testing_flags = set(flag_list)
    else:
        env_flags = os.environ.get('GW_TEST_FLAGS', '')
        gw.testing_flags = {f.strip() for f in env_flags.replace(',', ' ').split() if f.strip()}
    cov = None
    if coverage:
        try:
            from coverage import Coverage
            cov = Coverage()
            cov.start()
        except Exception as e:
            gw.warning(f"Coverage requested but failed to initialize: {e}")

    log_path = os.path.join("logs", "test.log")

    with use_logging(
        logfile="test.log",
        logdir="logs",
        prog_name="gway",
        debug=getattr(gw, "debug", False),
        backup_count=0,
        verbose=getattr(gw, "verbose", False),
    ):
        print("Running the test suite...")

        def is_test_file(file):
            if filter:
                return file.endswith('.py') and filter in file
            return file.endswith('.py') and not file.startswith('_')

        test_files = [
            os.path.join(root, f) for f in os.listdir(root)
            if is_test_file(f)
        ]

        test_loader = unittest.defaultTestLoader
        test_suite = unittest.TestSuite()

        for test_file in test_files:
            test_suite.addTests(test_loader.discover(
                os.path.dirname(test_file), pattern=os.path.basename(test_file)))

        class TimedResult(unittest.TextTestResult):
            def startTest(self, test):
                super().startTest(test)
                if getattr(gw, "timed_enabled", False):
                    self._start_time = time.perf_counter()

            def stopTest(self, test):
                if getattr(gw, "timed_enabled", False) and hasattr(self, "_start_time"):
                    elapsed = time.perf_counter() - self._start_time
                    gw.log(f"[test] {test} took {elapsed:.3f}s")
                super().stopTest(test)

        runner = unittest.TextTestRunner(verbosity=2, resultclass=TimedResult)
        result = runner.run(test_suite)
        gw.info(f"Test results: {str(result).strip()}")

    if cov:
        cov.stop()
        try:
            percent = cov.report(include=["gway/*"])
            gw.info(f"gway coverage: {percent:.2f}%")
            print(f"gway: {percent:.2f}%")
            projects_dir = "projects"
            if os.path.isdir(projects_dir):
                for proj in sorted(os.listdir(projects_dir)):
                    if proj.startswith("__"):
                        continue
                    path = os.path.join(projects_dir, proj)
                    include_paths = []
                    if os.path.isdir(path):
                        include_paths = [os.path.join(os.path.abspath(path), "*")]
                    elif os.path.isfile(path) and path.endswith(".py"):
                        include_paths = [os.path.abspath(path)]
                    if include_paths:
                        try:
                            percent = cov.report(include=include_paths)
                            gw.info(f"{proj} coverage: {percent:.2f}%")
                            print(f"{proj}: {percent:.2f}%")
                        except Exception:
                            gw.warning(f"Coverage report failed for {proj}")
            total = cov.report()
            gw.info(f"Total coverage: {total:.2f}%")
            print(f"Total: {total:.2f}%")
        except Exception as e:
            gw.warning(f"Coverage report failed: {e}")

    # --- Cleanup: Remove test.log if tests succeeded and on_success is 'clear' ---
    if result.wasSuccessful() and on_success == "clear":
        if os.path.exists(log_path):
            os.remove(log_path)

    if not result.wasSuccessful() and on_failure == "abort":
        gw.abort(f"Tests failed with --abort flag. Results: {str(result).strip()}")

    return result.wasSuccessful()

def help(*args, full=False):
    from gway import gw
    import os, textwrap, ast, sqlite3

    gw.info(f"Help on {' '.join(args)} requested")

    def extract_gw_refs(source):
        refs = set()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return refs

        class GwVisitor(ast.NodeVisitor):
            def visit_Attribute(self, node):
                parts = []
                cur = node
                while isinstance(cur, ast.Attribute):
                    parts.append(cur.attr)
                    cur = cur.value
                if isinstance(cur, ast.Name) and cur.id == "gw":
                    parts.append("gw")
                    full = ".".join(reversed(parts))[3:]  # remove "gw."
                    refs.add(full)
                self.generic_visit(node)

        GwVisitor().visit(tree)
        return refs

    db_path = gw.resource("data", "help.sqlite")
    if not os.path.isfile(db_path):
        gw.release.build_help_db()

    joined_args = " ".join(args).strip().replace("-", "_")
    norm_args = [a.replace("-", "_").replace("/", ".") for a in args]

    with gw.sql.open_connection(db_path, row_factory=True) as cur:
        if not args:
            cur.execute("SELECT DISTINCT project FROM help")
            return {"Available Projects": sorted([row["project"] for row in cur.fetchall()])}

        rows = []

        # Case 1: help("web.site.view_help")
        if len(norm_args) == 1 and "." in norm_args[0]:
            parts = norm_args[0].split(".")
            if len(parts) >= 2:
                project = ".".join(parts[:-1])
                function = parts[-1]
                cur.execute("SELECT * FROM help WHERE project = ? AND function = ?", (project, function))
                rows = cur.fetchall()
                if not rows:
                    try:
                        cur.execute("SELECT * FROM help WHERE help MATCH ?", (f'"{norm_args[0]}"',))
                        rows = cur.fetchall()
                    except sqlite3.OperationalError as e:
                        gw.warning(f"FTS query failed for {norm_args[0]}: {e}")
            else:
                return {"error": f"Could not parse dotted input: {norm_args[0]}"}

        # Case 2: help("web", "view_help") or help("builtin", "hello_world")
        elif len(norm_args) >= 2:
            *proj_parts, maybe_func = norm_args
            project = ".".join(proj_parts)
            function = maybe_func
            cur.execute("SELECT * FROM help WHERE project = ? AND function = ?", (project, function))
            rows = cur.fetchall()
            if not rows:
                fuzzy_query = ".".join(norm_args)
                try:
                    cur.execute("SELECT * FROM help WHERE help MATCH ?", (f'"{fuzzy_query}"',))
                    rows = cur.fetchall()
                except sqlite3.OperationalError as e:
                    gw.warning(f"FTS fallback failed for {fuzzy_query}: {e}")

        # Final fallback: maybe it's a builtin like help("hello_world")
        if not rows and len(norm_args) == 1:
            name = norm_args[0]
            cur.execute("SELECT * FROM help WHERE project = ? AND function = ?", ("builtin", name))
            rows = cur.fetchall()

        if not rows:
            fuzzy_query = ".".join(norm_args)
            try:
                cur.execute("SELECT * FROM help WHERE help MATCH ?", (f'"{fuzzy_query}"',))
                rows = cur.fetchall()
            except sqlite3.OperationalError as e:
                gw.warning(f"FTS final fallback failed for {fuzzy_query}: {e}")
                return {"error": f"No help found and fallback failed for: {joined_args}"}

        results = []
        for row in rows:
            project = row["project"]
            function = row["function"]
            prefix = f"gway {project} {function.replace('_', '-')}" if project != "builtin" else f"gway {function.replace('_', '-')}"
            entry = {
                "Project": project,
                "Function": function,
                "Sample CLI": prefix,
                "References": sorted(extract_gw_refs(row["source"])),
            }
            if full:
                entry["Full Code"] = row["source"]
            else:
                entry["Signature"] = textwrap.fill(row["signature"], 100).strip()
                entry["Docstring"] = row["docstring"].strip() if row["docstring"] else None
                entry["TODOs"] = row["todos"].strip() if row["todos"] else None
            results.append({k: v for k, v in entry.items() if v})

        return results[0] if len(results) == 1 else {"Matches": results}

def sample_cli(func):
    """Generate a sample CLI string for a function."""


    from gway import gw
    if not callable(func):
        func = gw[str(func)]
    sig = inspect.signature(func)
    parts = []
    seen_kw_only = False

    for name, param in sig.parameters.items():
        kind = param.kind

        if kind == inspect.Parameter.VAR_POSITIONAL:
            parts.append(f"[{name}1 {name}2 ...]")
        elif kind == inspect.Parameter.VAR_KEYWORD:
            parts.append(f"[--{name}1 val1 --{name}2 val2 ...]")
        elif kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
            if not seen_kw_only:
                parts.append(f"<{name}>")
            else:
                parts.append(f"--{name.replace('_', '-')} <val>")
        elif kind == inspect.Parameter.KEYWORD_ONLY:
            seen_kw_only = True
            cli_name = f"--{name.replace('_', '-')}"
            if param.annotation is bool or isinstance(param.default, bool):
                parts.append(f"[{cli_name} | --no-{name.replace('_', '-')}]")
            else:
                parts.append(f"{cli_name} <val>")

    return " ".join(parts)

def sigils(*args: str):
    """List the valid sigils found in any of the given args."""
    from .sigils import Sigil
    text = "\n".join(args)
    return Sigil(text).list_sigils()

def try_cast(value, default=None, **types) -> tuple:
    """
    Try casting `value` to each provided type. If a cast succeeds, 
    returns the corresponding key (name) and the value after casting.
    If none succeed, returns default and the original value.
    Example:
        gw.try_cast("42", INTEGER=int, REAL=float)  # => "INTEGER"
        gw.try_cast("hello", INTEGER=int, default="TEXT")  # => "TEXT"
    """
    for name, caster in types.items():
        try:
            new_value = caster(value)
            return name, new_value
        except Exception:
            continue
    return default, value

def run_recipe(*scripts: str, **context):
    """
    Run commands parsed from one or more .gwr files, falling back to the 'recipes/' resource bundle.
    Recipes are just simple GWAY scripts: one command per line, with optional comments.
    """
    from .console import load_recipe, process
    from gway import gw

    if not scripts:
        raise ValueError("At least one script must be provided to run_recipe()")
    gw.debug(f"run_recipe called with scripts: {scripts!r}")

    results = []
    for script in scripts:
        orig_script = script
        # Ensure extension
        if not script.endswith('.gwr'):
            script += '.gwr'
            gw.debug(f"Appended .gwr extension: {script!r}")

        # Try to resolve the script as given
        try:
            script_path = gw.resource(script, check=True)
            gw.debug(f"Found script at: {script_path}")
        except (FileNotFoundError, KeyError) as first_exc:
            # Fallback: look in the 'recipes' directory of the package
            gw.debug(f"Script not found at {script!r}: {first_exc!r}")
            try:
                script_path = gw.resource("recipes", script)
                gw.debug(f"Found script in 'recipes/': {script_path}")
            except Exception as second_exc:
                # If still not found, re-raise with a clear message
                msg = (
                    f"Could not locate script {script!r} "
                    f"(tried direct lookup and under 'recipes/')."
                )
                gw.debug(f"{msg} Last error: {second_exc!r}")
                raise FileNotFoundError(msg) from second_exc

        # Load and run the recipe
        command_sources, comments = load_recipe(script_path)
        if comments:
            gw.debug("Recipe comments:\n" + "\n".join(comments))
        result = process(command_sources, **context)
        results.append(result)
    return results[-1] if len(results) == 1 else results

def run(*script: str, **context):
    """Run recipes. If recipes are not found, treat the input as the literal recipe to be run."""
    from gway import gw
    import uuid
    import os
    from datetime import datetime

    # Try to run all scripts as recipes first
    try:
        return gw.run_recipe(*script, **context)
    except FileNotFoundError:
        # Not found: treat script as raw lines, write to temp recipe and run that
        gw.debug(f"run(): Could not find one or more recipes, treating script as raw lines")
        work_dir = gw.resource("work", check=True)
        unique_id = str(uuid.uuid4())
        recipe_name = f"run_{unique_id}.gwr"
        recipe_path = os.path.join(work_dir, recipe_name)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
        context_lines = [
            f"# GWAY ad-hoc script",
            f"# Created: {now} by {user}",
            f"# Args: {script!r}",
        ]
        if context:
            context_lines.append(f"# Context: {context!r}")
        script_lines = list(script)
        all_lines = context_lines + list(script_lines)

        # Write to file
        with open(recipe_path, "w", encoding="utf-8") as f:
            for line in all_lines:
                f.write(line.rstrip("\n") + "\n")
        gw.debug(f"Wrote ad-hoc script to {recipe_path}")

        # Now run the new recipe
        return gw.run_recipe(recipe_path, **context)



# Excludse ambiguous characters: 0, O, 1, I, l, Z, 2
_EZ_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXY3456789"

def random_id(length: int = 8, alphabet: str = _EZ_ALPHABET) -> str:
    """Generate a readable random ID, avoiding confusing characters."""
    return ''.join(random.choices(alphabet, k=length))

def notify(message: str, *, title: str = "GWAY Notice", timeout: int = 10):
    """Send a notification via GUI, email or console fallback."""
    from gway import gw
    try:
        gw.screen.notify(message, title=title, timeout=timeout)
        return "gui"
    except Exception as e:
        gw.debug(f"GUI notify failed: {e}")
    try:
        if hasattr(gw, "mail") and os.environ.get("ADMIN_EMAIL"):
            gw.mail.send(title, body=message, to=os.environ.get("ADMIN_EMAIL"))
            return "email"
    except Exception as e:  # pragma: no cover - mail may not be configured
        gw.debug(f"Email notify failed: {e}")
    print(message)
    gw.info(f"Console notify: {message}")
    return "console"

def shell():
    """Launch an interactive Python shell with 'from gway import gw' preloaded."""
    from gway import gw, __
    local_vars = {'gw': gw, '__': __}
    banner = "GWAY interactive shell.\nfrom gway import gw  # Python 3.13 compatible"
    code.interact(banner=banner, local=local_vars)


def init_root(path: str | None = None) -> str:
    """Create a minimal GWAY workspace at the resolved path."""
    from pathlib import Path
    from gway import gw

    target = Path(
        gw.resolve(
            path,
            "[GWAY_ROOT]",
            "[GWAY_PATH]",
            "[BASE_PATH]",
            "[APP_ROOT]",
            default=".",
        )
    ).resolve()

    subdirs = [
        "envs/clients",
        "envs/servers",
        "projects",
        "data/static",
        "logs",
        "work",
        "recipes",
    ]

    for sub in subdirs:
        (target / sub).mkdir(parents=True, exist_ok=True)

    readme = target / "README.rst"
    if not readme.exists():
        readme.write_text("# GWAY Workspace\nCreated by `gway init-root`\n")

    gw.info(f"Initialized root at {target}")
    return str(target)
