""" Define classes of applications and tools to launch """
import os
import subprocess
import logging
import cccore.core_constants as core_constants


logging.basicConfig(level=logging.INFO)


class BaseEntity(object):
    name = str()

    def __init__(self):
        super(BaseEntity, self).__init__()

        # set launching variables
        self.cmd_list = list()
        self.python_paths = list()
        self.project_data = None
        self.project_root = None
        self.project_code = None
        self.display_name = None
        self.use_version = None
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
        os.environ["PROJECT_CODE"] = self.project_code
        os.environ["PROJECT_ROOT"] = self.project_root
        os.environ["APP_VERSION"] = self.use_version
        os.environ["APP_NAME"] = self.name

        # add core root to python paths list
        core_path = self.join_file_names(self.pipeline_root, "core", "python")
        self.python_paths.append(core_path)
        
        # add core root to python paths list
        core_path = self.join_file_names(core_path, "cccore", "pyside")
        self.python_paths.append(core_path)

        # add general root to python paths list
        general_path = self.join_file_names(self.pipeline_root, "general", "python")
        self.python_paths.append(general_path)

        # add ftrack root to python paths list
        ftrack_path = self.join_file_names(self.pipeline_root, "ftrack", "python")
        self.python_paths.append(ftrack_path)

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
        if self.use_version:
            return self.use_version
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
        #version_to_py = {"2026": "311_nopyside", "2024": "311_nopyside"}
        #return version_to_py[self.app_version]
        return "311_nopyside"

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
        startup_path = self.join_file_names(maya_python_path, "ccmaya", "startup")
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
    name = "unreal"

    def __init__(self):
        super().__init__()
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
        if not os.environ["USERNAME"] == "joele":
            self.cmd_list = [self.exe_path]
            return
        uproject_path = "C:/Users/joele/Documents/Unreal Projects/new_test/new_test.uproject"
        self.cmd_list = [self.exe_path, uproject_path]


class HoudiniApp(BaseApp):
    """
    Launching Houdini application
    """
    def __init__(self):
        super(HoudiniApp, self).__init__()
        self.name = "houdini"
        self.display_text = "Houdini"
        self.icon = "houdini.png"
        self.is_app = True

        # create list variables
        self.otls_paths = list()
        self.toolbars_path = list()
        self.houdini_icons = list()
        self.houdini_paths = list()
        self.houdini_menus = list()
        self.third_party_houdini_dir = str()

        self.hou_install = "/opt/Houdini"
        self.launch_path = "C:/Program Files/Side Effects Software/Houdini {version}/bin/houdini.exe"

    '''
    @property
    def python_version(self):
        # type: () -> str
        """
        Python version to use to add site packages
        """
        project_data = server_data.ProjectData()
        houdini_py_mappings = project_data.get("houdini_py_mappings")
        houdini_py_version = houdini_py_mappings[self.app_version]
        return str(houdini_py_version)
    '''

    def make_command_list(self):
        """
        Launch the houdini version
        """
        self.cmd_list = [self.exe_path]

    def set_environment(self):
        """
        Set the nuke environment variables
        """
        super(HoudiniApp, self).set_environment()
        self.set_houdini_core_variables()
        self.join_variables()

    @property
    def major_version(self):
        # type: () -> str
        """ Get the houdini major version e.g. 20"""
        return self.app_version.split(".")[0]

    @property
    def minor_version(self):
        # type: () -> str
        """ Get the houdini minor version e.g. 20.5 """
        num = self.app_version.split(".")
        return f"{num[0]}.{num[1]}"

    def set_houdini_core_variables(self):
        """
        Set the houdini core variables
        """
        # add menu variable
        os.environ["HOUDINI_NO_ENV_FILE"] = "1"

        # set the scripts path
        houdini_scripts_path = self.join_file_names(self.pipeline_root, "houdini", "python")
        self.python_paths.append(houdini_scripts_path)

        # add no8 custom menus. need to join or it errors
        pipeline_menu_path = self.join_file_names(self.pipeline_root, "houdini", "menu")
        self.houdini_menus.append(pipeline_menu_path)

        # houdini paths
        houdini_root_path = self.join_file_names(self.pipeline_root, "houdini")
        self.houdini_paths.append(houdini_root_path)

        # add toolbars
        no8_hou_shared_toolbar = self.join_file_names(houdini_root_path, "shelves")
        self.toolbars_path.append(no8_hou_shared_toolbar)

        # set the icons variable
        houdini_icons_path = self.join_file_names(no8_hou_shared_toolbar, "icons")
        os.environ["HOUDINI_ICONS"] = houdini_icons_path


    @staticmethod
    def add_directory_to_list(directory_path, list_variable):
        # type: (str, list[str]) -> None
        """
        Add the directory to the variable list

        Args:
            directory_path: Path of the directory to add
            list_variable: The variable list to add to
        """
        if os.path.exists(directory_path):
            logging.info(f"Found directory: {directory_path}")
            list_variable.append(directory_path)
        else:
            logging.warning(f"Directory not found: {directory_path}")

    def join_variables(self):
        """
        Join all environment variables
        """
        self.join_env_variables("HOUDINI_TOOLBAR_PATH", self.toolbars_path)
        self.join_env_variables("HOUDINI_OTLSCAN_PATH", self.otls_paths)
        self.join_env_variables("HOUDINI_PATH", self.houdini_paths)
        self.join_env_variables("HOUDINI_MENU_PATH", self.houdini_menus)

    @property
    def exe_path(self):
        # type: () -> str
        """ Work out the unreal exe path """
        exe_path = self.launch_path.format(version=self.app_version)
        return exe_path


class NukeApp(BaseApp):
    """
    Launching Houdini application
    """
    name = "nuke"

    def __init__(self):
        super().__init__()




class SlateMakerTool(BaseTool):
    name = "slate_maker_tool"

    def __init__(self):
        super().__init__()
        self.display_text = "Slate Maker"
        self.icon = "slate_maker.png"
        self.launch_path = "{0}/standalone/python/slate_maker/slate_maker_ui.py"


class ProjectCreatorTool(BaseTool):
    name = "project_creator"

    def __init__(self):
        super().__init__()
        self.display_text = "Project Creator"
        self.icon = "project_creator.png"
        self.launch_path = "{0}/standalone/python/creators/project_creator.py"


class ShotCreatorTool(BaseTool):
    name = "shot_creator_tool"

    def __init__(self):
        super(ShotCreatorTool, self).__init__()
        self.display_text = "Shot Creator"
        self.icon = "shot_creator.png"
        self.launch_path = "{0}/standalone/python/creators/shot_creator.py"


class AssetCreatorTool(BaseTool):
    name = "asset_creator_tool"

    def __init__(self):
        super(AssetCreatorTool, self).__init__()
        self.display_text = "Asset Creator"
        self.icon = "asset.png"
        self.launch_path = "{0}/standalone/python/creators/asset_creator.py"


class MediaPublisherTool(BaseTool):
    name = "media_publisher_tool"

    def __init__(self):
        super(MediaPublisherTool, self).__init__()
        self.display_text = "Media Publisher"
        self.icon = "media_publisher.png"
        self.launch_path = "{0}/standalone/python/uploader/media_publisher_wizard.py"


APPLICATIONS = [
    MayaApp,
    UnrealApp,
    HoudiniApp
]
TOOLS = [
    SlateMakerTool,
    ProjectCreatorTool,
    ShotCreatorTool,
    AssetCreatorTool,
    MediaPublisherTool
]
