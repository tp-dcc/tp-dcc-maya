from __future__ import annotations

from typing import Sequence

import maya.cmds as cmds

from tp.core import log
from tp.maya.cmds import gui
from tp.maya.cmds.nodes import attributes

logger = log.tpLogger


def joint_chains(
        joints: list[str], ignore_connected_joints: bool = True,
        filter_type: str = 'joint') -> tuple[list[list[str]], list[str]]:
    """
    Checks the given list of joints for chans and returns a list of chains, each branch being a separated chain.

    :param list[str] joints: list of Maya joint full path names.
    :param bool ignore_connected_joints: whether to skip any joints with keyframes, connections, constraints or locked
        attributes
    :param str filter_type: type of node to filter by ('transform' or 'joint').
    :return: list containing a list for each joint chain found.
    :rtype: tuple[list[list[str]], list[str]]
    ..note:: each member of the joint chains must be in the given list of nodes.
    """

    ignore_joints: list[str] = []
    chain_lists: list[list[str]] = []
    end_joints: list[str] = []
    already_recorded_joints: list[str] = []

    if ignore_connected_joints:
        joints_to_ignore = attributes.locked_connected_attributes_for_nodes(
            joints, attributes=attributes.MAYA_TRANSFORM_ATTRS, keyframes=True, constraints=True)[0]
        if ignore_joints:
            joints = [x for x in joints if x not in ignore_joints]

    # Retrieve all joints.
    for joint in joints:
        end = True
        child_joints = cmds.listRelatives(joint, children=True, type=filter_type, fullPath=True)
        if child_joints:
            for child_joint in child_joints:
                if child_joint in joints:
                    end = False
        if not child_joints or end:
            end_joints.append(joint)

    # Loop backward all joints.
    for end_joint in end_joints:
        joints_chain: list[str] = [end_joint]
        already_recorded_joints.append(end_joint)
        last_joint_parent = cmds.listRelatives(end_joint, parent=True, type=filter_type, fullPath=True)\

        # Next chain has no parent.
        if not last_joint_parent:
            chain_lists.append(joints_chain)
            continue

        # Next chain parent is not in the joints list.
        last_joint_parent = last_joint_parent[0]
        if last_joint_parent not in joints:
            chain_lists.append(joints_chain)
            continue

        while last_joint_parent:
            joints_chain.append(last_joint_parent)
            already_recorded_joints.append(last_joint_parent)
            parent_joint = cmds.listRelatives(last_joint_parent, parent=True, type=filter_type, fullPath=True)
            if parent_joint:
                parent_joint = parent_joint[0]
            if not parent_joint:
                last_joint_parent = None
            elif parent_joint not in joints or parent_joint in already_recorded_joints:
                last_joint_parent = None
            else:
                last_joint_parent = parent_joint

        chain_lists.append(joints_chain)

    for chain in chain_lists:
        chain.reverse()

    return chain_lists, ignore_joints


def filter_child_joints(joints: list[str]) -> list[str]:
    """
    Retrieve all child joints under the given list of joints in the hierarchy.

    :param list[str] joints: list of joints to get child joints from.
    :return: list of the given joints with all their child joints (without duplicates).
    :rtype: list[str]
    """

    all_joints: list[str] = []
    for joint in joints:
        all_joints.append(joint)
        all_joints.extend(cmds.listRelatives(joint, allDescendents=True, type='joint', fullPath=True) or [])

    return list(set(all_joints))


def align_joint_to_parent(joint: str):
    """
    Aligns given joint to its parent.
    Uses orient constraint (while temporally un-parenting children) to re-orient the joint to match parent orientation.
    Freezes joint transforms before re-parenting children.

    :param str joint: joint to orient to its parent.
    """

    children = cmds.listRelatives(joint, children=True, fullPath=True)
    parent = cmds.listRelatives(joint, parent=True, fullPath=True)
    if children:
        children = cmds.parent(children, world=True)
    cmds.delete(cmds.orientConstraint(parent[0], joint, maintainOffset=False))
    cmds.makeIdentity(joint, apply=True, r=True)
    if children:
        cmds.parent(children, joint)


