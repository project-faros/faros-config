"""Faros Configuration Models - Bastion.

This module contains the configuration models for the bastion section. This
includes settings specific to the bastion host itself.
"""

from pydantic import Field

from .common import FarosBaseModel


class BastionConfig(FarosBaseModel):
    """Configuration specific to the bastion host."""

    become_pass: str = Field(
        alias="Sudo Password",
        description=("The password for the sudo user executing Faros on the "
                     "bastion.")
    )
