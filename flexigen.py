#!/usr/bin/env python3
"""
Flexigen Interpreter
CS 420 - Spring 2026
Authors: Nikhil Maharaj, Ryan Collins, Chris Sapien

A self-adapting programming language interpreter.
"""

import io
import sys
import re
from typing import Any, Dict, List, Optional, Tuple, Union

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)


# ─────────────────────────────────────────────
#  TOKEN TYPES
# ─────────────────────────────────────────────
class TT:
    INT = "INT"; FLOAT = "FLOAT"; STRING = "STRING"; BOOL = "BOOL"
    IDENT = "IDENT"; PLUS = "PLUS"; MINUS = "MINUS"; STAR = "STAR"
    SLASH = "SLASH"; PERCENT = "PERCENT"; EQ = "EQ"; EQEQ = "EQEQ"
    NEQ = "NEQ"; LT = "LT"; GT = "GT"; LTE = "LTE"; GTE = "GTE"
    LPAREN = "LPAREN"; RPAREN = "RPAREN"; LBRACE = "LBRACE"; RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"; RBRACKET = "RBRACKET"; COMMA = "COMMA"
    COLON = "COLON"; ARROW = "ARROW"; SEMICOLON = "SEMICOLON"
    LET = "LET"; MUT = "MUT"; FN = "FN"; RETURN = "RETURN"
    IF = "IF"; ELSE = "ELSE"; WHILE = "WHILE"; FOR = "FOR"; IN = "IN"
    PRINT = "PRINT"; TRUE = "TRUE"; FALSE = "FALSE"
    ADAPTIVE = "ADAPTIVE"; SPEC = "SPEC"; BASELINE = "BASELINE"
    VARIANT = "VARIANT"; WHEN = "WHEN"; ENSURE = "ENSURE"
    OPTIMIZE = "OPTIMIZE"; KEEP = "KEEP"; PROPOSE = "PROPOSE"
    AND = "AND"; OR = "OR"; NOT = "NOT"
    EOF = "EOF"


class Token:
    def __init__(self, type: str, value: Any, line: int = 0):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


