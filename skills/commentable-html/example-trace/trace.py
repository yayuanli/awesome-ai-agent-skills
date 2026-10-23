"""Trace Python's bisect.bisect_left line by line on one example, and record every value.

Every value on index.html comes from this script. Run it with:  python3 trace.py
It prints the trace and writes trace.json beside itself.

`import bisect` normally hands you a C version (from the _bisect module) that cannot be traced
line by line. The same file, Lib/bisect.py, also holds the pure-Python version that runs when the
C module is missing. This script blocks the C module, traces the pure-Python bisect_left, and then
checks that the C version returns the same answer.
"""
import ast
import importlib
import inspect
import json
import linecache
import os
import platform
import sys

SORTED_LIST = [3, 8, 8, 15, 21, 40]
VALUE = 8

# 1. Keep the C versions for the cross-check, then load the pure-Python fallback.
import bisect as bisect_c  # noqa: E402

c_bisect_left, c_bisect_right = bisect_c.bisect_left, bisect_c.bisect_right
del sys.modules["bisect"]
sys.modules["_bisect"] = None  # makes `from _bisect import *` raise ImportError inside bisect.py
bisect_py = importlib.import_module("bisect")
assert inspect.isfunction(bisect_py.bisect_left), "still the C version"
SOURCE_FILE = inspect.getsourcefile(bisect_py)


def statements_by_line(func):
    """Map each line number in func's body to the statement that starts on it."""
    tree = ast.parse(open(SOURCE_FILE).read())
    fdef = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == func.__name__)
    found = {}
    for node in ast.walk(fdef):
        if isinstance(node, ast.stmt) and node is not fdef:
            found.setdefault(node.lineno, node)
    return found


def segment(node):
    return ast.get_source_segment(open(SOURCE_FILE).read(), node)


def run_traced(func, a, x):
    """Call func(a, x) under sys.settrace and return (result, events) for func's own frame."""
    code = func.__code__
    events = []

    def tracer(frame, event, arg):
        if frame.f_code is not code:
            return None
        snapshot = {k: (list(v) if isinstance(v, list) else v) for k, v in frame.f_locals.items()}
        if event == "line":
            events.append({"event": "line", "line": frame.f_lineno, "locals": snapshot})
        elif event == "return":
            events.append({"event": "return", "line": frame.f_lineno, "locals": snapshot, "value": arg})
        return tracer

    sys.settrace(tracer)
    try:
        result = func(a, x)
    finally:
        sys.settrace(None)
    return result, events


def describe(func, events):
    """Turn raw line events into steps: the source line, and the value it produced."""
    stmts = statements_by_line(func)
    steps = []
    for i, ev in enumerate(events):
        if ev["event"] != "line":
            continue
        line = ev["line"]
        node = stmts.get(line)
        before = ev["locals"]
        after = events[i + 1]["locals"] if i + 1 < len(events) else before
        step = {"line": line, "code": linecache.getline(SOURCE_FILE, line).rstrip("\n"), "before": before}
        if isinstance(node, (ast.If, ast.While)):
            test = segment(node.test)
            step["kind"] = "test"
            step["test"] = test
            step["value"] = eval(test, {"len": len}, dict(before))
            # the value of each side of a comparison, such as a[mid] in `a[mid] < x`
            if isinstance(node.test, ast.Compare):
                sides = [s for s in [node.test.left] + list(node.test.comparators) if not isinstance(s, ast.Constant)]
                step["sides"] = {segment(s): eval(segment(s), {"len": len}, dict(before)) for s in sides}
        elif isinstance(node, ast.Assign):
            target = node.targets[0].id
            step["kind"] = "assign"
            step["target"] = target
            step["value"] = after[target]
        elif isinstance(node, ast.Return):
            step["kind"] = "return"
            step["value"] = events[i + 1]["value"]
        else:
            step["kind"] = type(node).__name__
        steps.append(step)
    return steps


