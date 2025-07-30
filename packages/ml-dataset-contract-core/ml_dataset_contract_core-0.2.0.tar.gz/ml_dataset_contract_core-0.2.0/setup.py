from pathlib import Path
from setuptools import setup, find_namespace_packages

ROOT = Path(__file__).parent

setup(
    name="ml_dataset_contract_core",
    description="Runtime core for ML dataset contracts.",
    long_description=(
        ROOT / "README.md"
    ).read_text(encoding="utf-8") if (ROOT / "README.md").exists() else "",
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
    license="MIT",
    author="Nikolskii D.N.",
    url="https://github.com/nikolskydn/ml_dataset_contract_core",
    use_scm_version={
        "version_scheme": "no-guess-dev",
        "local_scheme":  "no-local-version",
        "fallback_version": "0.0.0",
    },
    setup_requires=["setuptools_scm[toml]>=8"],
    # --------------------------------------------
    package_dir={"": "src"},
    packages=find_namespace_packages(
        "src",
        include=["ml_dataset_contract.runtime*"],
    ),
    install_requires=[
        "pydantic>=2.6",
        "pyyaml>=6.0",
    ],
    include_package_data=False,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Framework :: Pydantic",
        "Operating System :: OS Independent",
    ],
)
