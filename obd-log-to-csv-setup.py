[check-manifest]
ignore =
    *.sublime-project
    .git*
    .vscode/*
    data/*
    tmp/*
    examples/*
    docs/*
    .mypy*
    .pytest*
    __pycache__*


[metadata]
name = telemetry-obd-log-to-csv
author = Larry Pearson
author_email = not-an-email-address@gmail.com
version = 0.3.3
description = Telemetry Onboard Diagnostic Data Logger output to CSV file.
long_description = file:README.md
long_description_content_type = text/markdown
url = https://github.com/thatlarrypearson?tab=repositories
license = MIT
classifiers =
    Development Status :: 4 - Beta
    Environment :: Web Environment
    Intended Audience :: Developers
    License :: OSI Approved :: MIT License
    Operating System :: OS Independent
    Natural Language :: English
    Programming Language :: Python :: 3 :: Only
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: Implementation :: CPython
    Topic :: Software Development :: Libraries :: Application Frameworks
    Topic :: Software Development :: Libraries :: Python Modules

[options]
include_package_data = true
python_requires = >=3.8
setup_requires = 
    setuptools >= 38.3.0
install_requires =
    pint == 0.20.1
    rich == 13.6.0
    python-dateutil == 2.8.2
    obd == 0.7.2
packages = find:
