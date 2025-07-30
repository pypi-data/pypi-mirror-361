# setup.py

from setuptools import setup, find_packages

setup(
    name="ejercicio13-camaljac", # Nombre del paquete en PyPI (debe ser único)
    version="0.1.0",             # Versión inicial del paquete
    author="camaljac",     # Nombre o alias
    author_email="camaljac@gmail.com", # Correo electrónico
    description="Un módulo simple para operaciones matemáticas básicas.",
    long_description=open("README.md").read(), # Descripción larga desde un archivo README
    long_description_content_type="text/markdown", # Tipo de contenido para long_description
    packages=find_packages(),     # Encuentra automáticamente los paquetes en el directorio
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", # Elige una licencia (MIT es común y permisiva)
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
    ],
    python_requires='>=3.8',      # Versión mínima de Python requerida
    keywords="calculadora matematicas suma resta multiplicacion division", # Palabras clave para la búsqueda en PyPI
)