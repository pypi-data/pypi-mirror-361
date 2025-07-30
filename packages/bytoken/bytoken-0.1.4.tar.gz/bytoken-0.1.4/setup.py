from skbuild import setup

setup(
    name="bytoken",
    version="0.1.4",
    description="A fast C++ BPE tokenizer with Python bindings",
    author="Vaibhav Sharma",
    license="MIT",
    packages=["bytoken"],
    package_data={"bytoken": ["*.pyi"]},
    package_dir={"bytoken": "bytoken"},
    cmake_install_dir="bytoken",  # where to install the .so file
    python_requires=">=3.7",
)
