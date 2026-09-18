""" Create the panel to set the context """
import hou
from typing import Optional
from CCPySide import QtWidgets
import cccore.data.server_data as server_data
import cccore.file_env.ctx_constants as ctx_constants


PROJECT_MANAGER_PANEL = "houdini/python_panels/project_manager.pypanel"
PERFORMANCE_MONITOR_PANEL = "PerformanceMonitor"
SHOT_SWITCHER_WIDGET = "shot_switcher_widget"


class CreateCCHoudiniPanel(object):
    """
    Create the Control Chaos Houdini panel
    """
    def __init__(self):
        self.pypan = None
        self.installed_interfaces = list()
        self.project_data = server_data.ProjectData()

    def make_panel(self):
        """
        Run create panel functions
        """
        self.install_panel()
        self.get_installed_interfaces()
        self.load_cc_panel()

    def install_panel(self):
        """
        Install the cc project panel into the houdini panels
        """
        project_panel_path = self.project_data.get_relative_path(PROJECT_MANAGER_PANEL)
        hou.pypanel.installFile(project_panel_path)
        self.pypan = hou.pypanel.interfacesInFile(project_panel_path)[0]

    def get_installed_interfaces(self):
        # type: () -> None
        """
        Populate the list of interfaces

        Returns:
            List of install houdini interfaces
        """
        interfaces = hou.pypanel.menuInterfaces()
        for interface in interfaces:
            hou.pypanel.setMenuInterfaces((interface,))

            if interface == '__separator__':
                continue

            if interface not in self.installed_interfaces:
                self.installed_interfaces.append(interface)

        self.installed_interfaces.append(self.pypan.name())

    @property
    def add_to_panel(self):
        """
        Find the panel index to add to. If the
        tab name is in the list use it
        """
        name_to_panel_dict = dict()
        all_panels = hou.ui.curDesktop().panes()
        for panel in all_panels:
            for tab in panel.tabs():
                tab_name = tab.type().name()
                name_to_panel_dict[tab_name] = panel

        # use the shot switcher panel first. If it is
        # not found then use the performance panel
        use_panel = name_to_panel_dict.get(SHOT_SWITCHER_WIDGET)
        if not use_panel:
            use_panel = name_to_panel_dict.get(PERFORMANCE_MONITOR_PANEL)

        # if still not found use the first one
        if not use_panel:
            use_panel = list(name_to_panel_dict.values())[0]
        return use_panel

    def load_cc_panel(self):
        """
        Load the cc panel
        """
        hou.pypanel.setMenuInterfaces(tuple(self.installed_interfaces))
        python_panel = self.add_to_panel.createTab(hou.paneTabType.PythonPanel)
        python_panel.setIsCurrentTab()
        python_panel.showToolbar(0)
        python_panel.setActiveInterface(self.pypan)


def make_context_panel():
    """
    Create the cc project panel for houdini
    """
    import hdefereval
    create_cc_panel_inst = CreateCCHoudiniPanel()
    hdefereval.executeDeferred(lambda: create_cc_panel_inst.make_panel())


def get_ctx_panel():
    # type: () -> Optional[QtWidgets.QWidget]
    """
    Find the Control Chaos Panel. Create it if it doesn't exist

    Returns:
        ctx_panel: THe houdini cc panel
    """
    # check houdini has opened
    if not hou.isUIAvailable():
        return None

    hou_window = hou.qt.mainWindow()
    if not hou_window:
        return None

    # get the context panel and create if not
    ctx_panel = hou_window.findChild(
        QtWidgets.QWidget,
        ctx_constants.CONTEXT_PANEL
    )
    if not ctx_panel:
        make_context_panel()

    # get the context panel
    ctx_panel = hou_window.findChild(
        QtWidgets.QWidget,
        ctx_constants.CONTEXT_PANEL
    )
    return ctx_panel