# ─────────────────────────────────────────────
#  LEXER
# ─────────────────────────────────────────────
KEYWORDS = {
    "let": TT.LET, "mut": TT.MUT, "fn": TT.FN, "return": TT.RETURN,
    "if": TT.IF, "else": TT.ELSE, "while": TT.WHILE, "for": TT.FOR,
    "in": TT.IN, "print": TT.PRINT, "true": TT.TRUE, "false": TT.FALSE,
    "adaptive": TT.ADAPTIVE, "spec": TT.SPEC, "baseline": TT.BASELINE,
    "variant": TT.VARIANT, "when": TT.WHEN, "ensure": TT.ENSURE,
    "optimize": TT.OPTIMIZE, "keep": TT.KEEP, "propose": TT.PROPOSE,
    "and": TT.AND, "or": TT.OR, "not": TT.NOT,
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens: List[Token] = []

    def error(self, msg):
        raise SyntaxError(f"[Lexer] Line {self.line}: {msg}")

    def peek(self, offset=0):
        p = self.pos + offset
        return self.source[p] if p < len(self.source) else "\0"

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def skip_whitespace_and_comments(self):
        while self.pos < len(self.source):
            ch = self.peek()
            if ch in " \t\r\n":
                self.advance()
            elif ch == "/" and self.peek(1) == "/":
                while self.pos < len(self.source) and self.peek() != "\n":
                    self.advance()
            else:
                break

    def read_string(self):
        self.advance()  # opening "
        result = ""
        while self.pos < len(self.source) and self.peek() != '"':
            result += self.advance()
        if self.pos >= len(self.source):
            self.error("Unterminated string")
        self.advance()  # closing "
        return result

    def read_number(self):
        start = self.pos
        while self.peek().isdigit():
            self.advance()
        if self.peek() == "." and self.peek(1).isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
            return float(self.source[start:self.pos])
        return int(self.source[start:self.pos])

    def tokenize(self) -> List[Token]:
        while True:
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                self.tokens.append(Token(TT.EOF, None, self.line))
                break

            ch = self.peek()
            line = self.line

            if ch == '"':
                val = self.read_string()
                self.tokens.append(Token(TT.STRING, val, line))
            elif ch.isdigit():
                val = self.read_number()
                tt = TT.FLOAT if isinstance(val, float) else TT.INT
                self.tokens.append(Token(tt, val, line))
            elif ch.isalpha() or ch == "_":
                start = self.pos
                while self.peek().isalnum() or self.peek() == "_":
                    self.advance()
                word = self.source[start:self.pos]
                tt = KEYWORDS.get(word, TT.IDENT)
                self.tokens.append(Token(tt, word, line))
            elif ch == "+":
                self.advance(); self.tokens.append(Token(TT.PLUS, "+", line))
            elif ch == "-":
                self.advance()
                if self.peek() == ">":
                    self.advance(); self.tokens.append(Token(TT.ARROW, "->", line))
                else:
                    self.tokens.append(Token(TT.MINUS, "-", line))
            elif ch == "*":
                self.advance(); self.tokens.append(Token(TT.STAR, "*", line))
            elif ch == "/":
                self.advance(); self.tokens.append(Token(TT.SLASH, "/", line))
            elif ch == "%":
                self.advance(); self.tokens.append(Token(TT.PERCENT, "%", line))
            elif ch == "=":
                self.advance()
                if self.peek() == "=":
                    self.advance(); self.tokens.append(Token(TT.EQEQ, "==", line))
                else:
                    self.tokens.append(Token(TT.EQ, "=", line))
            elif ch == "!":
                self.advance()
                if self.peek() == "=":
                    self.advance(); self.tokens.append(Token(TT.NEQ, "!=", line))
                else:
                    self.error(f"Unexpected '!'")
            elif ch == "<":
                self.advance()
                if self.peek() == "=":
                    self.advance(); self.tokens.append(Token(TT.LTE, "<=", line))
                else:
                    self.tokens.append(Token(TT.LT, "<", line))
            elif ch == ">":
                self.advance()
                if self.peek() == "=":
                    self.advance(); self.tokens.append(Token(TT.GTE, ">=", line))
                else:
                    self.tokens.append(Token(TT.GT, ">", line))
            elif ch == "(":
                self.advance(); self.tokens.append(Token(TT.LPAREN, "(", line))
            elif ch == ")":
                self.advance(); self.tokens.append(Token(TT.RPAREN, ")", line))
            elif ch == "{":
                self.advance(); self.tokens.append(Token(TT.LBRACE, "{", line))
            elif ch == "}":
                self.advance(); self.tokens.append(Token(TT.RBRACE, "}", line))
            elif ch == "[":
                self.advance(); self.tokens.append(Token(TT.LBRACKET, "[", line))
            elif ch == "]":
                self.advance(); self.tokens.append(Token(TT.RBRACKET, "]", line))
            elif ch == ",":
                self.advance(); self.tokens.append(Token(TT.COMMA, ",", line))
            elif ch == ":":
                self.advance(); self.tokens.append(Token(TT.COLON, ":", line))
            elif ch == ";":
                self.advance(); self.tokens.append(Token(TT.SEMICOLON, ";", line))
            else:
                self.error(f"Unexpected character: {ch!r}")

        return self.tokens


# ─────────────────────────────────────────────
#  AST NODES
# ─────────────────────────────────────────────
class Node:
    pass


class Program(Node):
    def __init__(self, stmts): self.stmts = stmts

class LetStmt(Node):
    def __init__(self, name, type_ann, value, mutable=False):
        self.name = name; self.type_ann = type_ann
        self.value = value; self.mutable = mutable

class AssignStmt(Node):
    def __init__(self, name, value): self.name = name; self.value = value

class FnDef(Node):
    def __init__(self, name, params, ret_type, body, adaptive=False, spec=None, variants=None):
        self.name = name; self.params = params; self.ret_type = ret_type
        self.body = body; self.adaptive = adaptive
        self.spec = spec or {}; self.variants = variants or []

class ReturnStmt(Node):
    def __init__(self, value): self.value = value

class IfStmt(Node):
    def __init__(self, cond, then_body, else_body=None):
        self.cond = cond; self.then_body = then_body; self.else_body = else_body

class WhileStmt(Node):
    def __init__(self, cond, body): self.cond = cond; self.body = body

class ForStmt(Node):
    def __init__(self, var, iterable, body):
        self.var = var; self.iterable = iterable; self.body = body

class PrintStmt(Node):
    def __init__(self, value): self.value = value

class ExprStmt(Node):
    def __init__(self, expr): self.expr = expr

class BinOp(Node):
    def __init__(self, left, op, right): self.left = left; self.op = op; self.right = right

class UnaryOp(Node):
    def __init__(self, op, operand): self.op = op; self.operand = operand

class Literal(Node):
    def __init__(self, value): self.value = value

class Identifier(Node):
    def __init__(self, name): self.name = name

class Call(Node):
    def __init__(self, name, args): self.name = name; self.args = args

class IndexAccess(Node):
    def __init__(self, obj, index): self.obj = obj; self.index = index

class ListLiteral(Node):
    def __init__(self, elements): self.elements = elements

class SpecBlock(Node):
    def __init__(self, directives): self.directives = directives

class VariantDecl(Node):
    def __init__(self, name, condition=None): self.name = name; self.condition = condition


# ─────────────────────────────────────────────
#  PARSER
# ─────────────────────────────────────────────
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0) -> Token:
        p = self.pos + offset
        return self.tokens[p] if p < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, tt: str) -> Token:
        tok = self.advance()
        if tok.type != tt:
            raise SyntaxError(f"[Parser] Line {tok.line}: Expected {tt}, got {tok.type} ({tok.value!r})")
        return tok

    def check(self, *types) -> bool:
        return self.peek().type in types

    def match(self, *types) -> Optional[Token]:
        if self.check(*types):
            return self.advance()
        return None

    def parse(self) -> Program:
        stmts = []
        while not self.check(TT.EOF):
            stmts.append(self.parse_stmt())
        return Program(stmts)

    def parse_stmt(self) -> Node:
        tok = self.peek()

        if tok.type == TT.LET or tok.type == TT.MUT:
            return self.parse_let()
        elif tok.type == TT.FN:
            return self.parse_fn()
        elif tok.type == TT.ADAPTIVE:
            return self.parse_adaptive_fn()
        elif tok.type == TT.RETURN:
            return self.parse_return()
        elif tok.type == TT.IF:
            return self.parse_if()
        elif tok.type == TT.WHILE:
            return self.parse_while()
        elif tok.type == TT.FOR:
            return self.parse_for()
        elif tok.type == TT.PRINT:
            return self.parse_print()
        elif tok.type == TT.PROPOSE:
            return self.parse_propose()
        else:
            # could be assignment or expr
            return self.parse_assign_or_expr()

    def parse_let(self) -> LetStmt:
        mutable = self.peek().type == TT.MUT
        self.advance()
        name = self.expect(TT.IDENT).value
        type_ann = None
        if self.match(TT.COLON):
            type_ann = self.parse_type()
        self.expect(TT.EQ)
        value = self.parse_expr()
        return LetStmt(name, type_ann, value, mutable)

    def parse_type(self) -> str:
        base = self.advance().value
        if self.match(TT.LT):
            inner = self.parse_type()
            if self.check(TT.COMMA):
                self.advance()
                inner2 = self.parse_type()
                inner = f"{inner},{inner2}"
            self.expect(TT.GT)
            return f"{base}<{inner}>"
        return base

    def parse_fn(self) -> FnDef:
        self.expect(TT.FN)
        name = self.expect(TT.IDENT).value
        params = self.parse_params()
        ret_type = None
        if self.match(TT.ARROW):
            ret_type = self.parse_type()
        body = self.parse_block()
        return FnDef(name, params, ret_type, body)

    def parse_adaptive_fn(self) -> FnDef:
        self.expect(TT.ADAPTIVE)
        self.expect(TT.FN)
        name = self.expect(TT.IDENT).value
        params = self.parse_params()
        ret_type = None
        if self.match(TT.ARROW):
            ret_type = self.parse_type()
        self.expect(TT.LBRACE)
        spec = {}
        variants = []
        baseline_body = None

        while not self.check(TT.RBRACE) and not self.check(TT.EOF):
            if self.check(TT.SPEC):
                spec = self.parse_spec_block()
            elif self.check(TT.BASELINE):
                self.advance()
                self.expect(TT.LBRACE)
                # baseline is a call expression
                expr = self.parse_expr()
                self.expect(TT.RBRACE)
                baseline_body = [ReturnStmt(expr)]
            elif self.check(TT.VARIANT):
                variants.append(self.parse_variant())
            else:
                self.advance()  # skip unknown

        self.expect(TT.RBRACE)
        return FnDef(name, params, ret_type, baseline_body or [], adaptive=True, spec=spec, variants=variants)

    def parse_spec_block(self) -> dict:
        self.expect(TT.SPEC)
        self.expect(TT.LBRACE)
        directives = {}
        while not self.check(TT.RBRACE) and not self.check(TT.EOF):
            if self.check(TT.ENSURE):
                self.advance()
                val = self.collect_until([TT.SEMICOLON, TT.OPTIMIZE, TT.KEEP, TT.RBRACE])
                directives["ensure"] = val
            elif self.check(TT.OPTIMIZE):
                self.advance()
                val = self.collect_until([TT.SEMICOLON, TT.ENSURE, TT.KEEP, TT.RBRACE])
                directives["optimize"] = val
            elif self.check(TT.KEEP):
                self.advance()
                val = self.collect_until([TT.SEMICOLON, TT.ENSURE, TT.OPTIMIZE, TT.RBRACE])
                directives["keep"] = val
            elif self.match(TT.SEMICOLON):
                pass
            else:
                self.advance()
        self.expect(TT.RBRACE)
        return directives

    def collect_until(self, stop_types) -> str:
        parts = []
        while not self.check(*stop_types) and not self.check(TT.EOF):
            parts.append(self.advance().value)
        return " ".join(str(p) for p in parts)

    def parse_variant(self) -> VariantDecl:
        self.expect(TT.VARIANT)
        name = self.advance().value  # variant name (could be ident or keyword-like)
        condition = None
        if self.check(TT.WHEN):
            self.advance()
            parts = []
            while not self.check(TT.VARIANT) and not self.check(TT.RBRACE) and not self.check(TT.EOF) and not self.check(TT.SPEC) and not self.check(TT.BASELINE):
                parts.append(self.advance().value)
            condition = " ".join(str(p) for p in parts)
        return VariantDecl(name, condition)

    def parse_propose(self) -> Node:
        # Skip propose blocks (AI variant proposals)
        while not self.check(TT.RBRACE) and not self.check(TT.EOF):
            self.advance()
        if self.check(TT.RBRACE):
            self.advance()
        return ExprStmt(Literal(None))

    def parse_params(self) -> List[Tuple[str, str]]:
        self.expect(TT.LPAREN)
        params = []
        while not self.check(TT.RPAREN) and not self.check(TT.EOF):
            name = self.expect(TT.IDENT).value
            type_ann = None
            if self.match(TT.COLON):
                type_ann = self.parse_type()
            params.append((name, type_ann))
            self.match(TT.COMMA)
        self.expect(TT.RPAREN)
        return params

    def parse_block(self) -> List[Node]:
        self.expect(TT.LBRACE)
        stmts = []
        while not self.check(TT.RBRACE) and not self.check(TT.EOF):
            stmts.append(self.parse_stmt())
        self.expect(TT.RBRACE)
        return stmts

    def parse_return(self) -> ReturnStmt:
        self.expect(TT.RETURN)
        value = self.parse_expr()
        return ReturnStmt(value)

    def parse_if(self) -> IfStmt:
        self.expect(TT.IF)
        cond = self.parse_expr()
        then_body = self.parse_block()
        else_body = None
        if self.match(TT.ELSE):
            if self.check(TT.IF):
                else_body = [self.parse_if()]
            else:
                else_body = self.parse_block()
        return IfStmt(cond, then_body, else_body)

    def parse_while(self) -> WhileStmt:
        self.expect(TT.WHILE)
        cond = self.parse_expr()
        body = self.parse_block()
        return WhileStmt(cond, body)

    def parse_for(self) -> ForStmt:
        self.expect(TT.FOR)
        var = self.expect(TT.IDENT).value
        self.expect(TT.IN)
        iterable = self.parse_expr()
        body = self.parse_block()
        return ForStmt(var, iterable, body)

    def parse_print(self) -> PrintStmt:
        self.expect(TT.PRINT)
        self.expect(TT.LPAREN)
        value = self.parse_expr()
        self.expect(TT.RPAREN)
        return PrintStmt(value)

    def parse_assign_or_expr(self) -> Node:
        expr = self.parse_expr()
        if self.match(TT.EQ):
            if isinstance(expr, Identifier):
                value = self.parse_expr()
                return AssignStmt(expr.name, value)
        return ExprStmt(expr)

    def parse_expr(self) -> Node:
        return self.parse_or()

    def parse_or(self) -> Node:
        left = self.parse_and()
        while self.check(TT.OR):
            op = self.advance().value
            right = self.parse_and()
            left = BinOp(left, op, right)
        return left

    def parse_and(self) -> Node:
        left = self.parse_equality()
        while self.check(TT.AND):
            op = self.advance().value
            right = self.parse_equality()
            left = BinOp(left, op, right)
        return left

    def parse_equality(self) -> Node:
        left = self.parse_comparison()
        while self.check(TT.EQEQ, TT.NEQ):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinOp(left, op, right)
        return left

    def parse_comparison(self) -> Node:
        left = self.parse_addition()
        while self.check(TT.LT, TT.GT, TT.LTE, TT.GTE):
            op = self.advance().value
            right = self.parse_addition()
            left = BinOp(left, op, right)
        return left

    def parse_addition(self) -> Node:
        left = self.parse_multiplication()
        while self.check(TT.PLUS, TT.MINUS):
            op = self.advance().value
            right = self.parse_multiplication()
            left = BinOp(left, op, right)
        return left

    def parse_multiplication(self) -> Node:
        left = self.parse_unary()
        while self.check(TT.STAR, TT.SLASH, TT.PERCENT):
            op = self.advance().value
            right = self.parse_unary()
            left = BinOp(left, op, right)
        return left

    def parse_unary(self) -> Node:
        if self.check(TT.NOT):
            op = self.advance().value
            return UnaryOp(op, self.parse_unary())
        if self.check(TT.MINUS):
            op = self.advance().value
            return UnaryOp(op, self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self) -> Node:
        expr = self.parse_primary()
        while True:
            if self.check(TT.LBRACKET):
                self.advance()
                index = self.parse_expr()
                self.expect(TT.RBRACKET)
                expr = IndexAccess(expr, index)
            else:
                break
        return expr

    def parse_primary(self) -> Node:
        tok = self.peek()

        if tok.type == TT.INT:
            self.advance(); return Literal(tok.value)
        if tok.type == TT.FLOAT:
            self.advance(); return Literal(tok.value)
        if tok.type == TT.STRING:
            self.advance(); return Literal(tok.value)
        if tok.type == TT.TRUE:
            self.advance(); return Literal(True)
        if tok.type == TT.FALSE:
            self.advance(); return Literal(False)

        if tok.type == TT.IDENT:
            # List literal: List<Int>[1,2,3]
            if tok.value == "List":
                self.advance()
                if self.check(TT.LT):
                    self.advance()
                    # consume inner type tokens until >
                    depth = 1
                    while depth > 0 and not self.check(TT.EOF):
                        if self.check(TT.LT):
                            depth += 1
                        elif self.check(TT.GT):
                            depth -= 1
                        self.advance()
                self.expect(TT.LBRACKET)
                elements = []
                while not self.check(TT.RBRACKET) and not self.check(TT.EOF):
                    elements.append(self.parse_expr())
                    self.match(TT.COMMA)
                self.expect(TT.RBRACKET)
                return ListLiteral(elements)

            self.advance()
            if self.check(TT.LPAREN):
                # function call
                self.advance()
                args = []
                while not self.check(TT.RPAREN) and not self.check(TT.EOF):
                    args.append(self.parse_expr())
                    self.match(TT.COMMA)
                self.expect(TT.RPAREN)
                return Call(tok.value, args)
            return Identifier(tok.value)

        if tok.type == TT.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TT.RPAREN)
            return expr

        self.advance()
        return Literal(None)


