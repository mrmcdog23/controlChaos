""" No8Wedger node management and functions """
import hou
from typing import Optional, Any
import cccore.utils.cc_logging as cc_logging


WEDGER_PARM_SUFFIXES = [
    "_single_int",
    "_vector2_int",
    "_vector3_int",
    "_single_float",
    "_vector2_float",
    "_vector3_float"
]


class No8WedgerNode(object):
    """
    Class for management of the ccwedger node
    """
    def __init__(self, cc_wedger_node):
        # type: (hou.Node) -> None
        """
        Args:
            cc_wedger_node: Node to manage
        """
        self.logger = cc_logging.cc_logger()
        self.cc_wedger_node = cc_wedger_node

    def on_create(self):
        """ When node is created set the colour """
        self.cc_wedger_node.setColor(hou.Color(0.302, 0.525, 0.114))

    @property
    def num_of_wedges(self):
        # type: () -> int
        """ Get the number of wedges set in the slider """
        return self.cc_wedger_node.parm("number_of_wedges").eval()

    @property
    def parameter_name(self):
        # type: () -> str
        """ Name of the given parameter """
        return self.cc_wedger_node.parm("parameter_name").evalAsString()

    @property
    def input_node(self):
        # type: () -> Optional[hou.Node]
        """
        Get the input node of the wedger node
        """
        input_nodes = self.cc_wedger_node.inputs()
        if not input_nodes:
            return
        input_node = [node for node in input_nodes][0]
        return input_node

    @property
    def parms_names_to_submit(self):
        # type: () -> list[str]
        """
        Get a list of the parameter names
        """
        parm_names = list()
        suffix = self.cc_wedger_node.parm("suffix").eval()
        for index in range(self.num_of_wedges):
            parm_name = f"wedger{(index + 1)}{suffix}"
            parm_names.append(parm_name)
        return parm_names

    def get_input_suffix(self):
        # type: () -> Optional[str]
        """
        Work out the input suffix of the parameter
        """
        parameter_name = self.parameter_name
        input_node = self.input_node
        if not input_node:
            return None

        # work out the parameter type
        parm = input_node.parm(parameter_name)
        parm_type = str()

        # work out the parameter type
        if parm:
            parm_type = "_single"

        elif input_node.parm(f"{parameter_name}z"):
            parm_type = "_vector3"
            parm = input_node.parm(f"{parameter_name}z")

        elif input_node.parm(f"{parameter_name}y"):
            parm_type = "_vector2"
            parm = input_node.parm(f"{parameter_name}y")

        if not parm:
            return None

        # work out if its an int or float
        value = parm.eval()
        if isinstance(value, float):
            parm_type += "_float"
        elif isinstance(value, int):
            parm_type += "_int"
        return parm_type

    def show_relevant_parms(self):
        """
        Set the suffix of the parameter
        """
        input_suffix = self.get_input_suffix()
        if not input_suffix:
            self.cc_wedger_node.parm("suffix").set("none")
            return
        self.cc_wedger_node.parm("suffix").set(input_suffix)

    def set_node_to_wedge(self, parm_name):
        # type: (str) -> Any
        """
        From the name of a wedger parameter get its
        value and set it on the input node parameter

        Args:
            parm_name: Name of the wedger parameter

        Returns:
            value: The value of the parameter
        """

        suffix = self.get_input_suffix()

        # if it is a vector then work out the individual
        # parameters and get the value on the wedger node
        # and set on the input node
        if "_vector" in suffix:
            if "_vector3" in suffix:
                parm_list = ["x", "y", "z"]
            else:
                parm_list = ["x", "y"]

            value_str = str()
            for parm in parm_list:
                full_parm_name = f"{parm_name}{parm}"
                parm_value = self.cc_wedger_node.parm(full_parm_name).eval()
                use_vector_parameter_name = f"{self.parameter_name}{parm}"
                self.input_node.parm(use_vector_parameter_name).set(parm_value)
                value_str += f"{parm_value} "
        else:
            parm_value = self.cc_wedger_node.parm(parm_name).eval()
            self.input_node.parm(self.parameter_name).set(parm_value)
            value_str = str(parm_value)
        return value_str

    def set_input_value(self, value_to_set):
        # type: (Any) -> None
        """
        Set the wedger value

        Args:
            value_to_set: Either a value or list of values to set
        """
        self.logger.info(f"Value to set: {value_to_set}")
        if isinstance(value_to_set, list):
            vector_list = ["x", "y", "z"]
            vector_to_value = dict(zip(vector_list, value_to_set))
            for vector, wedge_value in vector_to_value.items():
                use_parameter_name = f"{self.parameter_name}{vector}"
                self.logger.info(f"Setting {use_parameter_name} to set: {wedge_value}")
                self.input_node.parm(use_parameter_name).set(wedge_value)
        else:
            self.input_node.parm(self.parameter_name).set(value_to_set)

    def reset_values(self):
        """
        Reset the wedger node values
        """
        for parm in self.cc_wedger_node.allParms():
            if parm.name().startswith("wedger"):
                parm.revertToDefaults()
