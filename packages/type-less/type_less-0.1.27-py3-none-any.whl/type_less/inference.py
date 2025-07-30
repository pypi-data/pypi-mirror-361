from __future__ import annotations
import ast
from collections.abc import Awaitable as ABCAwaitable
from functools import cache
import inspect
import sys
from typing import (
    Any,
    Callable,
    Dict,
    Literal,
    Optional,
    Tuple,
    TypedDict,
    Type,
    Union,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
    Awaitable,
    Annotated,
)
import textwrap


def _unwrap_annotated(t: Type) -> Type:
    """Unwrap Annotated types to get the underlying type."""
    # get_origin is from typing
    if get_origin(t) is Annotated:
        # The first argument to Annotated is the actual type
        return get_args(t)[0]
    return t


@cache
def _get_cached_type_hints(cls: Type[Any]) -> dict[str, Type[Any]]:
    return get_type_hints(cls)


def _snake_case_to_capital_case(name: str) -> str:
    return "".join(word.capitalize() for word in name.split("_"))


def _sanitize_name(name: str) -> str:
    return "".join(c if c.isalnum() else "" for c in name)


def _get_full_attribute_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base_name = _get_full_attribute_name(node.value)
        if base_name:
            return f"{base_name}.{node.attr}"
    return None


def _get_module_type(func: Callable, name: str) -> Type:
    # Split the name by dots to handle nested attributes
    parts = name.split(".")
    if not parts:
        return Any

    # Get the base module
    module = sys.modules.get(func.__module__, None)
    if not module:
        return Any

    # Start with the base module
    current = module
    for i, part in enumerate(parts):
        if not hasattr(current, part):
            # If we're at the top-level (first part), check module __dict__ for imported variables
            if i == 0 and part in getattr(current, "__dict__", {}):
                current = current.__dict__[part]
            else:
                # Missing attribute
                return Any
        else:
            current = getattr(current, part)

    # Check the final result
    if isinstance(current, type) or getattr(current, "__module__", None) == "typing":
        return current
    elif isinstance(current, Callable):
        return guess_return_type(current)
    else:
        # For imported variables, return their type
        return type(current)

    return Any


def _get_module_type_in_context(name: str, context_func: Callable) -> Type:
    """
    Resolve a type name in the context of a specific function/method.
    This is used when we need to resolve string type annotations in the
    context where they were defined, not where they are being used.
    """
    # Split the name by dots to handle nested attributes
    parts = name.split(".")
    if not parts:
        return Any

    # Get the module where the context function is defined
    module = sys.modules.get(context_func.__module__, None)
    if not module:
        return Any

    # Start with the base module
    current = module
    for part in parts:
        if not hasattr(current, part):
            return Any
        current = getattr(current, part)

    # Check the final result
    if isinstance(current, type) or getattr(current, "__module__", None) == "typing":
        return current
    elif isinstance(current, Callable):
        return guess_return_type(current)

    return Any


def _default_typed_dict_name_generator(
    func: Callable, nested_path: list[str], branch_path: list[tuple[ast.AST, bool]]
) -> str:
    """Default name generator for TypedDicts."""
    class_name = f"{_snake_case_to_capital_case(func.__name__)}"

    for condition, is_if_branch in branch_path:
        cond_name_str = _get_full_attribute_name(condition)

        if cond_name_str:
            sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in cond_name_str)
            branch_name = _snake_case_to_capital_case(sanitized)
            if is_if_branch:
                class_name += f"If{branch_name}"
            else:
                class_name += f"IfNot{branch_name}"

    for component in nested_path:
        class_name += _snake_case_to_capital_case(_sanitize_name(component))

    return class_name


