from __future__ import annotations

from tp.maya import api

from tp.core import dcc, command


def orient_nodes(
        nodes: list[api.DagNode], primary_axis: api.OpenMaya.MVector, secondary_axis: api.OpenMaya.MVector,
        world_up_axis: api.OpenMaya.MVector, skip_end: bool = True):
    """
    Orients each one of the given nodes to the next in the list.

    :param list[api.DagNode] nodes: list of nodes from parent to child.
    :param api.OpenMaya.MVector primary_axis: primary (aim) axis for each node.
    :param api.OpenMaya.MVector secondary_axis: secondary (up) axis for each node.
    :param api.OpenMaya.MVector world_up_axis: world up axis to align all nodes.
    :param api.OpenMaya.MVector skip_end: whether the last node should be aligned.
    """

    return command.execute('tp.maya.nodes.orient', **locals())
