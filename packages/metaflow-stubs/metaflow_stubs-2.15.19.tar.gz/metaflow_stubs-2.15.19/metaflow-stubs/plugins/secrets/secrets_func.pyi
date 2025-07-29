######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.19                                                                                #
# Generated on 2025-07-10T01:18:40.902941                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.secrets.secrets_spec
    import typing

from ...exception import MetaflowException as MetaflowException
from .secrets_spec import SecretSpec as SecretSpec
from .utils import get_secrets_backend_provider as get_secrets_backend_provider

DEFAULT_SECRETS_ROLE: None

def get_secrets(sources: typing.List[typing.Union[str, typing.Dict[str, typing.Any]]] = [], role: typing.Optional[str] = None) -> typing.Dict[metaflow.plugins.secrets.secrets_spec.SecretSpec, typing.Dict[str, str]]:
    """
    Get secrets from sources
    
    Parameters
    ----------
    sources : List[Union[str, Dict[str, Any]]], default: []
        List of secret specs, defining how the secrets are to be retrieved
    role : str, optional
        Role to use for fetching secrets
    """
    ...

