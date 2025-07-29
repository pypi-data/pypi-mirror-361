# add_simple_package

Un *Hello World* de publication sur PyPI avec deux fonctionnalités principales :

- `add` : addition de deux nombres scalaires.
- `add_arrays` : addition de deux tableaux NumPy.

## Installation

```bash
pip install add-simple-package
```

## Exemples Utilisation

### Addition de scalaires

```python
from add_simple_package import add

print(add(2, 3))  # Résultat : 5
```

### Addition de tableaux NumPy

```python
from add_simple_package import add_arrays
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

result = add_arrays(a, b)
print(result)  # [5 7 9]
```

