from setuptools import find_packages, setup
from setuptools.extension import Extension

# Define setup requirements first
setup_requires = ["cython>=0.29.0"]
install_requires = ["cython>=0.29.0"]


# Create a function to get extensions
def get_extensions():  # noqa: D103
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
        },
    )


setup(
    name="diffr",
    version="0.1.0",
    packages=find_packages(),
    setup_requires=setup_requires,
    install_requires=install_requires,
    ext_modules=get_extensions(),
    entry_points={
        "console_scripts": [
            "diffr = diffr.cli:main",
        ],
    },
)
