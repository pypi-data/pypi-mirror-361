# mypy: disable-error-code="no-untyped-def,no-untyped-call"

import importlib
from typing import Any, Dict, Optional, Sequence


def custom_imports(libraries: list[str]) -> Any:
    def restricted_imports(
        name: str,
        globals: Optional[Dict[str, Any]] = None,
        locals: Optional[Dict[str, Any]] = None,
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> Any:
        if name in libraries:
            return importlib.__import__(name, globals, locals, fromlist, level)
        else:
            raise ImportError(f"Restricted import: {name}")

    return restricted_imports


def guarded_getitem(ob: Dict[str, Any], index: str) -> Any:
    # No restrictions.
    return ob[index]


def guarded_write(allowed_classes: list[str]):
    def guarded_write(ob):
        if ob.__class__.__name__ in allowed_classes:
            return ob
        else:
            raise AttributeError(f"Restricted write: {ob.__class__.__name__}")

    return guarded_write


def guarded_getiter(ob):
    return ob


def guarded_unpack_sequence(it, spec, _getiter_):
    """Protect nested sequence unpacking.

    Protect the unpacking of 'it' by wrapping it with '_getiter_'.
    Furthermore for each child element, defined by spec,
    guarded_unpack_sequence is called again.

    Have a look at transformer.py 'gen_unpack_spec' for a more detailed
    explanation.
    """
    # Do the guarded unpacking of the sequence.
    ret = list(_getiter_(it))

    # If the sequence is shorter then expected the interpreter will raise
    # 'ValueError: need more than X value to unpack' anyway
    # => No children are unpacked => nothing to protect.
    if len(ret) < spec["min_len"]:
        return ret

    # For all child elements do the guarded unpacking again.
    for idx, child_spec in spec["children"]:
        ret[idx] = guarded_unpack_sequence(ret[idx], child_spec, _getiter_)

    return ret


def implement_policy(
    safe_globals: dict, import_globals: dict = {}, libraries: list[str] = [], allowed_write_classes: list[str] = []
) -> None:
    safe_globals.update(import_globals)
    safe_globals["__metaclass__"] = type
    safe_globals["__name__"] = globals()["__name__"]
    safe_globals["_getitem_"] = guarded_getitem
    safe_globals["__builtins__"]["__import__"] = custom_imports(libraries)
    safe_globals["dict"] = dict
    safe_globals["_write_"] = guarded_write(allowed_write_classes)
    safe_globals["_getiter_"] = guarded_getiter
    safe_globals["_iter_unpack_sequence_"] = guarded_unpack_sequence
    safe_globals["__builtins__"]["enumerate"] = globals()["__builtins__"]["enumerate"]
