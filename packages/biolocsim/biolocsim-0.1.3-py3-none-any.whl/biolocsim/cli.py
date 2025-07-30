"""Console script for biolocsim."""

import click


@click.command()
def main():
    """Main entrypoint."""
    click.echo("biolocsim")
    click.echo("=" * len("biolocsim"))
    click.echo("A Python library for simulating SMLM point cloud data.")


if __name__ == "__main__":
    main()  # pragma: no cover