def guess_return_type(
    func: Callable,
    use_literals=True,
    typed_dict_name_generator: Optional[Callable[[Callable, list, list], str]] = None,
) -> Type:
    """
    Infer the return type of a Python function by analyzing its AST.
    For dictionary returns, creates a TypedDict representation.

    Args:
        func: The function to analyze

    Returns:
        The inferred return type
    """
    name_generator = typed_dict_name_generator or _default_typed_dict_name_generator
    # Get function source code and create AST
    try:
        source = inspect.getsource(func)
        source = textwrap.dedent(source)
    except Exception:
        return Any

    module = ast.parse(source)

    # Extract the function definition node
    func_def = module.body[0]
    if not isinstance(func_def, (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise ValueError("Input is not a function definition")

    # Create a symbol table for type analysis
    symbol_table = {}

    # Populate the symbol table with type hints from function annotations
    if func_def.returns:
        # If function has a return type annotation, use it directly
        return _resolve_annotation(func_def.returns, {}, func)

    # Gather type information from annotations and assignments
    _analyze_function_body(func_def, symbol_table, func, use_literals, name_generator)

    # Find all return statements
    return_types = []
    for node in ast.walk(func_def):
        if isinstance(node, ast.Return) and node.value:
            return_type = _infer_expr_type(node.value, symbol_table, func, [], use_literals, [], name_generator)
            return_types.append(return_type)
    # If we found return statements
    if return_types:
        if len(return_types) == 1:
            return return_types[0]
        else:
            # Multiple return types - use Union
            return Union[tuple(set(return_types))]

    # Default to Any if no return statements or couldn't infer
    return Any


def _analyze_function_body(
    func_def: ast.FunctionDef,
    symbol_table: dict[str, Type],
    func: Callable,
    use_literals: bool,
    typed_dict_name_generator: Callable,
) -> None:
    """Analyze function body to populate symbol table with type information"""
    # First gather parameter types and TypeVar bindings
    type_context = {}
    for arg in func_def.args.args:
        if arg.annotation:
            param_type = _resolve_annotation(arg.annotation, type_context, func)
            symbol_table[arg.arg] = param_type

            # If the parameter type is a TypeVar, track its binding
            if isinstance(param_type, TypeVar):
                type_context[param_type.__name__] = param_type

    # Analyze assignments to track variable types
    for node in ast.walk(func_def):
        if isinstance(node, ast.Assign):
            assigned_type = _infer_expr_type(
                node.value, symbol_table, func, [], use_literals, [], typed_dict_name_generator
            )
            for target in node.targets:
                if isinstance(target, ast.Name):
                    symbol_table[target.id] = assigned_type
                elif isinstance(target, ast.Tuple):
                    # Handle tuple unpacking
                    if hasattr(assigned_type, "__origin__") and assigned_type.__origin__ is tuple:
                        # Get the element types from the tuple type
                        element_types = assigned_type.__args__
                        if isinstance(element_types, tuple):
                            # Match each target with its corresponding type
                            for i, elt in enumerate(target.elts):
                                if isinstance(elt, ast.Name):
                                    if i < len(element_types):
                                        symbol_table[elt.id] = element_types[i]
                                    else:
                                        symbol_table[elt.id] = Any
                        else:
                            # If we can't determine individual element types, use Any
                            for elt in target.elts:
                                if isinstance(elt, ast.Name):
                                    symbol_table[elt.id] = Any
                    else:
                        # If not a tuple type, use Any for all targets
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                symbol_table[elt.id] = Any
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            # Handle annotated assignments
            symbol_table[node.target.id] = _resolve_annotation(node.annotation, type_context, func)


def _resolve_annotation(annotation: ast.AST, type_context: dict[str, Any], func: Callable) -> Type:
    """Resolve a type annotation AST node to a real type"""
    if isinstance(annotation, ast.Name):
        # Simple types like int, str, etc.
        type_name = annotation.id
        # Check Python's built-in types first
        if type_name in __builtins__:
            return _unwrap_annotated(__builtins__[type_name])

        # Check if it's a TypeVar
        if type_name in type_context:
            return _unwrap_annotated(type_context[type_name])

        # Otherwise check if it's imported
        return _unwrap_annotated(_get_module_type(func, type_name))

    elif isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        # Handle string literal type names
        type_name = annotation.value
        # Check Python's built-in types first
        if type_name in __builtins__:
            return _unwrap_annotated(__builtins__[type_name])

        # Check if it's a TypeVar
        if type_name in type_context:
            return _unwrap_annotated(type_context[type_name])

        # Otherwise check if it's imported
        return _unwrap_annotated(_get_module_type(func, type_name))

    elif isinstance(annotation, ast.Subscript):
        # Handle generic types like list[int], dict[str, int], etc.
        if isinstance(annotation.value, ast.Name):
            base_type = annotation.value.id
            if base_type == "List" or base_type == "list":
                elem_type = _resolve_annotation(annotation.slice, type_context, func)
                return list[elem_type]
            elif base_type == "Dict" or base_type == "dict":
                if isinstance(annotation.slice, ast.Tuple):
                    key_type = _resolve_annotation(annotation.slice.elts[0], type_context, func)
                    val_type = _resolve_annotation(annotation.slice.elts[1], type_context, func)
                    return dict[key_type, val_type]
                return Dict
            elif base_type == "Set" or base_type == "set":
                elem_type = _resolve_annotation(annotation.slice, type_context, func)
                return set[elem_type]
            elif base_type == "Union":
                if isinstance(annotation.slice, ast.Tuple):
                    elem_types = [_resolve_annotation(e, type_context, func) for e in annotation.slice.elts]
                    return Union[tuple(elem_types)]
                return Union
            elif base_type == "Literal":
                if isinstance(annotation.slice, ast.Tuple):
                    values = []
                    for elt in annotation.slice.elts:
                        if isinstance(elt, ast.Constant):
                            values.append(elt.value)
                    return Literal[tuple(values)]  # type: ignore
                elif isinstance(annotation.slice, ast.Constant):
                    return Literal[annotation.slice.value]  # type: ignore
            elif base_type == "Optional":
                elem_type = _resolve_annotation(annotation.slice, type_context, func)
                return Optional[elem_type]
            elif base_type == "Type":
                elem_type = _resolve_annotation(annotation.slice, type_context, func)
                return Type[elem_type]
            elif base_type == "TypeVar":
                # Handle TypeVar definitions
                if isinstance(annotation.slice, ast.Constant):
                    return TypeVar(annotation.slice.value)
                return TypeVar

    elif isinstance(annotation, ast.Attribute):
        full_name = _get_full_attribute_name(annotation)
        if full_name:
            return _unwrap_annotated(_get_module_type(func, full_name))
        return Any

    # Fallback for unresolved or complex annotations
    return Any


def _get_function_definition(func_name: str, func: Callable) -> Optional[Callable]:
    """Get the definition of a function by name from the module"""
    module = sys.modules.get(func.__module__, None)
    if not module:
        return None
    return getattr(module, func_name, None)


def _resolve_str_type(type_candidate, func):
    # Helper to resolve string type names to actual types
    if isinstance(type_candidate, str):
        return _get_module_type(func, type_candidate)
    return type_candidate


def _infer_expr_type(
    node: ast.AST,
    symbol_table: dict[str, Type],
    func: Callable,
    nested_path: list[str],
    use_literals: bool,
    branch_path: list[tuple[ast.AST, bool]],
    typed_dict_name_generator: Callable,
) -> Type:
    """Infer the type of an expression"""
    if isinstance(node, ast.Dict):
        return _create_typed_dict_from_dict(
            node,
            symbol_table,
            func,
            nested_path,
            use_literals,
            branch_path,
            typed_dict_name_generator,
        )

    elif isinstance(node, ast.List):
        if not node.elts:
            return list[Any]
        element_types = [
            _infer_expr_type(
                elt,
                symbol_table,
                func,
                nested_path,
                use_literals,
                branch_path,
                typed_dict_name_generator,
            )
            for elt in node.elts
        ]
        element_types = [_resolve_str_type(t, func) for t in element_types]
        if len(set(element_types)) == 1:
            return list[element_types[0]]
        return list[Union[tuple(set(element_types))]]

    elif isinstance(node, ast.Tuple):
        if not node.elts:
            return tuple[()]
        element_types = [
            _infer_expr_type(
                elt,
                symbol_table,
                func,
                nested_path,
                use_literals,
                branch_path,
                typed_dict_name_generator,
            )
            for elt in node.elts
        ]
        element_types = [_resolve_str_type(t, func) for t in element_types]
        return tuple[tuple(element_types)]

    elif isinstance(node, ast.Set):
        if not node.elts:
            return set[Any]
        element_types = [
            _infer_expr_type(
                elt,
                symbol_table,
                func,
                nested_path,
                use_literals,
                branch_path,
                typed_dict_name_generator,
            )
            for elt in node.elts
        ]
        element_types = [_resolve_str_type(t, func) for t in element_types]
        if len(set(element_types)) == 1:
            return set[element_types[0]]
        return set[Union[tuple(set(element_types))]]

    elif isinstance(node, ast.Constant):
        # Handle literals
        if use_literals:
            return Literal[node.value]  # type: ignore
        else:
            return type(node.value)

    elif isinstance(node, ast.Name):
        # Look up variable types in the symbol table
        if node.id in symbol_table:
            return symbol_table[node.id]

        # Handle built-in types referenced by name
        if node.id in __builtins__ and isinstance(__builtins__[node.id], type):
            return __builtins__[node.id]

        return _get_module_type(func, node.id)

    elif isinstance(node, ast.Call):
        # Handle function calls
        if isinstance(node.func, ast.Attribute):
            # Handle class method calls
            if isinstance(node.func.value, ast.Name):
                class_name = node.func.value.id
                method_name = node.func.attr

                # Get the class type
                class_type = _get_module_type(func, class_name)
                if isinstance(class_type, type):
                    # Get the method
                    method = getattr(class_type, method_name, None)
                    if method and hasattr(method, "__annotations__"):
                        return_type = _get_cached_type_hints(method).get("return")
                        if isinstance(return_type, TypeVar):
                            # For class methods, the TypeVar is bound to the class
                            return class_type
                        # If return type is a string, resolve it in the method's module context
                        if isinstance(return_type, str):
                            return _get_module_type_in_context(return_type, method)
                        # Handle complex types with quoted strings
                        return _resolve_complex_type_in_context(return_type, method)

                        # Handle chained method calls (e.g., obj.method1().method2())
            elif isinstance(node.func.value, ast.Call):
                # First, infer the return type of the base call
                base_type = _infer_expr_type(
                    node.func.value,
                    symbol_table,
                    func,
                    nested_path,
                    use_literals,
                    branch_path,
                    typed_dict_name_generator,
                )

                # If the base_type has Self, resolve it to the actual class
                if hasattr(base_type, "__args__") and base_type.__args__:
                    for i, arg in enumerate(base_type.__args__):
                        if hasattr(arg, "__name__") and arg.__name__ == "Self":
                            # Get the class from the base call
                            if isinstance(node.func.value.func, ast.Attribute) and isinstance(
                                node.func.value.func.value, ast.Name
                            ):
                                class_name = node.func.value.func.value.id
                                class_type = _get_module_type(func, class_name)
                                if isinstance(class_type, type):
                                    # Replace Self with the actual class
                                    if hasattr(base_type, "__origin__"):
                                        new_args = list(base_type.__args__)
                                        new_args[i] = class_type
                                        base_type = base_type.__origin__[tuple(new_args)]

                # Then get the method from that type
                method_name = node.func.attr

                # Handle generic types by getting the origin type
                if hasattr(base_type, "__origin__"):
                    # For generic types like QuerySet[Cat], get the origin type (QuerySet)
                    origin_type = base_type.__origin__
                    method = getattr(origin_type, method_name, None)
                    if method and hasattr(method, "__annotations__"):
                        return_type = _get_cached_type_hints(method).get("return")
                        if return_type:
                            # If return type has args (generic), substitute them
                            if hasattr(return_type, "__args__") and hasattr(base_type, "__args__"):
                                # For QuerySet[Cat].first() -> QuerySetSingle[Cat | None]
                                # We need to preserve the original type parameter
                                if base_type.__args__:
                                    original_type_param = base_type.__args__[0]
                                    # Handle Self type - resolve it to the actual class
                                    if (
                                        hasattr(original_type_param, "__name__")
                                        and original_type_param.__name__ == "Self"
                                    ):
                                        # Get the class from the base call
                                        if isinstance(node.func.value.func, ast.Attribute) and isinstance(
                                            node.func.value.func.value, ast.Name
                                        ):
                                            class_name = node.func.value.func.value.id
                                            class_type = _get_module_type(func, class_name)
                                            if isinstance(class_type, type):
                                                original_type_param = class_type

                                    # Create a new generic type with the preserved type parameter
                                    if hasattr(return_type, "__origin__"):
                                        return_origin = return_type.__origin__
                                        return_args = return_type.__args__
                                        # Replace TYPEVAR with the original type parameter
                                        new_args = []
                                        for arg in return_args:
                                            if isinstance(arg, TypeVar):
                                                new_args.append(original_type_param)
                                            elif hasattr(arg, "__origin__") and arg.__origin__ is Union:
                                                # Handle Union types like Optional[TYPEVAR]
                                                union_args = []
                                                for union_arg in arg.__args__:
                                                    if isinstance(union_arg, TypeVar):
                                                        union_args.append(original_type_param)
                                                    else:
                                                        union_args.append(union_arg)
                                                if len(union_args) == 1:
                                                    new_args.append(union_args[0])
                                                else:
                                                    new_args.append(Union[tuple(union_args)])
                                            else:
                                                new_args.append(arg)
                                        if new_args:
                                            return return_origin[tuple(new_args)]

                            return return_type

                elif isinstance(base_type, type):
                    method = getattr(base_type, method_name, None)
                    if method and hasattr(method, "__annotations__"):
                        return_type = _get_cached_type_hints(method).get("return")
                        if isinstance(return_type, TypeVar):
                            # For class methods, the TypeVar is bound to the class
                            return base_type
                        # If return type is a string, resolve it in the method's module context
                        if isinstance(return_type, str):
                            return _get_module_type_in_context(return_type, method)
                        # Handle complex types with quoted strings
                        if return_type is not None:
                            return _resolve_complex_type_in_context(return_type, method)
                        # If no return type annotation found, infer from method code
                        else:
                            return guess_return_type(method)
                    # If method has no annotations, infer from method code
                    elif method:
                        return guess_return_type(method)

                # If we can't find the method or type info, return Any
                return Any

            # Handle regular method calls
            # Build the full attribute path by traversing the AST
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            # Reverse the parts to get the correct order
            parts.reverse()
            return _get_module_type(func, ".".join(parts))

        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            # First check if we have the function in our symbol table
            if func_name in symbol_table:
                func_type = symbol_table[func_name]
                if hasattr(func_type, "__annotations__") and "return" in func_type.__annotations__:
                    return_type = _get_cached_type_hints(func_type)["return"]
                    # If return type is a TypeVar, try to resolve it from arguments
                    if isinstance(return_type, TypeVar):
                        # Look at the first argument to determine the type
                        if node.args and isinstance(node.args[0], ast.Name):
                            arg_name = node.args[0].id
                            if arg_name in symbol_table:
                                return symbol_table[arg_name]
                        return return_type

            # If not in symbol table, try to get the function definition
            func_def = _get_function_definition(func_name, func)
            if func_def and hasattr(func_def, "__annotations__"):
                if "return" in func_def.__annotations__:
                    return_type = _get_cached_type_hints(func_def)["return"]
                    if isinstance(return_type, TypeVar):
                        # Look at the first argument to determine the type
                        if node.args and isinstance(node.args[0], ast.Constant):
                            return type(node.args[0].value)
                        elif node.args and isinstance(node.args[0], ast.Name):
                            arg_name = node.args[0].id
                            if arg_name in symbol_table:
                                return symbol_table[arg_name]
                        return return_type
                    # Handle tuple return types
                    if hasattr(return_type, "__origin__") and return_type.__origin__ is tuple:
                        return return_type

        # Handle module function calls
        if isinstance(node.func, ast.Attribute):
            return _get_module_type(func, f"{node.func.value.id}.{node.func.attr}")

        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            # Handle some common built-in functions
            if func_name == "int":
                return int
            elif func_name == "str":
                return str
            elif func_name == "float":
                return float
            elif func_name == "list":
                return list[Any]
            elif func_name == "dict":
                return dict[Any, Any]
            elif func_name == "set":
                return set[Any]
            elif func_name == "tuple":
                return Tuple

            return _get_module_type(func, func_name)

        # For other function calls, we default to Any
        return Any

    elif isinstance(node, ast.BinOp):
        # Handle binary operations
        left_type = _infer_expr_type(
            node.left,
            symbol_table,
            func,
            nested_path,
            use_literals,
            branch_path,
            typed_dict_name_generator,
        )
        right_type = _infer_expr_type(
            node.right,
            symbol_table,
            func,
            nested_path,
            use_literals,
            branch_path,
            typed_dict_name_generator,
        )

        # String concatenation
        if isinstance(node.op, ast.Add) and (left_type == str or right_type == str):
            return str

        # Numeric operations typically return numeric types
        if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            if left_type == float or right_type == float:
                return float
            return int

        return Any

    elif isinstance(node, ast.Compare):
        return bool

    elif isinstance(node, ast.IfExp):
        body_type = _infer_expr_type(
            node.body,
            symbol_table,
            func,
            nested_path,
            use_literals,
            branch_path + [(node.test, True)],
            typed_dict_name_generator,
        )
        orelse_type = _infer_expr_type(
            node.orelse,
            symbol_table,
            func,
            nested_path,
            use_literals,
            branch_path + [(node.test, False)],
            typed_dict_name_generator,
        )
        return body_type | orelse_type

    elif isinstance(node, ast.Attribute):
        # Handle attribute access (e.g., obj.attr)
        if isinstance(node.value, ast.Name):
            # Special case for self.attribute access
            if node.value.id == "self":
                # Check if we're in a method context (function has self parameter)
                if hasattr(func, "__self__"):
                    # This is a bound method, get the class
                    class_type = func.__self__.__class__
                elif hasattr(func, "__qualname__") and "." in func.__qualname__:
                    # This is an unbound method, get the class from the qualname
                    class_name = func.__qualname__.split(".")[0]
                    class_type = _get_module_type(func, class_name)
                else:
                    class_type = Any

                # Look up the attribute in the class annotations
                if isinstance(class_type, type) and hasattr(class_type, "__annotations__"):
                    if node.attr in class_type.__annotations__:
                        return _get_cached_type_hints(class_type)[node.attr]

                return Any

            # First check if the object is in the symbol table
            if node.value.id in symbol_table:
                # Get the type of the object
                obj_type = symbol_table[node.value.id]

                # If the object has type annotations, try to get the attribute type
                if hasattr(obj_type, "__annotations__") and node.attr in obj_type.__annotations__:
                    return _get_cached_type_hints(obj_type)[node.attr]

                # If the object is a class with class variables
                if isinstance(obj_type, type):
                    if hasattr(obj_type, node.attr):
                        attr_value = getattr(obj_type, node.attr)
                        # If it's a Literal type or other type annotation
                        if hasattr(attr_value, "__origin__") and attr_value.__origin__ is Literal:
                            return attr_value
                        # For regular attributes, infer their type
                        return type(attr_value)
                # If the object is an instance of a class
                elif hasattr(obj_type, "__class__"):
                    class_type = obj_type.__class__
                    if hasattr(class_type, "__annotations__") and node.attr in class_type.__annotations__:
                        return _get_cached_type_hints(class_type)[node.attr]
            else:
                # If not in symbol table, try to resolve from module
                obj_type = _get_module_type(func, node.value.id)
                if obj_type != Any:
                    # If the object has type annotations, try to get the attribute type
                    if hasattr(obj_type, "__annotations__") and node.attr in obj_type.__annotations__:
                        return _get_cached_type_hints(obj_type)[node.attr]

                    # If the object is a class with class variables
                    if isinstance(obj_type, type):
                        if hasattr(obj_type, node.attr):
                            attr_value = getattr(obj_type, node.attr)
                            # If it's a Literal type or other type annotation
                            if hasattr(attr_value, "__origin__") and attr_value.__origin__ is Literal:
                                return attr_value
                            # For regular attributes, infer their type
                            return type(attr_value)
                    # If the object is an instance of a class
                    elif hasattr(obj_type, "__class__"):
                        class_type = obj_type.__class__
                        if hasattr(class_type, "__annotations__") and node.attr in class_type.__annotations__:
                            return _get_cached_type_hints(class_type)[node.attr]

        # For other attribute access, default to Any
        return Any

    elif isinstance(node, ast.Subscript):
        value_type = _infer_expr_type(
            node.value,
            symbol_table,
            func,
            nested_path,
            use_literals,
            branch_path,
            typed_dict_name_generator,
        )
        value_type = _resolve_str_type(value_type, func)
        # If the value is a list, get its element type
        if hasattr(value_type, "__origin__") and value_type.__origin__ is list:
            return _resolve_str_type(value_type.__args__[0], func)
        # If the value is a dict, get its value type
        if hasattr(value_type, "__origin__") and value_type.__origin__ is dict:
            return _resolve_str_type(value_type.__args__[1], func)
        return Any

    elif isinstance(node, ast.Await):
        # Handle await expressions by inferring the type of the awaited value
        awaited_type = _infer_expr_type(
            node.value,
            symbol_table,
            func,
            nested_path,
            use_literals,
            branch_path,
            typed_dict_name_generator,
        )
        origin = get_origin(awaited_type)

        # Check if it's a standard Awaitable type
        if origin in (Awaitable, ABCAwaitable):
            return awaited_type.__args__[0]

        # Check if the origin is a subclass of Awaitable (like QuerySetSingle)
        if origin is not None and isinstance(origin, type):
            try:
                if issubclass(origin, (Awaitable, ABCAwaitable)):

                    # Check if it has a __await__ method that returns a Generator
                    if hasattr(origin, "__await__"):
                        try:
                            await_method = getattr(origin, "__await__")
                            await_hints = _get_cached_type_hints(await_method)
                            if "return" in await_hints:
                                await_return_type = await_hints["return"]
                                # Check if it's a Generator[Any, None, T] - we want T
                                await_origin = get_origin(await_return_type)
                                if await_origin is not None:
                                    from collections.abc import Generator

                                    if await_origin in (Generator, ABCAwaitable) or (
                                        hasattr(await_origin, "__name__") and await_origin.__name__ == "Generator"
                                    ):
                                        await_args = get_args(await_return_type)
                                        if len(await_args) >= 3:
                                            # For Generator[Send, Yield, Return], we want Return (the 3rd arg)
                                            final_type = await_args[2]

                                            # We need to substitute TypeVars in final_type with the actual type arguments
                                            # from the original awaited_type
                                            if awaited_type.__args__:
                                                # Get the type arguments from the original type (e.g., Self from QuerySet[Self])
                                                original_args = awaited_type.__args__

                                                # Handle the case where final_type contains TypeVars that need substitution
                                                # TODO: refactor this AI goo
                                                final_origin = get_origin(final_type)
                                                if final_origin is not None:
                                                    final_args = get_args(final_type)
                                                    if final_args:
                                                        resolved_args = []
                                                        for arg in final_args:
                                                            # If this is a TypeVar, substitute it with the corresponding type from original_args
                                                            if isinstance(arg, TypeVar):
                                                                # For now, assume 1:1 mapping (first TypeVar gets first original arg)
                                                                if original_args:
                                                                    substituted_arg = original_args[0]
                                                                    # If the substituted arg is Self, resolve it to the actual class
                                                                    if (
                                                                        hasattr(
                                                                            substituted_arg,
                                                                            "__name__",
                                                                        )
                                                                        and substituted_arg.__name__ == "Self"
                                                                    ):
                                                                        if isinstance(
                                                                            node.value, ast.Call
                                                                        ) and isinstance(
                                                                            node.value.func,
                                                                            ast.Attribute,
                                                                        ):
                                                                            if isinstance(
                                                                                node.value.func.value,
                                                                                ast.Name,
                                                                            ):
                                                                                class_name = node.value.func.value.id
                                                                                class_type = _get_module_type(
                                                                                    func, class_name
                                                                                )
                                                                                if isinstance(class_type, type):
                                                                                    resolved_args.append(class_type)
                                                                                else:
                                                                                    resolved_args.append(
                                                                                        substituted_arg
                                                                                    )
                                                                            else:
                                                                                resolved_args.append(substituted_arg)
                                                                        else:
                                                                            resolved_args.append(substituted_arg)
                                                                    else:
                                                                        resolved_args.append(substituted_arg)
                                                                else:
                                                                    resolved_args.append(arg)
                                                            else:
                                                                resolved_args.append(arg)

                                                        # Reconstruct the type with resolved args
                                                        if final_origin is list:
                                                            return (
                                                                list[resolved_args[0]]
                                                                if len(resolved_args) == 1
                                                                else list[Union[tuple(resolved_args)]]
                                                            )
                                                        elif final_origin is tuple:
                                                            return tuple[tuple(resolved_args)]
                                                        elif final_origin is dict:
                                                            return (
                                                                dict[
                                                                    resolved_args[0],
                                                                    resolved_args[1],
                                                                ]
                                                                if len(resolved_args) == 2
                                                                else dict[Any, Any]
                                                            )
                                                        elif final_origin is set:
                                                            return (
                                                                set[resolved_args[0]]
                                                                if len(resolved_args) == 1
                                                                else set[Union[tuple(resolved_args)]]
                                                            )
                                                        else:
                                                            try:
                                                                return final_origin[tuple(resolved_args)]
                                                            except (TypeError, AttributeError):
                                                                return final_type

                                                # If final_type is directly a TypeVar, substitute it
                                                elif isinstance(final_type, TypeVar) and original_args:
                                                    substituted_type = original_args[0]
                                                    if (
                                                        hasattr(substituted_type, "__name__")
                                                        and substituted_type.__name__ == "Self"
                                                    ):
                                                        if isinstance(node.value, ast.Call) and isinstance(
                                                            node.value.func, ast.Attribute
                                                        ):
                                                            if isinstance(node.value.func.value, ast.Name):
                                                                class_name = node.value.func.value.id
                                                                class_type = _get_module_type(func, class_name)
                                                                if isinstance(class_type, type):
                                                                    return class_type
                                                    return substituted_type

                                            return final_type
                        except Exception:
                            pass

                    # Fallback to the original logic
                    if awaited_type.__args__:
                        result_type = awaited_type.__args__[0]
                        # Handle Self type - resolve it to the actual class
                        if hasattr(result_type, "__name__") and result_type.__name__ == "Self":
                            # Look for the class context in the call chain
                            # Check if we're in a method call context
                            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
                                if isinstance(node.value.func.value, ast.Name):
                                    class_name = node.value.func.value.id
                                    class_type = _get_module_type(func, class_name)
                                    if isinstance(class_type, type):
                                        return class_type
                        return result_type
                    return Any
            except TypeError:
                # issubclass can raise TypeError for some types
                pass

        # If not awaitable, return the type as-is
        return awaited_type

    # Default for complex or unknown expressions
    return Any


def _create_typed_dict_from_dict(
    dict_node: ast.Dict,
    symbol_table: dict[str, Type],
    func: Callable,
    nested_path: list[str],
    use_literals: bool,
    branch_path: list[tuple[ast.AST, bool]],
    typed_dict_name_generator: Callable,
) -> Type:
    """Create a TypedDict from a dictionary literal"""
    # Check if all keys are string literals
    field_types = {}
    is_valid_typeddict = True

    for i, key in enumerate(dict_node.keys):
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            value_type = _infer_expr_type(
                dict_node.values[i],
                symbol_table,
                func,
                nested_path + [key.value],
                use_literals,
                branch_path,
                typed_dict_name_generator,
            )
            field_types[key.value] = value_type
        else:
            is_valid_typeddict = False
            break

    if is_valid_typeddict and field_types:
        # Create a dynamic TypedDict class
        class_name = typed_dict_name_generator(func, nested_path, branch_path)
        return TypedDict(class_name, field_types)

    # If not a valid TypedDict, return a regular Dict with inferred types
    if dict_node.keys:
        key_types = [
            _infer_expr_type(
                key,
                symbol_table,
                func,
                nested_path + [key],
                use_literals,
                branch_path,
                typed_dict_name_generator,
            )
            for key in dict_node.keys
        ]
        value_types = [
            _infer_expr_type(
                value,
                symbol_table,
                func,
                nested_path,
                use_literals,
                branch_path,
                typed_dict_name_generator,
            )
            for value in dict_node.values
        ]

        # Determine common types
        if len(set(key_types)) == 1 and len(set(value_types)) == 1:
            return dict[key_types[0], value_types[0]]
        elif len(set(key_types)) == 1:
            return dict[key_types[0], Union[tuple(set(value_types))]]
        elif len(set(value_types)) == 1:
            return dict[Union[tuple(set(key_types))], value_types[0]]
        else:
            return dict[Union[tuple(set(key_types))], Union[tuple(set(value_types))]]

    return dict[Any, Any]


def _resolve_complex_type_in_context(type_annotation: Type, context_func: Callable) -> Type:
    """
    Recursively resolve quoted types in complex type annotations.
    This handles cases like tuple["Cat", "Dog"] where the strings
    need to be resolved to actual types in the context where they were defined.
    """
    # Handle simple string types
    if isinstance(type_annotation, str):
        return _get_module_type_in_context(type_annotation, context_func)

    # Handle generic types (like tuple, list, etc.)
    origin = get_origin(type_annotation)
    if origin is not None:
        args = get_args(type_annotation)
        if args:
            # Recursively resolve each argument
            resolved_args = []
            for arg in args:
                if isinstance(arg, str):
                    resolved_args.append(_get_module_type_in_context(arg, context_func))
                else:
                    resolved_args.append(_resolve_complex_type_in_context(arg, context_func))

            # Reconstruct the type with resolved arguments
            if origin is tuple:
                return tuple[tuple(resolved_args)]
            elif origin is list:
                return list[resolved_args[0]] if len(resolved_args) == 1 else list[Union[tuple(resolved_args)]]
            elif origin is dict:
                return dict[resolved_args[0], resolved_args[1]] if len(resolved_args) == 2 else dict[Any, Any]
            elif origin is set:
                return set[resolved_args[0]] if len(resolved_args) == 1 else set[Union[tuple(resolved_args)]]
            elif origin is Union:
                return Union[tuple(resolved_args)]
            else:
                # For other generic types, try to reconstruct
                try:
                    return origin[tuple(resolved_args)]
                except (TypeError, AttributeError):
                    return type_annotation

    # For non-generic types, return as-is
    return type_annotation
