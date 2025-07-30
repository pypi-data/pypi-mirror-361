import warnings
from typing import get_origin, get_args, Union


class PactException(Exception):
    def __init__(self, cls_name: str, missing_attributes: list[str]):
        super().__init__(f'PactException: Class "{cls_name}" is missing required attributes: {missing_attributes}')


def _check_type(value, expected_type):
    """
    Simple type check that handles basic types and typing.Union.
    You can extend this function for full typing support if needed.
    """
    origin = get_origin(expected_type)
    if origin is Union:
        return any(isinstance(value, arg) for arg in get_args(expected_type))
    else:
        return isinstance(value, expected_type)


class PactMeta(type):
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

        if name == 'Pact' and cls.__module__ == __name__:
            return

        annotated_attributes = {}
        for base in reversed(cls.__mro__):
            annotated_attributes.update(base.__dict__.get('__annotations__', {}))

        if not annotated_attributes:
            return

        # Skip if all missing (abstract base)
        no_attributes_defined = all(not hasattr(cls, attr) for attr in annotated_attributes)
        if no_attributes_defined:
            return

        missing_or_type_mismatch = []
        for attr, expected_type in annotated_attributes.items():
            if not hasattr(cls, attr):
                missing_or_type_mismatch.append(attr)
                continue

            value = getattr(cls, attr)
            if not _check_type(value, expected_type):
                missing_or_type_mismatch.append(attr)

        if missing_or_type_mismatch:
            warnings.warn(
                f'Class "{name}" is missing required Pact attributes or has wrong types: {missing_or_type_mismatch}',
                UserWarning
            )
            raise PactException(name, missing_or_type_mismatch)


class Pact(metaclass=PactMeta):
    pass
