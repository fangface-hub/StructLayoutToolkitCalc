# StructLayoutToolkitCalc
A safe, deterministic expression evaluator for computing bit‑accurate offsets, sizes, and field values within StructLayoutToolkit.

## Overview
sltcalc provides a safe and deterministic expression evaluator used across StructLayoutToolkit to compute bit‑accurate offsets, sizes, and derived field values.
It parses expressions into Python’s AST and evaluates a restricted subset of operations, ensuring predictable behavior without accessing Python globals or executing arbitrary code.
The evaluator supports arithmetic, bitwise operations, conditional expressions, and user‑defined variables supplied through an isolated environment.
This module enables dynamic field definitions, computed offsets, variable‑length structures, and protocol‑specific formulas while maintaining strict safety and structural consistency.