def align_joints_to_parent(joints: list[str]):
    """
    Aligns given joints to its parent.
    Uses orient constraint (while temporally un-parenting children) to re-orient the joint to match parent orientation.
    Freezes joint transforms before re-parenting children.

    :param list[str] joints: list of joints to orient to their parents.
    """

    [align_joint_to_parent(joint) for joint in joints]


def align_selected_joints_to_parent():
    """
    Aligns selected joints to its parent.
    Uses orient constraint (while temporally un-parenting children) to re-orient the joint to match parent orientation.
    Freezes joint transforms before re-parenting children.
    """

    selected_joints = cmds.ls(selection=True, exactType='joint', long=True)
    if not selected_joints:
        logger.warning('No joints found. Please select some joints.')
        return

    align_joints_to_parent(selected_joints)
    cmds.select(selected_joints, replace=True)

    logger.debug('Joints aligned to their parent successfully!')


def edit_component_lra(flag: bool = True):
    """
    Makes the local rotation axis editable/no editable in component mode.

    :param bool flag: If True, local rotation axis is editable in component mode; if False, disables it and exit to
        object mode.
    """

    if flag:
        cmds.selectMode(component=True)
        cmds.selectType(localRotationAxis=True)
        current_panel = gui.panel_under_pointer_or_focus(viewport3d=True, message=False)
        cmds.modelEditor(current_panel, edit=True, handles=True)
    else:
        cmds.selectType(localRotationAxis=False)
        cmds.selectMode(object=True)


def zero_joints_rotation_axis(joints: list[str], zero_children: bool = True):
    """
    Zeroes out the joint rotation of given joints.

    :param list[str] joints: list of joints.
    :param bool zero_children: whether to zero out also rotation axis of child joints.
    """

    if zero_children:
        joints = filter_child_joints(joints)
    for joint in joints:
        cmds.joint(joint, edit=True, zeroScaleOrient=True)


def zero_selected_joints_rotation_axis(zero_children: bool = True):
    """
    Zeroes out the joint rotation of selected joints.

    :param bool zero_children: whether to zero out also rotation axis of child joints.
    """

    selected_joints = cmds.ls(selection=True, exactType='joint', long=True)
    if not selected_joints:
        logger.warning('No joints found. Please select some joints.')
        return

    zero_joints_rotation_axis(selected_joints)
    cmds.select(selected_joints, replace=True)

    logger.debug('Joints rotations axis zeroed successfully!')


def rotate_joint_local_rotation_axis(
        joint: Sequence[str], rotation: Sequence[float, float, float], include_children: bool = True):
    """
    Rotates the local rotation axis of given `joint` by given `rotation`.

    :param str joint: joint to rotate local rotation axis of.
    :param Sequence[float, float, float] rotation: XYZ rotationa in degrees.
    :param bool include_children: whether to include joints hierarchy.
    """

    cmds.rotate(rotation[0], rotation[1], rotation[2], f'{joint}.rotateAxis', objectSpace=True, forceOrderXYZ=True)
    if cmds.objectType(joint) == 'joint':
        cmds.joint(joint, edit=True, zeroScaleOrient=True)


def rotate_joints_local_rotation_axis(
        joints: Sequence[str], rotation: Sequence[float, float, float], include_children: bool = True):
    """
    Rotates the local rotation axis of given `joints` by given `rotation`.

    :param Sequence[str] joints: joints to rotate local rotation axis of.
    :param Sequence[float, float, float] rotation: XYZ rotationa in degrees.
    :param bool include_children: whether to include joints hierarchy.
    """

    for joint in joints:
        rotate_joint_local_rotation_axis(joint, rotation, include_children=include_children)


def rotate_selected_joints_local_rotation_axis(rotation: Sequence[float, float, float], include_children: bool = True):
    """
    Rotates the local rotation axis of current selected joints by given `rotation`.

    :param Sequence[float, float, float] rotation: XYZ rotationa in degrees.
    :param bool include_children: whether to include joints hierarchy.
    """

    selected_joints = cmds.ls(selection=True, exactType='joint', long=True)
    if not selected_joints:
        logger.warning('No joints found. Please select some joints.')
        return

    rotate_joints_local_rotation_axis(selected_joints, rotation, include_children=include_children)
