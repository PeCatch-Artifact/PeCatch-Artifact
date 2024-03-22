from plugin.detectors.LoopOverflow import LoopOverflow
from plugin.detectors.UnboundedMassOp import UnboundedMassOp
from plugin.detectors.WalletGriefing import WalletGriefing


def make_plugin():
    plugin_detectors = [LoopOverflow, UnboundedMassOp, WalletGriefing]
    plugin_printers = []

    return plugin_detectors, plugin_printers