######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.20                                                                                #
# Generated on 2025-07-10T18:07:14.442423                                                            #
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

