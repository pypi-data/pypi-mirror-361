######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.20                                                                                #
# Generated on 2025-07-10T18:07:14.413261                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.monitor


class DebugMonitor(metaflow.monitor.NullMonitor, metaclass=type):
    @classmethod
    def get_worker(cls):
        ...
    ...

class DebugMonitorSidecar(object, metaclass=type):
    def __init__(self):
        ...
    def process_message(self, msg):
        ...
    ...

