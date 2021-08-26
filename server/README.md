# zupplin - backend server

![Pyright](https://github.com/Fyssion/zupplin/actions/workflows/server_pyright.yml/badge.svg)

This is the backend server for Zupplin, written in [Python](https://www.python.org/) and using [Tornado](https://www.tornadoweb.org/).

## Installation

> Python 3.9+, PostgreSQL 13, and [Poetry](https://python-poetry.org/) are **required** for installation.

```sh
# Clone the repository from GitHub and enter the server directory.
git clone https://github.com/Fyssion/zupplin.git
cd zupplin/server

# OPTIONAL: create and activate a virtual env to house the requirements.
python3 -m venv venv
source venv/bin/activate

# Install the requirements.
poetry install

# Copy the example config
cp config.example.toml config.toml
# Edit the config to your satisfaction.

# Setup the PostgreSQL database.
# See the Database Setup section below for more info.

# Run the server.
python3 -m app
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

### Code Style

Please try to keep the code style consistant with the existing project code.
The project mostly follows [PEP-8 guidelines](https://python.org/dev/peps/pep-0008) with a max column length of 150.
All code changes are also checked with the [Pyright type checker](https://github.com/microsoft/pyright).
Pyright is currently set to run on its basic mode.
