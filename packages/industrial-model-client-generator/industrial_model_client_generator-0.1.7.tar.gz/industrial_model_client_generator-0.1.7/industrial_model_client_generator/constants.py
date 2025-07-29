python_keywords = [
    "false",
    "none",
    "true",
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
]

mapping_types = {
    "text": "str",
    "boolean": "bool",
    "timestamp": "datetime.datetime",
    "date": "datetime.date",
    "json": "Any",
    "float32": "float",
    "float64": "float",
    "int32": "int",
    "int64": "int",
    "timeseries": "str",
    "file": "str",
    "sequence": "str",
    "direct": "InstanceId",
    "enum": "str",
}

aggregate_group_types = {
    "text",
    "boolean",
    "float32",
    "float64",
    "int32",
    "int64",
    "direct",
}


prefix_operator = {
    "eq": "==",
    "gt": ">",
    "gte": ">=",
    "lt": "<",
    "lte": "<=",
    "contains_all": "containsAll",
    "contains_any": "containsAny",
}

list_operators = {
    "in",
    "contains_all",
    "contains_any",
    "containsAll",
    "containsAny",
}
range_types = {"datetime.datetime", "datetime.date", "float", "int"}
