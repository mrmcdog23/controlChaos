""" Creating and managing a shot override parameter """
import re
import hou
import cchoudini.utils.create_parameters as create_parameters
import cccore.file_env.context as context
import cccore.utils.cc_logging as cc_logging


class CreateOverride(object):
    """ Create a shot parameter override """
    override_prefix = "shotoverride_"
    cmd = ('import cchoudini.utils.shot_override_parm as sop;'
           'sop.set_override_parm_value(kwargs["parm"])')
    
    def __init__(self, parm_data=None):
        # type: (dict) -> None
        """
        Args:
            parm_data: The source parameters data
        """
        self.parm_data = parm_data
        self.logger = cc_logging.cc_logger()
        self.ctx = context.Context()

    @property
    def data_values_dict(self):
        # type: () -> dict
        """
        Build a dictionary of the values of the source parameter

        Returns:
            data_values_dict: The source parameter values
        """
        template_data = self.source_parm.templateAsData()
        data_values_dict = dict()
        parm_to_find = ["type", "default_value", "min_value", "max_value"]
        for key, value in template_data.items():
            for parm_name in parm_to_find:
                parm_value = value.get(parm_name)
                if parm_value:
                    data_values_dict[parm_name] = parm_value
        return data_values_dict

    @property
    def source_parm_name(self):
        # type: () -> str
        """ Get the source parameter name """
        if self.parm_type == "float_vector3":
            template_name = self.source_parm.parmTemplate()
            source_parameter_label = template_name.name()
        else:
            source_parameter_label = self.source_parm.name()
        return source_parameter_label

    @property
    def source_parm(self):
        # type: () -> hou.Parm
        """ Source parameter that's been changed or needs override for """
        parms = self.parm_data.get("parms")
        if parms:
            return self.parm_data["parms"][0]
        else:
            return self.parm_data["parm"]
    
    @property
    def node(self):
        # type: () -> hou.Node
        """ The source node """
        return self.source_parm.node()

    @property
    def parm_type(self):
        # type: () -> str
        """ The parameter type changed """
        return self.data_values_dict["type"]

    def create_override_parameters(self):
        """
        Create the override parameter
        """
        # if the node changed is already an override node skip
        if self.source_parm_name.startswith(self.override_prefix):
            self.logger.critical("Can not create an override of an override")
            return

        # get the new parameter name and its label
        parm_label = self.ctx.full_shot_name
        parm_name = f"{self.override_prefix}{self.source_parm_name}_{parm_label}"

        # create the new parameter based on its type
        self.logger.info(f"Creating parameter name {parm_name} of type {self.parm_type}")
        if self.parm_type == "float":
            create_parameters.float_parm(
                self.node, parm_name, parm_label, self.source_parm_name, cmd=self.cmd)

        elif self.parm_type == "toggle":
            create_parameters.toggle_parm(
                self.node, parm_name, parm_label, self.source_parm_name, cmd=self.cmd)

        elif self.parm_type == "float_vector3":
            create_parameters.float_vector3_parm(
                self.node, parm_name, parm_label, self.source_parm_name, cmd=self.cmd)

        elif self.parm_type == "integer":
            min_value = self.data_values_dict.get("min_value")
            max_value = self.data_values_dict.get("max_value")
            create_parameters.int_parm(
                self.node,
                parm_name,
                parm_label,
                self.source_parm_name, 
                min_value=min_value,
                max_value=max_value,
                cmd=self.cmd
            )
        else:
            self.logger.critical(f"Parameter of type {self.parm_type} has not been created")
            return

        # set the default value of the new parameter
        default_value = self.data_values_dict.get("default_value")
        if default_value and self.node.parm(parm_name):
            self.node.parm(parm_name).set(default_value)

    def update_shot_parm(self, override_parm):
        """
        Set the source parameter from the override one
        """
        override_parm_name = override_parm.name()
        if not override_parm_name.startswith(self.override_prefix):
            return

        self.logger.info(f"Updating parameter: {override_parm_name}")
        # from the parameter get the shot name
        parm_template = override_parm.parmTemplate()
        shot_name = parm_template.label()

        # if it's not the current shot skip
        if shot_name != self.ctx.full_shot_name:
            return

        # from the override parameter extract the original parameter name
        re_groups = re.search(f"{self.override_prefix}(.*)_{shot_name}(.*)", override_parm_name)
        original_parm_name = re_groups.groups()[0]
        if not original_parm_name:
            return

        node = override_parm.node()
        if parm_template.numComponents() == 3:
            override_parm_name_strip = override_parm_name[:-1]
            for axis in ["x", "y", "z"]:
                dest_axis_parm_name = f"{original_parm_name}{axis}"
                override_axis_parm_name = f"{override_parm_name_strip}{axis}"

                source_value = node.parm(override_axis_parm_name).eval()
                node.parm(dest_axis_parm_name).set(source_value)
        else:
            source_value = node.parm(override_parm_name).eval()
            node.parm(original_parm_name).set(source_value)

    def remove_parm(self):
        """
        Remove the custom parameter
        """
        if not self.source_parm_name.startswith(self.override_prefix):
            return
        parm_template = self.source_parm.parmTemplate()
        self.node.removeSpareParmTuple(parm_template)


def create_override(parm_data):
    # type: (dict) -> None
    """
    Create the override parameter

    Args:
        parm_data: The source parameters data
    """
    CreateOverride(parm_data).create_override_parameters()


def set_override_parm_value(parm):
    # type: (hou.Parm) -> None
    """
    Set the override parameter

    Args:
        parm: The source parameter
    """
    CreateOverride().update_shot_parm(parm)


def remove_override_parm(parm_data):
    # type: (dict) -> None
    """
    Create the override parameter

    Args:
        parm_data: The source parameters data
    """
    CreateOverride(parm_data).remove_parm()
