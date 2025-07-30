from setuptools import setup, Extension

# This setup.py is kept for compatibility reasons, to support editable installs
# and to build the C extension.
# All project metadata is now defined in pyproject.toml.

setup(
    ext_modules=[
        Extension(
            # The name of the extension module.
            # The path corresponds to where the Python wrapper will find it.
            name="iic_guard._c_iic_guard",
            sources=["iic_guard/c_src/iic_guard.c"],
        )
    ]
) 