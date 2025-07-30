import setuptools

with open("README.rst", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="sabatron_tryton_rpc_client",
    version="7.4.0-rc.1",
    author="mono",
    author_email="monomono@disroot.org",
    description="Python RPC Client for Tryton",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://git.disroot.org/sabatron/sabatron-tryton-rpc-client",
    license="GPL-3",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    test_suite="tests",
    keywords='tryton client'
)
