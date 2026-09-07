import cccore.file_env.context as context
import ccmaya.utils.maya_utils as maya_utils
from ccmaya.wizard.asset_publish_wizard import AssetWizard
from ccmaya.wizard.shot_export_wizard import ShotExportWizard


def main():
    """
    Launch the asset publish wizard
    """
    ctx = context.Context()
    if ctx.is_asset:
        use_wizard_cls = AssetWizard
    else:
        use_wizard_cls = ShotExportWizard
    message = use_wizard_cls.preflight_checks()
    if not message:
        return
    maya_utils.launch_wizard(use_wizard_cls)
