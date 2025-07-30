# ejercicio13/operaciones.py

def sumar(a, b):
    """
    Realiza la suma de dos números.
    """
    return a + b

def restar(a, b):
    """
    Realiza la resta de dos números.
    """
    return a - b

def multiplicar(a, b):
    """
    Realiza la multiplicación de dos números.
    """
    return a * b

def dividir(a, b):
    """
    Realiza la división de dos números.
    Lanza un ValueError si el divisor es cero.
    """
    if b == 0:
        raise ValueError("No se puede dividir por cero.")
    return a / b