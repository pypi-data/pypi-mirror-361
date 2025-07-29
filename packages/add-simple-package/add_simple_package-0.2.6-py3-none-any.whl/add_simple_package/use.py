from addition import add
from addition_arrays import add_arrays

print(add(2, 3))  # Résultat: 5

import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

print(add_arrays(a, b))  # Résultat: [5 7 9]
