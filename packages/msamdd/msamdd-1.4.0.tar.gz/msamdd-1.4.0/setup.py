# setup.py – MSAMDD
# Build two Pybind11 extensions that statically link against IBM CPLEX 22.1.x

from pathlib import Path
from setuptools import setup, Extension, find_packages
import glob, pybind11, sys

ROOT = Path(__file__).parent.resolve()

# ────────────────────────────────
#  CPLEX include & library paths
# ────────────────────────────────
CPLEX_INC   = ROOT / "vendor" / "cplex" / "include" / "cplex"
CONCERT_INC = ROOT / "vendor" / "cplex" / "include" / "concert"

include_dirs = [
    pybind11.get_include(),
    str(CPLEX_INC),
    str(CONCERT_INC),
    "src",
    "src/src_aff",
    "src/src_cnv",
]

STATIC_LIBS = [
    str(ROOT / "vendor" / "cplex" / "lib" / "static_pic" / "libcplex.a"),
    str(ROOT / "vendor" / "cplex" / "lib" / "static_pic" / "libilocplex.a"),
    str(ROOT / "vendor" / "cplex" / "lib" / "static_pic" / "libconcert.a"),
]

extra_cxx = ["-std=c++17"]

# ────────────────────────────────
#  Helper to define each extension
# ────────────────────────────────
def make_ext(py_name: str, src_glob: str, wrapper_cpp: str) -> Extension:
    sources = glob.glob(src_glob) + [wrapper_cpp]
    return Extension(
        f"msamdd.{py_name}",
        sources=sources,
        include_dirs=include_dirs,
        extra_compile_args=extra_cxx,
        extra_link_args=STATIC_LIBS,
        language="c++",
    )

ext_modules = [
    make_ext("_optmsa_aff", "src/src_aff/*.cpp",  "python/msamdd/wrapper_aff.cpp"),
    make_ext("_optmsa_cnv", "src/src_cnv/*.cpp",  "python/msamdd/wrapper_cnv.cpp"),
]

# ────────────────────────────────
#  Set-up metadata
# ────────────────────────────────
setup(
    name="msamdd",
    version="1.4.0",  # bumped
    description="Exact multiple sequence alignment via Synchronized Decision Diagrams",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Yeswanth Vootla",
    author_email="vootlayeswanth20@gmail.com",
    license="GPL-2.0-or-later",
    python_requires=">=3.8, <3.14",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    include_package_data=True,
    # ────────────────────────────────
    # include static libs in the wheel
    # ────────────────────────────────
    package_data={
        "msamdd": [
            "vendor/cplex/lib/static_pic/*.a",
            "vendor/cplex/lib/static_pic/*.so",
        ],
    },
    ext_modules=ext_modules,
    install_requires=[
        "pybind11>=2.6",
    ],
    # ────────────────────────────────
    # CLI entry-points
    # ────────────────────────────────
    entry_points={
        "console_scripts": [
            "msa_cnv = msamdd.cli_cnv:main",
            "msa_aff = msamdd.cli_aff:main",
        ],
    },
    zip_safe=False,
)
