"""Reference solver for the constraint IR used in the neuro-symbolic practical.

IR format (JSON):
{
  "variables":    {"Name": [lo, hi]  or  {"values": [v1, v2, ...]}},
  "all_different": [["A","B","C"], ...],
  "constraints":  ["A + 1 == B", "abs(C - D) == 2", "(X == 1) + (Y == 1) == 1", ...],
  "objective":    {"maximize": "expr"} | {"minimize": "expr"}   (optional)
}
Expression language: integer literals, variable names, + - * // %, comparisons,
and / or / not, abs(), parentheses. Booleans are coerced to 0/1 in arithmetic.
"""
import ast
import z3


def _as_int(e):
    return z3.If(e, 1, 0) if z3.is_bool(e) else e


def _as_bool(e):
    return e if z3.is_bool(e) else e != 0


class _Conv:
    def __init__(self, vars_):
        self.v = vars_

    def __call__(self, node):
        m = getattr(self, "_" + type(node).__name__, None)
        if m is None:
            raise ValueError(f"unsupported syntax: {type(node).__name__}")
        return m(node)

    def _Expression(self, n):
        return self(n.body)

    def _Name(self, n):
        if n.id not in self.v:
            raise ValueError(f"unknown variable: {n.id}")
        return self.v[n.id]

    def _Constant(self, n):
        if isinstance(n.value, bool):
            return z3.BoolVal(n.value)
        if isinstance(n.value, int):
            return z3.IntVal(n.value)
        raise ValueError("only integer constants allowed")

    def _UnaryOp(self, n):
        x = self(n.operand)
        if isinstance(n.op, ast.Not):
            return z3.Not(_as_bool(x))
        if isinstance(n.op, ast.USub):
            return -_as_int(x)
        if isinstance(n.op, ast.UAdd):
            return _as_int(x)
        raise ValueError("bad unary op")

    def _BinOp(self, n):
        a, b = _as_int(self(n.left)), _as_int(self(n.right))
        op = n.op
        if isinstance(op, ast.Add): return a + b
        if isinstance(op, ast.Sub): return a - b
        if isinstance(op, ast.Mult): return a * b
        if isinstance(op, ast.FloorDiv): return a / b      # z3 int division = floor for non-neg
        if isinstance(op, ast.Mod): return a % b
        raise ValueError("bad binary op")

    def _BoolOp(self, n):
        xs = [_as_bool(self(x)) for x in n.values]
        return z3.And(*xs) if isinstance(n.op, ast.And) else z3.Or(*xs)

    def _Compare(self, n):
        parts, left = [], self(n.left)
        for op, rnode in zip(n.ops, n.comparators):
            right = self(rnode)
            if z3.is_bool(left) and z3.is_bool(right) and isinstance(op, (ast.Eq, ast.NotEq)):
                l, r = left, right
            else:
                l, r = _as_int(left), _as_int(right)
            if isinstance(op, ast.Eq): parts.append(l == r)
            elif isinstance(op, ast.NotEq): parts.append(l != r)
            elif isinstance(op, ast.Lt): parts.append(l < r)
            elif isinstance(op, ast.LtE): parts.append(l <= r)
            elif isinstance(op, ast.Gt): parts.append(l > r)
            elif isinstance(op, ast.GtE): parts.append(l >= r)
            else: raise ValueError("bad comparison")
            left = right
        return z3.And(*parts) if len(parts) > 1 else parts[0]

    def _Call(self, n):
        if isinstance(n.func, ast.Name) and n.func.id == "abs" and len(n.args) == 1:
            x = _as_int(self(n.args[0]))
            return z3.If(x >= 0, x, -x)
        raise ValueError("only abs() is allowed")


def build(ir):
    zv, cons = {}, []
    for name, dom in ir["variables"].items():
        x = z3.Int(name)
        zv[name] = x
        if isinstance(dom, dict):                      # {"values": [...]}
            cons.append(z3.Or(*[x == d for d in dom["values"]]))
        else:                                          # [lo, hi] inclusive range
            lo, hi = dom
            cons += [x >= lo, x <= hi]
    for grp in ir.get("all_different", []):
        cons.append(z3.Distinct(*[zv[g] for g in grp]))
    conv = _Conv(zv)
    for c in ir.get("constraints", []):
        cons.append(_as_bool(conv(ast.parse(c, mode="eval"))))
    return zv, cons, conv


def solve(ir, limit=10):
    """Returns dict: status in {none, unique, multiple, optimal}, solutions, objective."""
    zv, cons, conv = build(ir)
    obj = ir.get("objective")
    if obj:
        (sense, expr), = obj.items()
        o = z3.Optimize()
        o.add(*cons)
        e = _as_int(conv(ast.parse(expr, mode="eval")))
        h = o.maximize(e) if sense == "maximize" else o.minimize(e)
        if o.check() != z3.sat:
            return {"status": "none", "solutions": []}
        m = o.model()
        best = m.eval(e).as_long()
        # count optimal solutions
        s = z3.Solver(); s.add(*cons); s.add(e == best)
        sols = _enum(s, zv, limit)
        return {"status": "optimal", "objective": best, "solutions": sols, "n_optimal": len(sols)}
    s = z3.Solver(); s.add(*cons)
    sols = _enum(s, zv, limit)
    st = "none" if not sols else ("unique" if len(sols) == 1 else "multiple")
    return {"status": st, "solutions": sols}


def _enum(s, zv, limit):
    out = []
    while len(out) < limit and s.check() == z3.sat:
        m = s.model()
        sol = {k: m.eval(v, model_completion=True).as_long() for k, v in zv.items()}
        out.append(sol)
        s.add(z3.Or(*[v != sol[k] for k, v in zv.items()]))
    return out
