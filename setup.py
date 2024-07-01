from os import path
from platform import system

from setuptools import Extension, find_packages, setup
from setuptools.command.build import build
from wheel.bdist_wheel import bdist_wheel

sources = [
    "bindings/python/tree_sitter_printf/binding.c",
    "src/parser.c",
]
if path.exists("src/scanner.c"):
    sources.extend("src/scanner.c")

if system() != "Windows":
    cflags = ["-std=c11", "-fvisibility=hidden"]
else:
    cflags = ["/std:c11", "/utf-8"]


class Build(build):
    def run(self):
        if path.isdir("queries"):
            dest = path.join(self.build_lib, "tree_sitter_printf", "queries")
            self.copy_tree("queries", dest)
        super().run()


class BdistWheel(bdist_wheel):
    def get_tag(self):
        python, abi, platform = super().get_tag()
        if python.startswith("cp"):
            python, abi = "cp39", "abi3"
        return python, abi, platform


setup(
    packages=find_packages("bindings/python"),
    package_dir={"": "bindings/python"},
    package_data={
        "tree_sitter_printf": ["*.pyi", "py.typed"],
        "tree_sitter_printf.queries": ["*.scm"],
    },
    ext_package="tree_sitter_printf",
    ext_modules=[
        Extension(
            name="_binding",
            sources=sources,
            extra_compile_args=cflags,
            define_macros=[
                ("Py_LIMITED_API", "0x03090000"),
                ("PY_SSIZE_T_CLEAN", None),
                ("TREE_SITTER_HIDE_SYMBOLS", None),
            ],
            include_dirs=["src"],
            py_limited_api=True,
        )
    ],
    cmdclass={
        "build": Build,
        "bdist_wheel": BdistWheel
    },
    zip_safe=False
)