from __future__ import annotations

import maya.cmds as cmds

from tp.maya.cmds.nodes import attributes


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
