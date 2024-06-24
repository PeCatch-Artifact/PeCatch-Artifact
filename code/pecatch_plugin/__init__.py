from pecatch_plugin.detectors.redundantsload import RedundantSLoad
from pecatch_plugin.detectors.bool import Bool
from pecatch_plugin.detectors.unchecked import Unchecked
from pecatch_plugin.detectors.memory2calldata import Memory2Calldata
from pecatch_plugin.detectors.loopinvariant import LoopInvariant
from pecatch_plugin.detectors.allocinloop import AllocInLoop

def make_plugin():
    plugin_detectors = [RedundantSLoad, Bool, Unchecked, Memory2Calldata, LoopInvariant, AllocInLoop]
    plugin_printers = []

    return plugin_detectors, plugin_printers