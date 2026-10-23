"""Print the annotated code blocks for index.html from trace.json, so no value is copied by hand.

Run after trace.py:  python3 codeblocks.py
Each block is the real source lines of Lib/bisect.py, with the value each line produced on this
run (`# -> value`), the plain-words notes added for the page, and grey lines that did not run.
"""
import html
import json
import linecache
import os

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, "trace.json")))
SRC = T["source_file"]
STEPS = T["bisect_left"]["steps"]


def src(n):
    return linecache.getline(SRC, n).rstrip("\n")


def annotation(step):
    v = step["value"]
    if step["kind"] == "test" and " < " in step["test"]:
        # the test with each name replaced by its value, such as `a[mid] < x` -> `15 < 8`
        shown = step["test"]
        for name, value in step["sides"].items():
            shown = shown.replace(name, repr(value))
        return f"# -> {v!r}  ({shown})"
    return f"# -> {v!r}"


def block(rows, dedent, col):
    """rows: (kind, payload). kind 'run' = (lineno, step), 'skip' = lineno, 'src' = lineno, 'add' = text."""
    out = []
    for kind, p in rows:
        if kind == "add":
            out.append(f'<span class="add">{html.escape(p)}</span>')
            continue
        n = p[0] if kind == "run" else p
        text = src(n)[dedent:]
        if kind == "run":
            pad = " " * max(1, col - len(text))
            out.append(f'<span class="ln" data-n="{n}">{html.escape(text)}{pad}'
                       f'<span class="v">{html.escape(annotation(p[1]))}</span></span>')
        else:
            cls = "ln skip" if kind == "skip" else "ln cm" if text.strip().startswith("#") else "ln"
            out.append(f'<span class="{cls}" data-n="{n}">{html.escape(text)}</span>')
    return "<pre class=\"code\"><code>" + "\n".join(out) + "</code></pre>"


by_line = {}
for s in STEPS:
    by_line.setdefault(s["line"], []).append(s)

a, x = T["sorted_list"], T["value"]
setup = [
    ("src", 74),
    ("add", f"    # The call: bisect_left({a}, {x})"),
    ("add", f"    # -> a = {a}, x = {x}"),
    ("add", "    #    lo = 0, hi = None, key = None"),
    ("add", "    # (75 to 86: the docstring and a blank line)"),
    ("add", "    # Refuse a negative start index."),
    ("run", (87, by_line[87][0])),
    ("skip", 88),
    ("add", "    # No hi given: search to the end of the list."),
    ("run", (89, by_line[89][0])),
    ("run", (90, by_line[90][0])),
    ("src", 91),
    ("src", 92),
    ("add", "    # key is None: compare the items themselves."),
    ("run", (93, by_line[93][0])),
]
print("=== setup\n" + block(setup, 0, 24))


def iteration(k):
    """Rows for the k-th pass through the loop (k = 0, 1, 2), dedented by 8 spaces."""
    test, mid, cmp = by_line[94][k], by_line[95][k], by_line[96][k]
    went_left = cmp["value"]  # a[mid] < x is True -> lo moves
    move = [s for s in STEPS if s["line"] in (97, 99)][k]
    rows = [
        ("add", "# Go on while some item is undecided."),
        ("run", (94, test)),
        ("add", "    # Pick the middle undecided item."),
        ("run", (95, mid)),
        ("add", "    # Is a[mid] below 8? The list is sorted, so"),
        ("add", "    # this also settles all items on one side of it."),
        ("run", (96, cmp)),
    ]
    if went_left:
        rows += [("add", "        # a[mid] and all left of it are below 8."),
                 ("run", (97, move)), ("skip", 98), ("skip", 99)]
    else:
        rows += [("skip", 97), ("src", 98),
                 ("add", "        # a[mid] and all right of it are 8 or more."),
                 ("run", (99, move))]
    return rows


for k in range(3):
    print(f"=== comparison {k + 1}\n" + block(iteration(k), 8, 26))

end = [
    ("add", "    # No item is undecided, so the loop ends."),
    ("run", (94, by_line[94][3])),
    ("add", "# lo is the insertion point."),
    ("run", (107, by_line[107][0])),
]
print("=== return\n" + block(end, 4, 26))

# The check, typed into a fresh interpreter by trace.py: no line numbers, since it is not bisect.py.
rows = []
for row in T["check"]:
    code = html.escape(row["code"])
    if row["value"] is None:
        rows.append(f'<span class="ln">{code}</span>')
    else:
        pad = " " * max(1, 26 - len(row["code"]))
        rows.append(f'<span class="ln">{code}{pad}<span class="v">{html.escape("# -> " + row["value"])}</span></span>')
print("=== check\n<pre class=\"code plain\"><code>" + "\n".join(rows) + "</code></pre>")
