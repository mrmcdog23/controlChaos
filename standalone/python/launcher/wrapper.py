import sys
import inspect
import cccore.app_starter as app_starter


def launch_app_or_tool(app_name, project_code, project_root, use_version):
    # type: (str, str, str) -> None
    """
    Launch the application or tool

    Args:
        app_name: Name of the tool or app
        project_name: Name of the project to start under
        pipeline_root: Directory of the pipeline to start under
        use_version: Version of the app
    """
    # find the launch app
    launch_app = None
    for name, appclass in inspect.getmembers(app_starter):
        if app_name == name:
            launch_app = appclass()
            break

    #launch_app.pipeline_root = pipeline_root
    launch_app.project_code = project_code
    launch_app.project_root = project_root
    launch_app.use_version = use_version

    # set the python environment
    launch_app.set_environment()
    launch_app.set_python_paths()
    launch_app.make_command_list()
    launch_app.start()


if __name__ == "__main__":
    app_name = sys.argv[1]
    project_code = sys.argv[2]
    project_root = sys.argv[3]
    use_version = sys.argv[4]
    launch_app_or_tool(app_name, project_code, project_root, use_version)
