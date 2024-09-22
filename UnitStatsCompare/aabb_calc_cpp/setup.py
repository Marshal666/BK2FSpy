# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

__version__ = "0.0.2"

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

ext_modules = [
    Pybind11Extension(
        "aabb_hit_calc",
        ["src/main.cpp"],
        # Example: passing in the version to the compiled code
        define_macros=[("VERSION_INFO", __version__)],
        extra_compile_args=['-std=c++17'],
    ),
]

setup(
    name="aabb_hit_calc",
    version=__version__,
    author="Field Marshal",
    author_email="field.marshal (discord)",
    url="none",
    description="AABB hit probability calculation library",
    long_description="",
    ext_modules=ext_modules,
    zip_safe=False,
    python_requires=">=3.7",
)
