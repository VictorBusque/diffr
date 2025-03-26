import os

from setuptools import find_packages, setup
from setuptools.extension import Extension

# Define setup requirements first
setup_requires = ["cython>=0.29.0"]
install_requires = ["cython>=0.29.0", "pydantic>=2.10.6"]


# Create a function to get extensions
def get_extensions():  # noqa: D103
    try:
        # Only import Cython when needed
        from Cython.Build import cythonize

        # Define Cython extension modules
        extensions = [
            Extension(
                "diffr.core.myers",
                sources=["diffr/core/myers.pyx"],
                extra_compile_args=["-O3"],  # Optimize for speed
            ),
            Extension(
                "diffr.core.patience",
                sources=["diffr/core/patience.pyx"],
                extra_compile_args=["-O3"],  # Optimize for speed
            ),
        ]

        return cythonize(
            extensions,
            compiler_directives={
                "language_level": "3",
                "boundscheck": False,
                "wraparound": False,
                "nonecheck": False,
                "cdivision": True,
                "initializedcheck": False,
                "overflowcheck": False,
                "infer_types": True,  # infiere automáticamente algunos tipos
            },
        )
    except ImportError:
        # If Cython is not available, return an empty list of extensions
        import warnings

        warnings.warn("Cython not available, building without Cython extensions")
        return []


# Get long description from README if available
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="diffr",
    version="0.1.0",
    description="A diff utility library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Victor Busques Somacarrera",
    packages=find_packages(),
    setup_requires=setup_requires,
    install_requires=install_requires,
    ext_modules=get_extensions(),
    package_data={
        "diffr": ["*.pyi", "**/*.pyi"],
    },
    include_package_data=True,
    zip_safe=False,  # Necessary for including .pyi files
    entry_points={
        "console_scripts": [
            "diffr = diffr.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
)
