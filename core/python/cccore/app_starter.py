""" Define classes of applications and tools to launch """
import os
import subprocess
import logging
import cccore.core_constants as core_constants


logging.basicConfig(level=logging.INFO)


class BaseEntity(object):
    app_versions = list()
    name = str()

    def __init__(self):
        super(BaseEntity, self).__init__()

        # set launching variables
        self.cmd_list = list()
        self.python_paths = list()
        self.project_data = None
        self.display_name = None
        self.is_app = None

    @property
    def python_version(self):
        # type: () -> str
        """ Python version to use to add site packages """
        return "311"

    @property
    def pipeline_root(self):
        # type: () -> str
        """ Python version to use to add site packages """
        return os.environ["PIPELINE_ROOT"].replace("\\", "/")

    @property
    def root_dir(self):
        # type: () -> str
        """ Python version to use to add site packages """
        return os.environ["ROOT_DIR"].replace("\\", "/")

    @staticmethod
    def join_file_names(*folder_list):
        # type: (Any) -> str
        """
        Join folder names and create a path from

        Args:
            folder_list: Names of files to join

        Returns:
            folder_path_clean: the joined path of names clean
        """
        if isinstance(folder_list[0], list):
            folder_path = "/".join(folder_list[0])
        else:
            folder_path = os.path.join(*folder_list)
        folder_path_clean = folder_path.replace("\\", "/")
        return folder_path_clean

    def set_site_packages(self):
        """
        Add the site packages to the python path
        """
        site_packages_fmt = "{0}virtual_env/python{1}/Lib/site-packages"
        site_packages = site_packages_fmt.format(self.root_dir, self.python_version)

        logging.info(f"Adding {site_packages}")
        self.python_paths.append(site_packages)

    @property
    def exe_path(self):
        """ The application exe path """
        return None

    def set_environment(self):
        """
        Set core and project environment
        """
        self.set_core_environment()
        self.set_site_packages()
        self.set_app_environment()

    @staticmethod
    def join_env_variables(env_name, paths):
        # type: (str, list[str]) -> None
        """
        Join a list of paths and setit as an environment variable

        Args:
            env_name: Name of the environment variable
            paths: List of environment paths
        """
        for path in paths:
            logging.info(f"Adding {env_name}: {path}")
        os.environ[env_name] = ";".join(paths) + f";&"

    def set_core_environment(self):
        """
        Set the base environment variables
        """
        logging.info("Setting core variables...")

        # add core root to python paths list
        core_path = self.join_file_names(self.pipeline_root, "core", "python")
        self.python_paths.append(core_path)
        
        # add core root to python paths list
        core_path = self.join_file_names(core_path, "cccore", "pyside")
        self.python_paths.append(core_path)

        # add general root to python paths list
        general_path = self.join_file_names(self.pipeline_root, "general", "python")
        self.python_paths.append(general_path)

    def set_python_paths(self):
        """
        Join the python paths to a string and
        add to the PYTHONPATH variable
        """
        for python_path in self.python_paths:
            logging.info("Adding python path: {0}".format(python_path))
        os.environ["PYTHONPATH"] = ";".join(self.python_paths)

    def set_app_environment(self):
        """ Set the application environment """
        pass

    def make_command_list(self):
        # type: () -> list[str]
        """
        Make the command to run to launch
        the tool or application
        """
        raise NotImplemented

    def start(self):
        """
        Execute the command list in a subprocess
        """
        logging.info(f"Running...{self.cmd_list}")
        subprocess.Popen(self.cmd_list)


class BaseTool(BaseEntity):
    def __init__(self):
        super(BaseTool, self).__init__()
        self.is_app = False
        self.launch_path = str()
        self.restricted = True

    def make_command_list(self):
        """
        Launch the tool via python
        """
        py_path = self.launch_path.format(self.pipeline_root)
        self.cmd_list = [core_constants.PYTHON_EXE, py_path]


class BaseApp(BaseEntity):
    def __init__(self):
        super(BaseApp, self).__init__()
        self.is_app = True

    @property
    def app_version(self):
        # type: () -> str
        """
        The version of the application to use
        """
        app_version = os.environ.get("APP_VERSION")
        if not app_version:
            raise Exception("Application version not set")
        return app_version

    def make_command_list(self):
        """
        Launch the maya version
        """
        self.cmd_list = [self.exe_path]

    @property
    def exe_path(self):
        # type: () -> str
        """ Work out the mayapy exe path """
        return self.launch_path.format(self.app_version)


