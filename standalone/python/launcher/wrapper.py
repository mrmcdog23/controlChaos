import sys
import inspect
import cccore.app_starter as app_starter


def launch_app_or_tool(app_name, display_text):
    """
    Launch the application or tool

    Args:
        app_name (str): Name of the tool or app
        project_name (str): Name of the project to start under
        pipeline_type (str): Type of pipeline ("stable", "beta", "branch"...)
        pipeline_root (str): Directory of the pipeline to start under
        display_name (str): Text to be displayed in applications
    """
    # find the launch app
    launch_app = None
    for name, appclass in inspect.getmembers(app_starter):
        if app_name == name:
            launch_app = appclass()
            break

    #launch_app.pipeline_root = pipeline_root
    launch_app.display_text = display_text

    # set the python environment
    launch_app.set_environment()
    launch_app.set_python_paths()
    launch_app.make_command_list()
    launch_app.start()


if __name__ == "__main__":
    app_name = sys.argv[1]
    display_text = sys.argv[2]
    launch_app_or_tool(app_name, display_text)
