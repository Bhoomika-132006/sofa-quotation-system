import ast
import operator
from typing import Any

from backend.app.database import get_connection


# ---------------------------------------------------------
# Safe mathematical expression evaluator
# ---------------------------------------------------------

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST, variables: dict[str, float]) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, variables)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("Only numeric constants are allowed.")

    if isinstance(node, ast.Name):
        if node.id not in variables:
            raise ValueError(f"Unknown variable in formula: {node.id}")
        return float(variables[node.id])

    if isinstance(node, ast.BinOp):
        operation = _ALLOWED_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError("Operator is not allowed.")
        left = _safe_eval(node.left, variables)
        right = _safe_eval(node.right, variables)
        return float(operation(left, right))

    if isinstance(node, ast.UnaryOp):
        operation = _ALLOWED_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError("Unary operator is not allowed.")
        value = _safe_eval(node.operand, variables)
        return float(operation(value))

    raise ValueError("Unsupported expression in engineering formula.")


def evaluate_formula(
    formula: str,
    base_quantity: float,
    scale_factors: dict[str, float],
) -> float:
    variables = {
        "base_quantity": float(base_quantity),
        "SL": float(scale_factors["SL"]),
        "SW": float(scale_factors["SW"]),
        "SH": float(scale_factors["SH"]),
        "AREA_RATIO": float(scale_factors["AREA_RATIO"]),
        "SURFACE_AREA_RATIO": float(
            scale_factors["SURFACE_AREA_RATIO"]
        ),
        "VOLUME_RATIO": float(scale_factors["VOLUME_RATIO"]),
    }

    expression = ast.parse(formula, mode="eval")

    result = _safe_eval(expression, variables)

    if result < 0:
        raise ValueError("Scaled quantity cannot be negative.")

    return result


# ---------------------------------------------------------
# Dimension calculations
# ---------------------------------------------------------

def calculate_scale_factors(
    reference_dimensions: dict[str, float],
    target_dimensions: dict[str, float],
) -> dict[str, float]:

    reference_length = float(reference_dimensions["length_mm"])
    reference_depth = float(reference_dimensions["depth_mm"])
    reference_height = float(reference_dimensions["height_mm"])

    target_length = float(target_dimensions["length_mm"])
    target_depth = float(target_dimensions["depth_mm"])
    target_height = float(target_dimensions["height_mm"])

    if reference_length <= 0:
        raise ValueError("Reference length must be greater than zero.")

    if reference_depth <= 0:
        raise ValueError("Reference depth must be greater than zero.")

    if reference_height <= 0:
        raise ValueError("Reference height must be greater than zero.")

    if target_length <= 0:
        raise ValueError("Target length must be greater than zero.")

    if target_depth <= 0:
        raise ValueError("Target depth must be greater than zero.")

    if target_height <= 0:
        raise ValueError("Target height must be greater than zero.")

    sl = target_length / reference_length
    sw = target_depth / reference_depth
    sh = target_height / reference_height

    area_ratio = sl * sw

    volume_ratio = sl * sw * sh

    # Generic surface-area ratio based on the three principal
    # rectangular dimensions.
    reference_surface_area = (
        2
        * (
            reference_length * reference_depth
            + reference_length * reference_height
            + reference_depth * reference_height
        )
    )

    target_surface_area = (
        2
        * (
            target_length * target_depth
            + target_length * target_height
            + target_depth * target_height
        )
    )

    if reference_surface_area <= 0:
        raise ValueError("Reference surface area must be greater than zero.")

    surface_area_ratio = (
        target_surface_area / reference_surface_area
    )

    return {
        "SL": sl,
        "SW": sw,
        "SH": sh,
        "AREA_RATIO": area_ratio,
        "SURFACE_AREA_RATIO": surface_area_ratio,
        "VOLUME_RATIO": volume_ratio,
    }


# ---------------------------------------------------------
# Engineering rules
# ---------------------------------------------------------

def get_engineering_rules() -> list[dict[str, Any]]:
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    rule_id,
                    component_id,
                    rule_name,
                    rule_type,
                    formula,
                    reference_dimension,
                    minimum_value,
                    maximum_value,
                    unit,
                    description,
                    is_active
                FROM engineering_rules
                WHERE is_active = TRUE
                ORDER BY rule_id
                """
            )

            rows = cur.fetchall()

            return [
                {
                    "rule_id": row[0],
                    "component_id": row[1],
                    "rule_name": row[2],
                    "rule_type": row[3],
                    "formula": row[4],
                    "reference_dimension": row[5],
                    "minimum_value": row[6],
                    "maximum_value": row[7],
                    "unit": row[8],
                    "description": row[9],
                    "is_active": row[10],
                }
                for row in rows
            ]

    finally:
        conn.close()


# ---------------------------------------------------------
# BOM scaling
# ---------------------------------------------------------

def scale_bom(bom_items, rules, scale_factors):
    """
    Scale BOM quantities using engineering rules.
    """

    # Normalize component names so:
    # "WoodFrame" == "Wood Frame"
    def normalize_name(name):
        return str(name).replace("_", "").replace("-", "").replace(" ", "").lower()

    rules_by_component = {
        normalize_name(rule["component_id"]): rule
        for rule in rules
    }

    scaled_bom = []

    for item in bom_items:
        component_name = item.get("component_name")

        if not component_name:
            continue

        rule = rules_by_component.get(normalize_name(component_name))

        if not rule:
            # No engineering rule → keep original quantity
            scaled_quantity = float(item["quantity"])
            scaling_applied = False
        else:
            scaled_quantity = evaluate_formula(
                rule["formula"],
                item["quantity"],
                scale_factors
            )
            scaling_applied = True

        scaled_item = {
            **item,
            "base_quantity": float(item["quantity"]),
            "scaled_quantity": float(scaled_quantity),
            "scaling_applied": scaling_applied,
        }

        scaled_bom.append(scaled_item)

    return scaled_bom
# ---------------------------------------------------------
# Complete sofa BOM scaling
# ---------------------------------------------------------

def scale_sofa_bom(
    reference_dimensions: dict[str, float],
    target_dimensions: dict[str, float],
    bom_items: list[dict[str, Any]],
    rules: list[dict[str, Any]],
) -> dict[str, Any]:

    scale_factors = calculate_scale_factors(
        reference_dimensions,
        target_dimensions,
    )

    scaled_bom = scale_bom(
        bom_items,
        rules,
        scale_factors,
    )

    return {
        "reference_dimensions": reference_dimensions,
        "target_dimensions": target_dimensions,
        "scale_factors": scale_factors,
        "scaled_bom": scaled_bom,
    }