import ccgeneral.texture.tx_manager as tx_manager
import cchoudini.utils.hou_utils as hou_utils


def open_tx_manager():
    """ Open the tx manager """
    hou_utils.launch_hou_win(tx_manager.TxManager)