class MayaApp(BaseApp):
    app_versions = ["2026", "2024"]
    name = "maya"

    def __init__(self):
        super().__init__()

        # launcher variables
        self.display_text = "Maya"
        self.icon = "maya.png"
        self.launch_path = "C:/Program Files/Autodesk/Maya{0}/bin/maya.exe"

    @property
    def python_version(self):
        # type: () -> str
        """ Python version to use to add site packages """
        version_to_py = {"2026": "311_nopyside", "2024": "311_nopyside"}
        return version_to_py[self.app_version]

    def set_app_environment(self):
        """
        Add the maya core environment variables
        """
        # add maya site package to first path as it will break if not
        maya_site_pkg_format = "C:/Program Files/Autodesk/Maya{0}/Python/Lib/site-packages"
        maya_site_pkg = maya_site_pkg_format.format(self.app_version)
        self.python_paths.insert(0, maya_site_pkg)

        # set the scripts path
        # add core root to python paths list
        maya_python_path = self.join_file_names(self.pipeline_root, "maya", "python")
        self.python_paths.append(maya_python_path)

        # add startup script
        startup_path = self.join_file_names(maya_python_path, "ddvmaya", "startup")
        self.python_paths.append(startup_path)

        # add shelf paths
        shelves_path = self.join_file_names(self.pipeline_root, "maya", "shelves")
        os.environ["MAYA_SHELF_PATH"] = shelves_path

        # add shelf icons
        shelf_icons_path = self.join_file_names(self.pipeline_root, "maya", "shelves", "icons")
        os.environ["XBMLANGPATH"] = shelf_icons_path

        maya_plugins_path = self.join_file_names(self.pipeline_root, "maya", "plugins")
        os.environ["MAYA_PLUG_IN_PATH"] = maya_plugins_path


class MayaPyApp(MayaApp):
    def __init__(self):
        super(MayaPyApp, self).__init__()
        self.launch_path = "C:/Program Files/Autodesk/Maya{0}/bin/mayapy.exe"

    def make_command_list(self):
        """
        Launch the maya version
        """
        # set the scripts path
        py_path = self.launch_path.format(self.pipeline_root)
        self.cmd_list = [core_constants.PYTHON_EXE, py_path]


class UnrealApp(BaseApp):
    """
    Launching Unreal application
    """
    app_versions = ["5.6"]
    name = "unreal"

    def __init__(self):
        super().__init__()
        self.name = "unreal"
        self.display_text = "Unreal"
        self.icon = "unreal.png"
        self.launch_path = "C:/Program Files/Epic Games/UE_{version}/Engine/Binaries/Win64/UnrealEditor.exe"

    @property
    def python_version(self):
        # type: () -> str
        """ Python version to use to add site packages """
        return "311"

    def set_environment(self):
        """
        Set the nuke environment variables
        """
        super().set_environment()
        self.set_python_paths()
        os.environ["UE_PYTHONPATH"] = os.environ["PYTHONPATH"]
        self.set_unreal_core_variables()

    def set_unreal_core_variables(self):
        """
        Set the core unreal python paths
        """
        unreal_paths = [f"{self.pipeline_root}/unreal/python",
                        f"{self.pipeline_root}/unreal/python/ccunreal/startup"
                        ]
        unreal_paths_str = ";".join(unreal_paths)
        os.environ["UE_PYTHONPATH"] += ";" + unreal_paths_str

    @property
    def exe_path(self):
        # type: () -> str
        """ Work out the unreal exe path """
        exe_path = self.launch_path.format(version=self.app_version)
        return exe_path

    def make_command_list(self):
        """
        Launch the unreal project
        """
        self.cmd_list = [self.exe_path]


class SlateMakerTool(BaseTool):
    name = "slate_maker_tool"

    def __init__(self):
        super().__init__()
        self.display_text = "Slate Maker"
        self.icon = "slate_maker.png"
        self.launch_path = "{0}/standalone/python/slate_maker/slate_maker_ui.py"


APPLICATIONS = [
    MayaApp,
    UnrealApp
]
TOOLS = [
    SlateMakerTool
]
