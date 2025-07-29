"""Allow devctx to be executed as a module with python -m devctx."""

from devctx.cli import cli

if __name__ == "__main__":
    cli() 