OPERATORS = ("equals", "not_equals", "contains", "in", "greater_than")


def matches(operator: str, attribute_value: object, rule_value: str) -> bool:
    """Whether one rule matches one attribute of the evaluation context."""
    if attribute_value is None:
        return False

    actual = str(attribute_value)

    if operator == "equals":
        return actual == rule_value
    if operator == "not_equals":
        return actual != rule_value
    if operator == "contains":
        return rule_value in actual
    if operator == "in":
        return actual in [item.strip() for item in rule_value.split(",")]
    if operator == "greater_than":
        try:
            return float(actual) > float(rule_value)
        except ValueError:
            return False
    return False


def all_rules_match(rules, context: dict) -> bool:
    """Every rule must match. No rules means nothing stands in the way."""
    return all(
        matches(rule.operator, context.get(rule.attribute), rule.value)
        for rule in rules
    )
