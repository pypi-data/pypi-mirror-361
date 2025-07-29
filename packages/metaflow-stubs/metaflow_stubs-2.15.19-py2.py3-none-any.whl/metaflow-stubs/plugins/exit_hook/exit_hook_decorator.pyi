######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.19                                                                                #
# Generated on 2025-07-10T01:18:40.906827                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

from ...exception import MetaflowException as MetaflowException

class ExitHookDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...

