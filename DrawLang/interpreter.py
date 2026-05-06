"""DrawLang interpreter.

Walks the Lark parse tree produced by grammar.lark and:
  - evaluates all expressions (arithmetic + logical)
  - executes control-flow (if/else, while, for, repeat, break, continue)
  - manages procedures (proc declaration, call, return)
  - tracks drawing state (canvas size, current color, transform stack)
  - collects SVG elements and serialises them at the end
"""
from __future__ import annotations

import math
from typing import Any

from lark import Tree, Token

# ---------------------------------------------------------------------------
# Signal exceptions used for control flow
# ---------------------------------------------------------------------------

class _Break(Exception):
    pass

class _Continue(Exception):
    pass

class _Return(Exception):
    def __init__(self, value):
        self.value = value

# ---------------------------------------------------------------------------
# Environment (variable scopes)
# ---------------------------------------------------------------------------

class Environment:
    def __init__(self, parent: "Environment | None" = None):
        self._vars: dict[str, Any] = {}
        self._parent = parent

    def get(self, name: str) -> Any:
        if name in self._vars:
            return self._vars[name]
        if self._parent:
            return self._parent.get(name)
        raise NameError(f"undefined variable: '{name}'")

    def set(self, name: str, value: Any) -> None:
        """Set in the scope where the variable is already defined, or locally."""
        if name in self._vars:
            self._vars[name] = value
        elif self._parent and self._parent._has(name):
            self._parent.set(name, value)
        else:
            self._vars[name] = value

    def define(self, name: str, value: Any) -> None:
        """Always define in the current (local) scope."""
        self._vars[name] = value

    def _has(self, name: str) -> bool:
        if name in self._vars:
            return True
        if self._parent:
            return self._parent._has(name)
        return False

# ---------------------------------------------------------------------------
# Interpreter
# ---------------------------------------------------------------------------

