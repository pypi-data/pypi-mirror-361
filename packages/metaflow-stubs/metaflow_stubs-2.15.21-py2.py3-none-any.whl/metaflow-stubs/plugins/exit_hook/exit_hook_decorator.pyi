######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.21                                                                                #
# Generated on 2025-07-11T15:58:13.065515                                                            #
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