# ─────────────────────────────────────────────
#  RETURN SIGNAL
# ─────────────────────────────────────────────
class ReturnSignal(Exception):
    def __init__(self, value): self.value = value


# ─────────────────────────────────────────────
#  ENVIRONMENT
# ─────────────────────────────────────────────
class Environment:
    def __init__(self, parent=None):
        self.vars: Dict[str, Any] = {}
        self.parent = parent

    def get(self, name: str) -> Any:
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined variable: '{name}'")

    def set(self, name: str, value: Any):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent and self.parent.has(name):
            self.parent.set(name, value)
        else:
            self.vars[name] = value

    def define(self, name: str, value: Any):
        self.vars[name] = value

    def has(self, name: str) -> bool:
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.has(name)
        return False


# ─────────────────────────────────────────────
#  ADAPTIVE RUNTIME
# ─────────────────────────────────────────────
class AdaptationReport:
    def __init__(self):
        self.entries: List[str] = []

    def log(self, fn_name: str, chosen: str, reason: str):
        entry = f"[AdaptReport] {fn_name}: selected '{chosen}' — {reason}"
        self.entries.append(entry)

    def dump(self):
        if self.entries:
            print("\n── Adaptation Report ──")
            for e in self.entries:
                print(e)
            print("───────────────────────\n")


