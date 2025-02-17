# pyright: reportUnknownMemberType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnnecessaryTypeIgnoreComment=false

import functools
import logging
import re
from typing import Any

from graphviz import Digraph
from graphviz.graphs import BaseGraph

from ospx import Component, Connection, OspSimulationCase

__ALL__ = ["Graph"]

logger = logging.getLogger(__name__)


class Graph:
    """Class providing methods to generate a visual dependency graph of a system's components and its connections."""

    @staticmethod
    def generate_dependency_graph(case: OspSimulationCase) -> None:
        """Generate a dependency graph of the system structure as pdf, for documentation.

        Note: This requires graphviz to be installed on the local machine
        """
        graphiz_not_found_error_mesage: str = (
            "OspSimulationCase.generate_dependency_graph(): failed to run graphviz. \n"
            "To generate the system structure dependency graph, graphviz needs to be installed on the local machine. \n"
            "Kindly check your local installation of graphviz."
        )

        label: str
        shape: str
        style: str
        color: str
        fontcolor: str
        fillcolor: str
        penwidth: tuple[str]
        weight: tuple[str]

        # Default styles
        text_size: str = "11"
        styles: dict[str, dict[str, str]] = {
            "graph": {
                "label": f"{case.simulation.name}",
                "fontname": "Verdana",
                "fontsize": text_size,
                "fontcolor": "black",
                "bgcolor": "white",
                "rankdir": "TD",
                "overlap": "compress",
                "sep": "10,100",
                "remincross": "true",
                "ratio": "fill",
                "margin": "0",
                "size": "10, 10!",
            },
            "nodes": {
                "fontname": "Verdana",
                "fontsize": text_size,
                "fontcolor": "white",
                "shape": "square",
                "color": "magenta",
                "style": "filled",
                "fillcolor": "magenta",
            },
            "edges": {
                "style": "dashed",
                "color": "magenta",
                "penwidth": "3",
                "arrowhead": "open",
                "fontname": "Verdana",
                "fontsize": text_size,
                "fontcolor": "magenta",
            },
        }

        basic_op_names: str = "(power|dot|sum|diff|prod|div|quotient)"
        input_names: str = "^(INP|inp)"

        callgraph: BaseGraph
        try:
            digraph = functools.partial(Digraph, format="png")
            callgraph = digraph()
            callgraph = _apply_styles(callgraph, styles)
        except Exception:
            logger.exception(graphiz_not_found_error_mesage)
            return

        # Components
        for component in case.system_structure.components.values():
            label_key, label = _get_node_label(component)
            label = _create_table(
                label_key,
                {
                    "source:": component.fmu.file.name,
                    "stepsize:": component.step_size,
                    "variables:": "",
                },
            )

            if re.search(input_names, component.name):
                shape = "diamond"
                style = "filled,rounded"
                fillcolor = "#FFFFFF"
            elif re.search(basic_op_names, component.name, re.IGNORECASE):
                shape = "square"
                style = "filled, rounded"
                fillcolor = "#EEBBDD"
            else:
                shape = "square"
                style = "filled"
                fillcolor = "#DDDDEE"

            callgraph.node(
                label_key,
                label=label,
                fontname="Verdana",
                fontsize=text_size,
                fontcolor="black",
                shape=shape,
                color="black",
                style=style,
                fillcolor=fillcolor,
            )

        # Connections

        for connection in case.system_structure.connections.values():
            if not (connection.source_endpoint and connection.target_endpoint):
                return
            if not (connection.source_endpoint.component and connection.target_endpoint.component):
                return
            from_key: str = connection.source_endpoint.component.name
            to_key: str = connection.target_endpoint.component.name

            label = _get_edge_label(connection)

            if re.search(input_names, from_key, re.IGNORECASE):
                label = f"input\n{label}"
                style = "dashed"
                color = "#003399"
                fontcolor = "#003399"
                penwidth = (f"{1:d}",)
                weight = (f"{1:d}",)

            elif re.search(basic_op_names, from_key, re.IGNORECASE):
                style = "filled"
                color = "#995566"
                fontcolor = "#663344"
                penwidth = (f"{3:d}",)
                weight = (f"{0.66:.2f}",)

            else:
                style = "bold"
                color = "black"
                fontcolor = "black"
                penwidth = (f"{int(round((2) ** 1.5, 0))}",)
                weight = (f"{int(round((2) ** 1.5, 0))}",)

            callgraph.edge(
                from_key,
                to_key,
                style=style,
                color=color,
                arrowhead="open",
                fontname="Verdana",
                fontsize=text_size,
                fontcolor=fontcolor,
                penwidth=str(penwidth),
                weight=str(weight),
                label=label,
                overlap="false",
                splines="true",
            )

        # Create callGraph pdf

        try:
            _ = callgraph.render(f"{case.simulation.name}_callGraph", format="pdf")
        except Exception:
            logger.exception(graphiz_not_found_error_mesage)

        return


def _apply_styles(digraph: BaseGraph, styles: dict[str, Any]) -> BaseGraph:
    digraph.graph_attr.update(("graph" in styles and styles["graph"]) or {})
    digraph.node_attr.update(("nodes" in styles and styles["nodes"]) or {})
    digraph.edge_attr.update(("edges" in styles and styles["edges"]) or {})
    return digraph


def _get_node_label(component: Component) -> tuple[str, str]:
    label = f"{component.name}\n___________\n\nfmu\n"
    label += re.sub(r"(^.*/|^.*\\|\.fmu.*$)", "", component.fmu.file.name)

    label_key = component.name
    return label_key, label


def _get_edge_label(connection: Connection) -> str:
    return (
        f"{connection.source_endpoint.variable_name}-->{connection.target_endpoint.variable_name}"
        if connection.is_valid
        else ""
    )


def _create_table(name: str, child: dict[str, Any] | None = None) -> str:
    _child: dict[str, Any] = child or {" ": " "}
    n_child = len(_child)
    string: str = (
        f'<\n<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">\n<TR>\n'
        f'<TD COLSPAN="{2 * n_child:d}">{name}</TD>\n</TR>\n'
    )
    for key, item in _child.items():
        string += f"<TR><TD>{key}</TD><TD>{item}</TD></TR>\n"
    string += "</TABLE>\n>"

    return string
