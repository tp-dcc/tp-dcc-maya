from __future__ import annotations

import maya.cmds as cmds

MAYA_TRANSLATE_ATTRS = ['translateX', 'translateY', 'translateZ']
MAYA_ROTATE_ATTRS = ['rotateX', 'rotateY', 'rotateZ']
MAYA_SCALE_ATTRS = ['scaleX', 'scaleY', 'scaleZ']
MAYA_TRANSFORM_ATTRS = MAYA_TRANSLATE_ATTRS + MAYA_ROTATE_ATTRS + MAYA_SCALE_ATTRS


def reset_transform_attributes(
		node_name: str, translate: bool = True, rotate: bool = True, scale: bool = True, visibility: bool = False):
	"""
	Resets teh transforms of the given node name.

	:param str node_name: name of the node whose transform attributes we want to reset.
	:param bool translate: whether to reset translate transform attributes.
	:param bool rotate: whether to reset rotate transform attributes.
	:param bool scale: whether to reset scale transform attributes.
	:param bool visibility: whether to reset visibility attribute.
	"""

	if translate:
		cmds.setAttr(f'{node_name}.translate', 0.0, 0.0, 0.0)
	if rotate:
		cmds.setAttr(f'{node_name}.rotate', 0.0, 0.0, 0.0)
	if scale:
		cmds.setAttr(f'{node_name}.scale', 1.0, 1.0, 1.0)
	if visibility:
		cmds.setAttr(f'{node_name}.visibility', 1.0)


def locked_connected_attributes(
		node: str, attributes: list[str] | None = None, keyframes: bool = False,
		constraints: bool = False) -> list[str]:
	"""
	Retrieves all locked or connected attributes from the given list of nodes.

	:param str node: Maya node full path names.
	:param list[str] or None attributes: list of attributes to check. If not given, all keyable attributes will be
		checked.
	:param bool keyframes: whether to check for keyframes.
	:param bool constraints: whether to check for constraints.
	:return: list with all the attributes locked or connected.
	:rtype: list[str]
	"""

	locked_connected_attrs: list[str] = []

	attributes = attributes or cmds.listAttr(node, keyable=True)
	for attr in attributes:
		node_attr = '.'.join((node, attr))
		if not cmds.getAttr(node_attr, settable=True):
			locked_connected_attrs.append(node_attr)
		if keyframes and cmds.keyframe(node, attribute=attr, selected=False, query=True):
			locked_connected_attrs.append(node_attr)

	if constraints:
		for attr in attributes:
			node_attr = '.'.join((node, attr))
			if cmds.listConnections(node_attr, type='constraint'):
				locked_connected_attrs.append(node_attr)

	return locked_connected_attrs


def locked_connected_attributes_for_nodes(
		nodes: list[str], attributes: list[str] | None = None, keyframes: bool = False, constraints: bool = False):
	"""
	Retrieves all locked or connected attributes from the given list of nodes.

	:param list[str] nodes: list of Maya node full path names.
	:param list[str] or None attributes: list of attributes to check. If not given, all keyable attributes will be
		checked.
	:param bool keyframes: whether to check for keyframes.
	:param bool constraints: whether to check for constraints.
	:return: a tuple containing the list of nodes with locked or connected attributes and also all the attributes locked
		or connected.
	"""

	locked_nodes: list[str] = []
	locked_attributes: list[str] = []

	for node in nodes:
		locked_connected_attrs = locked_connected_attributes(
			node, attributes=attributes, keyframes=keyframes, constraints=constraints)
		if locked_connected_attrs:
			locked_nodes.append(node)
			locked_attributes.extend(locked_connected_attrs)

	return locked_nodes, locked_attributes
