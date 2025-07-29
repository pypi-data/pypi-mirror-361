import numpy as np

def add_arrays(a, b):
    """
    Additionne deux tableaux NumPy élément par élément.
    
    Parameters:
        a (array-like): Premier tableau.
        b (array-like): Deuxième tableau.
        
    Returns:
        numpy.ndarray: Résultat de l'addition élément par élément.
    """
    return np.add(a, b)

