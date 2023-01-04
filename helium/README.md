# zupplin - helium

![lint](https://github.com/Fyssion/zupplin/actions/workflows/helium_lint.yml/badge.svg)
![test](https://github.com/Fyssion/zupplin/actions/workflows/helium_test.yml/badge.svg)

This is the backend API and WS server for zupplin, written in [Python](https://www.python.org/) using [Tornado](https://www.tornadoweb.org/).

## Installation

> Python 3.11+ and PostgreSQL 13 are **required** for installation.
> Installing [Hatch](hatch.pypa.io/) is highly recommended for dev environments, but not required.

```sh
# You are assumed to be in the helium directory before completing these steps.

# Copy and edit the example config.
cp config.example.toml config.toml

# Before running the server, you must setup the PostgreSQL database.
# See the Database Setup section below for more info.
# After doing so, use the following command(s) to start the server.

# With Hatch (recommended)
hatch run start

# Without Hatch
pip install .
python -m app
```

### Database Setup

To setup PostgreSQL, use the following SQL statements in your database:

```sql
CREATE ROLE zupplin WITH LOGIN PASSWORD 'yourpw';
CREATE DATABASE zupplin OWNER zupplin;
```

Then, edit the config to use the correct database URI.
Your URI should look something like this:
`postgresql://user:password@localhost:5432/database`

On first start, the server will initialize the database.
If you wish to drop the tables in the database, you can run `python3 -m app db drop`.

## Contributing

Please read the following guidelines before submitting code changes to this codebase.

### Running Tests

Tests are performed using pytest. Use `hatch run test:test` to run all tests.

### Code Style

Please try to keep the code style consistent with the existing project code.
The project mostly follows [PEP-8 guidelines](https://python.org/dev/peps/pep-0008) with a max column length of 100.
All code changes are also checked with the [Pyright type checker](https://github.com/microsoft/pyright).
Pyright is currently set to run on its basic mode.  
Use `hatch run style:check` to check your code style.
To run Pyright locally, first install Pyright (via pip or npm) then run it with `hatch run test:lint`.

run
