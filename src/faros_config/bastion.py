"""Faros Configuration Models - Bastion.

This module contains the configuration models for the bastion section. This
includes settings specific to the bastion host itself.
"""

from pydantic import BaseModel, Field


class BastionConfig(BaseModel):
    """Configuration specific to the bastion host."""

    become_pass: str = Field(
        alias="Sudo Password",
        description=("The password for the sudo user executing Faros on the "
                     "bastion.")
    )

    class Config:
        """Configuration class for Pydantic models."""

        allow_population_by_field_name = True
