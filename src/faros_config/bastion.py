"""Faros Configuration Models - Bastion.

This module contains the configuration models for the bastion section. This
includes settings specific to the bastion host itself.
"""

from pydantic import BaseModel


class BastionConfig(BaseModel):
    """The Bastion config section model."""

    become_pass: str
