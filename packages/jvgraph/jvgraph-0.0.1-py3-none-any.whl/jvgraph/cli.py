"""Jivas Graph CLI tool."""

from jvgraph.group import jvgraph
from jvgraph.commands.launch import launch


# Register command groups
jvgraph.add_command(launch)


if __name__ == "__main__":
    jvgraph()  # pragma: no cover