REPORT = AdaptationReport()


# ─────────────────────────────────────────────
#  BUILT-IN FUNCTIONS
# ─────────────────────────────────────────────
def builtin_len(args):
    if len(args) != 1:
        raise TypeError("len() takes 1 argument")
    val = args[0]
    if isinstance(val, list):
        return len(val)
    if isinstance(val, str):
        return len(val)
    raise TypeError(f"len() not supported for {type(val)}")

def builtin_max(args):
    if len(args) == 1 and isinstance(args[0], list):
        return max(args[0])
    return max(args)

def builtin_min(args):
    if len(args) == 1 and isinstance(args[0], list):
        return min(args[0])
    return min(args)

def builtin_sorted_check(args):
    if not args or not isinstance(args[0], list):
        return False
    xs = args[0]
    return all(xs[i] <= xs[i+1] for i in range(len(xs)-1))

def builtin_mostly_sorted(args):
    if not args or not isinstance(args[0], list):
        return False
    xs = args[0]
    if len(xs) < 2:
        return True
    inversions = sum(1 for i in range(len(xs)-1) if xs[i] > xs[i+1])
    return inversions / len(xs) < 0.2

def builtin_merge_sort(xs):
    if len(xs) <= 1:
        return xs[:]
    mid = len(xs) // 2
    left = builtin_merge_sort(xs[:mid])
    right = builtin_merge_sort(xs[mid:])
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:]); result.extend(right[j:])
    return result