def show(name, steps):
    print(f"\n{name}({SORTED_LIST}, {VALUE})   pure-Python code from {SOURCE_FILE}")
    for s in steps:
        extra = ""
        if s.get("sides"):
            extra = "   (" + ", ".join(f"{k} = {v}" for k, v in s["sides"].items()) + ")"
        print(f"  line {s['line']:>3}  {s['code']:<36} # -> {s.get('value')!r}{extra}")


report = {
    "python": platform.python_version(),
    "source_file": SOURCE_FILE,
    "sorted_list": SORTED_LIST,
    "value": VALUE,
}

for func, c_func in ((bisect_py.bisect_left, c_bisect_left), (bisect_py.bisect_right, c_bisect_right)):
    result, events = run_traced(func, SORTED_LIST, VALUE)
    steps = describe(func, events)
    show(func.__name__, steps)
    comparisons = [s for s in steps if s["kind"] == "test" and s["test"] != "lo < hi" and "mid" in s["test"]]
    windows = [(s["before"]["lo"], s["before"]["hi"]) for s in steps if s.get("test") == "lo < hi"]
    c_result = c_func(SORTED_LIST, VALUE)
    report[func.__name__] = {
        "result": result,
        "c_result": c_result,
        "same_as_c": result == c_result,
        "comparisons": len(comparisons),
        "mids": [s["before"]["mid"] for s in comparisons],
        "compared_items": [s["sides"]["a[mid]"] for s in comparisons],
        "windows_at_loop_test": windows,
        "undecided_counts": [hi - lo for lo, hi in windows],
        "first_line_locals": steps[0]["before"],
        "steps": steps,
    }
    print(f"  result {result}, C version returns {c_result}, comparisons {len(comparisons)}")
    print(f"  (lo, hi) at each loop test: {windows}")

i = report["bisect_left"]["result"]
inserted = list(SORTED_LIST)
inserted.insert(i, VALUE)
report["split"] = {"left": SORTED_LIST[:i], "right": SORTED_LIST[i:],
                   "all_left_below": all(e < VALUE for e in SORTED_LIST[:i]),
                   "all_right_at_least": all(e >= VALUE for e in SORTED_LIST[i:])}
report["after_insert"] = inserted
report["after_insert_sorted"] = inserted == sorted(inserted)
print(f"\nsplit at {i}: a[:{i}] = {SORTED_LIST[:i]}, a[{i}:] = {SORTED_LIST[i:]}")
print(f"a.insert({i}, {VALUE}) -> {inserted}, still sorted: {report['after_insert_sorted']}")
print(f"python {report['python']}")

# 2. The check a reader would type: a fresh interpreter, the normal `import bisect` (the C version).
CHECK = ["import bisect", f"a = {SORTED_LIST}", "bisect.bisect_left", f"bisect.bisect_left(a, {VALUE})",
         f"a.insert(bisect.bisect_left(a, {VALUE}), {VALUE})", "a"]
DRIVER = r"""
import json, sys
ns, out = {}, []
for line in json.loads(sys.argv[1]):
    try:
        code = compile(line, "<check>", "eval")
    except SyntaxError:
        exec(line, ns)
        out.append(None)
    else:
        value = eval(code, ns)
        out.append(None if value is None else repr(value))
print(json.dumps(out))
"""
import subprocess  # noqa: E402

done = subprocess.run([sys.executable, "-I", "-c", DRIVER, json.dumps(CHECK)], capture_output=True, text=True, check=True)
report["check"] = [{"code": c, "value": v} for c, v in zip(CHECK, json.loads(done.stdout))]
print("\ncheck in a fresh interpreter:")
for row in report["check"]:
    print(f"  {row['code']:<44} # -> {row['value']}" if row["value"] is not None else f"  {row['code']}")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "trace.json"), "w") as f:
    json.dump(report, f, indent=1)
