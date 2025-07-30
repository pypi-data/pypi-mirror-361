## <ins> Pact: Attribute Enforcement Metaclass for Python </ins>

Pact is a lightweight Python metaclass designed to enforce the presence and types of class attributes in subclasses <br>
It helps you ensure that all subclasses implement the required attributes declared in the base class, <br>
catching missing or mistyped attributes early with warnings and exceptions <br>

### <ins> Features </ins>

- Enforce presence of specific class or instance attributes in subclasses
- Type validation of annotated attributes
- Raises PactException exception and emits warnings for missing or mismatched attributes

### <ins> Installation </ins>

You can install this package via PIP: pip install python-pact

### <ins> Usage </ins>

```python
from pact import Pact


class Person(Pact):
    name: str
    age: int


class JohnDoe(Person):
    name = 'John Doe'
    age = 25


# This will raise PactException due to missing 'age':
class JaneDoe(Person):
    name = 'Jane Doe'
```