def builtin_insertion_sort(xs):
    arr = xs[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

def builtin_nested_scan(xs):
    for i in range(len(xs)):
        for j in range(i+1, len(xs)):
            if xs[i] == xs[j]:
                return True
    return False

def builtin_hashset_scan(xs):
    return len(xs) != len(set(xs))

BUILTINS = {
    "len": builtin_len,
    "max": builtin_max,
    "min": builtin_min,
    "sorted": builtin_sorted_check,
    "mostly_sorted": lambda args: builtin_mostly_sorted(args),
    "merge_sort": lambda args: builtin_merge_sort(args[0]),
    "insertion_sort": lambda args: builtin_insertion_sort(args[0]),
    "nested_scan": lambda args: builtin_nested_scan(args[0]),
    "hashset_scan": lambda args: builtin_hashset_scan(args[0]),
    "bitmap_scan": lambda args: builtin_hashset_scan(args[0]),
    "timsort": lambda args: sorted(args[0]),
    "str": lambda args: str(args[0]),
    "int": lambda args: int(args[0]),
    "float": lambda args: float(args[0]),
    "abs": lambda args: abs(args[0]),
    "range": lambda args: list(range(*[int(a) for a in args])),
}


# ─────────────────────────────────────────────
#  INTERPRETER
# ─────────────────────────────────────────────
class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.functions: Dict[str, FnDef] = {}
        self._call_depth = 0
        self._memo: Dict[str, Any] = {}

    def run(self, program: Program):
        for stmt in program.stmts:
            self.exec_stmt(stmt, self.global_env)

    def exec_stmt(self, node: Node, env: Environment):
        if isinstance(node, LetStmt):
            val = self.eval_expr(node.value, env)
            env.define(node.name, val)

        elif isinstance(node, AssignStmt):
            val = self.eval_expr(node.value, env)
            env.set(node.name, val)

        elif isinstance(node, FnDef):
            self.functions[node.name] = node

        elif isinstance(node, ReturnStmt):
            val = self.eval_expr(node.value, env) if node.value else None
            raise ReturnSignal(val)

        elif isinstance(node, IfStmt):
            cond = self.eval_expr(node.cond, env)
            if self.is_truthy(cond):
                self.exec_block(node.then_body, env)
            elif node.else_body:
                self.exec_block(node.else_body, env)

        elif isinstance(node, WhileStmt):
            while self.is_truthy(self.eval_expr(node.cond, env)):
                try:
                    self.exec_block(node.body, env)
                except ReturnSignal:
                    raise

        elif isinstance(node, ForStmt):
            iterable = self.eval_expr(node.iterable, env)
            if not isinstance(iterable, list):
                raise TypeError(f"Cannot iterate over {type(iterable)}")
            for item in iterable:
                loop_env = Environment(env)
                loop_env.define(node.var, item)
                try:
                    self.exec_block(node.body, loop_env)
                except ReturnSignal:
                    raise

        elif isinstance(node, PrintStmt):
            val = self.eval_expr(node.value, env)
            print(self.flex_str(val))

        elif isinstance(node, ExprStmt):
            self.eval_expr(node.expr, env)

        else:
            pass  # unknown node types silently skipped

    def exec_block(self, stmts: List[Node], parent_env: Environment):
        env = Environment(parent_env)
        for stmt in stmts:
            self.exec_stmt(stmt, env)

    def eval_expr(self, node: Node, env: Environment) -> Any:
        if isinstance(node, Literal):
            return node.value

        if isinstance(node, Identifier):
            return env.get(node.name)

        if isinstance(node, ListLiteral):
            return [self.eval_expr(el, env) for el in node.elements]

        if isinstance(node, IndexAccess):
            obj = self.eval_expr(node.obj, env)
            idx = self.eval_expr(node.index, env)
            return obj[idx]

        if isinstance(node, UnaryOp):
            val = self.eval_expr(node.operand, env)
            if node.op == "-":
                return -val
            if node.op == "not":
                return not self.is_truthy(val)
            return val

        if isinstance(node, BinOp):
            return self.eval_binop(node, env)

        if isinstance(node, Call):
            return self.eval_call(node, env)

        return None

    def eval_binop(self, node: BinOp, env: Environment) -> Any:
        left = self.eval_expr(node.left, env)
        right = self.eval_expr(node.right, env)
        op = node.op

        if op == "+":
            # String concatenation
            if isinstance(left, str) or isinstance(right, str):
                return self.flex_str(left) + self.flex_str(right)
            return left + right
        if op == "-": return left - right
        if op == "*": return left * right
        if op == "/":
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            if isinstance(left, int) and isinstance(right, int):
                return left // right
            return left / right
        if op == "%": return left % right
        if op == "==": return left == right
        if op == "!=": return left != right
        if op == "<":  return left < right
        if op == ">":  return left > right
        if op == "<=": return left <= right
        if op == ">=": return left >= right
        if op == "and": return self.is_truthy(left) and self.is_truthy(right)
        if op == "or":  return self.is_truthy(left) or self.is_truthy(right)
        raise RuntimeError(f"Unknown operator: {op}")

    def eval_call(self, node: Call, env: Environment) -> Any:
        fn_name = node.name
        args = [self.eval_expr(a, env) for a in node.args]

        # Built-ins
        if fn_name in BUILTINS:
            return BUILTINS[fn_name](args)

        # User-defined functions
        if fn_name not in self.functions:
            raise NameError(f"Undefined function: '{fn_name}'")

        fn = self.functions[fn_name]

        # Adaptive function: choose the best variant
        if fn.adaptive:
            return self.eval_adaptive(fn, args, env)

        return self.call_fn(fn, args, env)

    def eval_adaptive(self, fn: FnDef, args: List[Any], env: Environment) -> Any:
        """
        Adaptive dispatch: evaluate each variant's condition and pick the first match.
        Falls back to baseline. Logs the decision.
        """
        chosen_name = "baseline"
        chosen_body = fn.body

        for variant in fn.variants:
            if self.check_variant_condition(variant, args, env):
                # Try to find a built-in or user fn with this variant name
                if variant.name in BUILTINS:
                    REPORT.log(fn.name, variant.name, f"condition met: {variant.condition}")
                    return BUILTINS[variant.name](args)
                elif variant.name in self.functions:
                    REPORT.log(fn.name, variant.name, f"condition met: {variant.condition}")
                    return self.call_fn(self.functions[variant.name], args, env)
                # variant name matches a builtin pattern
                break

        REPORT.log(fn.name, chosen_name, "default baseline selected")
        return self.call_fn_with_body(fn, chosen_body, args, env)

    def check_variant_condition(self, variant: VariantDecl, args: List[Any], env: Environment) -> bool:
        if variant.condition is None:
            return True
        cond = variant.condition.strip()

        # Handle "n > 10" style simple int comparisons (first arg is int)
        m = re.match(r"(\w+)\s*(<|>|<=|>=|==)\s*([\d_]+)$", cond)
        if m and args and isinstance(args[0], (int, float)):
            op, val = m.group(2), int(m.group(3).replace("_", ""))
            n = args[0]
            return eval(f"{n} {op} {val}")

        # Handle "len(xs) < N"
        m = re.match(r"len\s*\(\s*\w+\s*\)\s*(<|>|<=|>=|==)\s*(\d+)", cond)
        if m and args:
            op, val = m.group(1), int(m.group(2))
            n = len(args[0]) if isinstance(args[0], list) else 0
            return eval(f"{n} {op} {val}")

        # Handle "max(xs) < N" or "max_val(xs) < N"
        m = re.match(r"max(?:_val)?\s*\(\s*\w+\s*\)\s*(<|>|<=|>=|==)\s*([\d_]+)", cond)
        if m and args and isinstance(args[0], list) and args[0]:
            op, val = m.group(1), int(m.group(2).replace("_", ""))
            n = max(args[0])
            return eval(f"{n} {op} {val}")

        # Handle "mostly_sorted(xs)"
        if "mostly_sorted" in cond and args and isinstance(args[0], list):
            return builtin_mostly_sorted([args[0]])

        # Handle "heuristic_available(g)"
        if "heuristic_available" in cond:
            return False

        # Handle "undirected(g)"
        if "undirected" in cond:
            return False

        return False

    def call_fn(self, fn: FnDef, args: List[Any], env: Environment) -> Any:
        return self.call_fn_with_body(fn, fn.body, args, env)

    def call_fn_with_body(self, fn: FnDef, body: List[Node], args: List[Any], env: Environment) -> Any:
        self._call_depth += 1
        if self._call_depth > 500:
            raise RecursionError("Maximum recursion depth exceeded")
        fn_env = Environment(self.global_env)
        for (param_name, _), arg_val in zip(fn.params, args):
            fn_env.define(param_name, arg_val)
        try:
            for stmt in body:
                self.exec_stmt(stmt, fn_env)
            return None
        except ReturnSignal as rs:
            return rs.value
        finally:
            self._call_depth -= 1

    def is_truthy(self, val: Any) -> bool:
        if val is None or val is False:
            return False
        if isinstance(val, (int, float)) and val == 0:
            return False
        return True

    def flex_str(self, val: Any) -> str:
        if val is None:
            return "null"
        if isinstance(val, bool):
            return "true" if val else "false"
        if isinstance(val, list):
            return "[" + ", ".join(self.flex_str(v) for v in val) + "]"
        return str(val)


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────
def run_file(path: str):
    try:
        with open(path, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {path}")
        sys.exit(1)

    print(f"── Running {path} ──")
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        interp = Interpreter()
        interp.run(ast)
        REPORT.dump()

    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)
    except NameError as e:
        print(f"Name Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)
    except RecursionError as e:
        print(f"Recursion Error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Flexigen Interpreter v1.0")
        print("Usage: flexigen <file.flex>")
        print("       flexigen --run-all")
        sys.exit(0)

    if sys.argv[1] == "--run-all":
        import glob
        files = sorted(glob.glob("programs/*.flex"))
        for f in files:
            run_file(f)
            print()
    else:
        run_file(sys.argv[1])


if __name__ == "__main__":
    main()
