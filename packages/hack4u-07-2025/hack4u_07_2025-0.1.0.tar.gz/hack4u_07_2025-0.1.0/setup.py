from setuptools import setup, find_packages

# Configuración mínima requerida
setup(
    name="hack4u-07-2025",  
    version="0.1.0",  
    packages=find_packages(),  
    install_requires=[],  
    
    # Metadatos importantes
    author="sergiobrvo01",
    description="Biblioteca Hack4u para busquedas",
    long_description=open("README.md").read(),  
    long_description_content_type="text/markdown",
    license="MIT",  # Licencia (ej: "MIT", "Apache-2.0")
    
    # Clasificadores (opciones en https://pypi.org/classifiers/)
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Versión mínima de Python
)