class Interpreter:
    def __init__(self):
        self._global_env = Environment()
        self._procs: dict[str, Tree] = {}   # name -> proc_decl Tree

        # SVG state
        self._width: int = 200
        self._height: int = 200
        self._color: str | None = None
        self._translate_x: float = 0.0
        self._translate_y: float = 0.0
        self._scale: float = 1.0
        self._elements: list[str] = []

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self, tree: Tree) -> str:
        """Execute the program tree and return an SVG string."""
        self._exec_block_children(tree.children, self._global_env)
        return self._build_svg()

    # ------------------------------------------------------------------
    # Statement execution
    # ------------------------------------------------------------------

    def _exec(self, node: Tree, env: Environment) -> None:
        name = node.data

        if name == "var_decl":
            ident = str(node.children[0])
            value = self._eval(node.children[1], env)
            env.define(ident, value)

        elif name == "assign_stmt":
            ident = str(node.children[0])
            value = self._eval(node.children[1], env)
            env.set(ident, value)

        elif name == "if_stmt":
            self._exec_if(node, env)

        elif name == "while_stmt":
            self._exec_while(node, env)

        elif name == "for_stmt":
            self._exec_for(node, env)

        elif name == "repeat_stmt":
            self._exec_repeat(node, env)

        elif name == "break_stmt":
            raise _Break()

        elif name == "continue_stmt":
            raise _Continue()

        elif name == "proc_decl":
            ident = str(node.children[0])
            self._procs[ident] = node

        elif name == "return_stmt":
            value = self._eval(node.children[0], env) if node.children and node.children[0] is not None else None
            raise _Return(value)

        elif name == "call_stmt":
            # Direct call evaluation since we inlined the call rule
            ident = str(node.children[0])
            args = []
            if len(node.children) > 1:
                args_node = node.children[1]
                if args_node and args_node.data == "args":
                    args = [self._eval(arg, env) for arg in args_node.children]
            self._eval_call_direct(ident, args, env)

        elif name == "canvas_stmt":
            self._width = int(self._eval(node.children[0], env))
            self._height = int(self._eval(node.children[1], env))

        elif name == "circle_stmt":
            x = self._eval(node.children[0], env)
            y = self._eval(node.children[1], env)
            r = self._eval(node.children[2], env)
            tx, ty = self._apply_transform(x, y)
            r2 = r * self._scale
            color_attr = self._color_attr()
            self._elements.append(
                f'  <circle cx="{_fmt(tx)}" cy="{_fmt(ty)}" r="{_fmt(r2)}"{color_attr} />'
            )

        elif name == "line_stmt":
            x1 = self._eval(node.children[0], env)
            y1 = self._eval(node.children[1], env)
            x2 = self._eval(node.children[2], env)
            y2 = self._eval(node.children[3], env)
            tx1, ty1 = self._apply_transform(x1, y1)
            tx2, ty2 = self._apply_transform(x2, y2)
            color_attr = self._color_attr("line")
            self._elements.append(
                f'  <line x1="{_fmt(tx1)}" y1="{_fmt(ty1)}"'
                f' x2="{_fmt(tx2)}" y2="{_fmt(ty2)}"{color_attr} />'
            )

        elif name == "rect_stmt":
            x = self._eval(node.children[0], env)
            y = self._eval(node.children[1], env)
            w = self._eval(node.children[2], env)
            h = self._eval(node.children[3], env)
            tx, ty = self._apply_transform(x, y)
            w2 = w * self._scale
            h2 = h * self._scale
            color_attr = self._color_attr()
            self._elements.append(
                f'  <rect x="{_fmt(tx)}" y="{_fmt(ty)}"'
                f' width="{_fmt(w2)}" height="{_fmt(h2)}"{color_attr} />'
            )

        elif name == "color_stmt":
            color_node = node.children[0]
            if color_node.data == "color_value":
                color_token = color_node.children[0]
                self._color = str(color_token).strip('"')
            else:
                self._color = str(color_node).strip('"')

        elif name == "translate_stmt":
            self._translate_x = float(self._eval(node.children[0], env))
            self._translate_y = float(self._eval(node.children[1], env))

        elif name == "scale_stmt":
            self._scale = float(self._eval(node.children[0], env))

        else:
            pass  # unknown node – silently skip

    def _exec_block_children(self, children, env: Environment) -> None:
        for child in children:
            if isinstance(child, Tree):
                self._exec(child, env)

    def _exec_block(self, block_node: Tree, env: Environment) -> None:
        """Execute a `block` node (which wraps statements in { })."""
        self._exec_block_children(block_node.children, env)

    def _exec_if(self, node: Tree, env: Environment) -> None:
        # if_stmt: expr block (else (if_stmt | block))?
        cond = self._eval(node.children[0], env)
        if _truthy(cond):
            self._exec_block(node.children[1], Environment(env))
        elif len(node.children) > 2:
            else_branch = node.children[2]
            if else_branch.data == "if_stmt":
                self._exec_if(else_branch, env)
            else:  # block
                self._exec_block(else_branch, Environment(env))

    def _exec_while(self, node: Tree, env: Environment) -> None:
        # while_stmt: expr block
        while _truthy(self._eval(node.children[0], env)):
            try:
                self._exec_block(node.children[1], Environment(env))
            except _Break:
                break
            except _Continue:
                continue

    def _exec_for(self, node: Tree, env: Environment) -> None:
        # for_stmt: IDENTIFIER "=" expr "to" expr ("step" expr)? block
        ident = str(node.children[0])
        start = self._eval(node.children[1], env)
        end   = self._eval(node.children[2], env)

        if len(node.children) == 4:
            step = 1
            block = node.children[3]
        else:
            step  = self._eval(node.children[3], env)
            block = node.children[4]

        i = start
        while i <= end:
            loop_env = Environment(env)
            loop_env.define(ident, i)
            try:
                self._exec_block(block, loop_env)
            except _Break:
                break
            except _Continue:
                pass
            i += step

    def _exec_repeat(self, node: Tree, env: Environment) -> None:
        # repeat_stmt: expr block
        count = int(self._eval(node.children[0], env))
        for _ in range(count):
            try:
                self._exec_block(node.children[1], Environment(env))
            except _Break:
                break
            except _Continue:
                continue

    # ------------------------------------------------------------------
    # Expression evaluation
    # ------------------------------------------------------------------

    def _eval(self, node, env: Environment) -> Any:
        if isinstance(node, Token):
            return _token_value(node)

        name = node.data

        if name == "number":
            return _token_value(node.children[0])

        if name == "string":
            raw = str(node.children[0])
            return raw.strip('"')

        if name == "bool_lit":
            return str(node.children[0]) == "true"

        if name == "var":
            return env.get(str(node.children[0]))

        if name == "call":
            return self._eval_call(node, env)

        # Arithmetic
        if name == "neg":
            return -self._eval(node.children[0], env)

        if name == "add_op":
            return str(node.children[0])

        if name == "mul_op":
            return str(node.children[0])

        if name == "sum":
            return self._eval_binop(node, env)

        if name == "product":
            return self._eval_binop(node, env)

        # Logic
        if name == "or_expr":
            return self._eval_logic_chain(node, env, "or")

        if name == "and_expr":
            return self._eval_logic_chain(node, env, "and")

        if name == "not_op":
            return not _truthy(self._eval(node.children[0], env))

        if name == "logical_comparison":
            return self._eval_comparison(node, env)

        if name == "cmp_op":
            return str(node.children[0])

        # Fallback: single child passthrough
        if len(node.children) == 1:
            return self._eval(node.children[0], env)

        raise RuntimeError(f"don't know how to evaluate node: {name}")

    def _eval_binop(self, node: Tree, env: Environment) -> Any:
        """Evaluate left-associative binary operator chains like sum / product."""
        result = self._eval(node.children[0], env)
        i = 1
        while i < len(node.children):
            op   = str(node.children[i].children[0])
            rhs  = self._eval(node.children[i + 1], env)
            result = _apply_arith(op, result, rhs)
            i += 2
        return result

    def _eval_logic_chain(self, node: Tree, env: Environment, kind: str) -> Any:
        result = self._eval(node.children[0], env)
        i = 1
        while i < len(node.children):
            rhs = self._eval(node.children[i], env)
            if kind == "or":
                result = _truthy(result) or _truthy(rhs)
            else:
                result = _truthy(result) and _truthy(rhs)
            i += 1
        return result

    def _eval_comparison(self, node: Tree, env: Environment) -> bool:
        lhs = self._eval(node.children[0], env)
        if len(node.children) == 1:
            return _truthy(lhs)
        op  = str(node.children[1].children[0])
        rhs = self._eval(node.children[2], env)
        ops = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "<":  lambda a, b: a <  b,
            ">":  lambda a, b: a >  b,
            "<=": lambda a, b: a <= b,
            ">=": lambda a, b: a >= b,
        }
        return ops[op](lhs, rhs)

    def _eval_call(self, node: Tree, env: Environment) -> Any:
        ident = str(node.children[0])

        # Evaluate arguments
        args: list[Any] = []
        if len(node.children) > 1:
            args_node = node.children[1]  # args node
            for arg in args_node.children:
                args.append(self._eval(arg, env))

        # Built-in math functions
        builtins = {
            "sin":   lambda a: math.sin(math.radians(a)),
            "cos":   lambda a: math.cos(math.radians(a)),
            "tan":   lambda a: math.tan(math.radians(a)),
            "sqrt":  lambda a: math.sqrt(a),
            "abs":   lambda a: abs(a),
            "floor": lambda a: math.floor(a),
            "ceil":  lambda a: math.ceil(a),
            "round": lambda a: round(a),
            "min":   lambda a, b: min(a, b),
            "max":   lambda a, b: max(a, b),
        }
        if ident in builtins:
            return builtins[ident](*args)

        # User-defined procedure
        if ident not in self._procs:
            raise NameError(f"undefined procedure: '{ident}'")

        proc = self._procs[ident]
        # proc_decl: IDENTIFIER params? block
        # children: [name, (params), block]  or [name, block]
        if isinstance(proc.children[-1], Tree) and proc.children[-1].data == "block":
            block = proc.children[-1]
            params_node = proc.children[1] if len(proc.children) > 2 else None
        else:
            block = proc.children[-1]
            params_node = None

        param_names: list[str] = []
        if params_node and params_node.data == "params":
            param_names = [str(t) for t in params_node.children]

        if len(args) != len(param_names):
            raise TypeError(
                f"procedure '{ident}' expects {len(param_names)} args, got {len(args)}"
            )

        call_env = Environment(self._global_env)
        for pname, pval in zip(param_names, args):
            call_env.define(pname, pval)

        try:
            self._exec_block(block, call_env)
        except _Return as ret:
            return ret.value

        return None

    def _eval_call_direct(self, ident: str, args: list[Any], env: Environment) -> Any:
        # Built-in math functions
        builtins = {
            "sin": lambda a: math.sin(math.radians(a)),
            "cos": lambda a: math.cos(math.radians(a)),
            "sqrt": lambda a: math.sqrt(a),
            "abs": lambda a: abs(a),
            "round": lambda a: round(a),
            "min": lambda a, b: min(a, b),
            "max": lambda a, b: max(a, b),
        }
        if ident in builtins:
            return builtins[ident](*args)

        # User-defined procedure
        if ident not in self._procs:
            raise NameError(f"undefined procedure: '{ident}'")

        proc = self._procs[ident]
        # proc_decl: IDENTIFIER params? block
        # children: [name, (params), block]  or [name, block]
        if isinstance(proc.children[-1], Tree) and proc.children[-1].data == "block":
            block = proc.children[-1]
            params_node = proc.children[1] if len(proc.children) > 2 else None
        else:
            block = proc.children[-1]
            params_node = None

        param_names: list[str] = []
        if params_node and params_node.data == "params":
            param_names = [str(t) for t in params_node.children]

        if len(args) != len(param_names):
            raise TypeError(
                f"procedure '{ident}' expects {len(param_names)} args, got {len(args)}"
            )

        call_env = Environment(self._global_env)
        for pname, pval in zip(param_names, args):
            call_env.define(pname, pval)

        try:
            self._exec_block(block, call_env)
        except _Return as ret:
            return ret.value

        return None

    # ------------------------------------------------------------------
    # SVG helpers
    # ------------------------------------------------------------------

    def _apply_transform(self, x: float, y: float) -> tuple[float, float]:
        return (
            self._translate_x + x * self._scale,
            self._translate_y + y * self._scale,
        )

    def _color_attr(self, shape_type: str = "fill") -> str:
        if self._color is None:
            return ""
        if shape_type == "line":
            return f' stroke="{self._color}"'
        else:
            return f' stroke="{self._color}" fill="{self._color}"'

    def _build_svg(self) -> str:
        inner = "\n".join(self._elements)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self._width}" height="{self._height}">\n'
            f'{inner}\n'
            f'</svg>\n'
        )

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _token_value(token: Token) -> Any:
    s = str(token)
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s

def _truthy(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    return bool(val)

def _apply_arith(op: str, a: Any, b: Any) -> Any:
    if op == "+": return a + b
    if op == "-": return a - b
    if op == "*": return a * b
    if op == "/": return a / b if b != 0 else 0
    if op == "%": return a % b
    raise RuntimeError(f"unknown operator: {op}")

def _fmt(v: float) -> str:
    """Format number: drop .0 for whole numbers."""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return f"{v:.4g}"