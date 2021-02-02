"""Faros Configuration UI - Form.

This module contains the WTForms definitions for the models.
"""
import enum
from flask_wtf import FlaskForm
import ipaddress
from typing import Tuple
from wtforms import (
    Field,
    FieldList,
    FormField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    StringField,
    TextAreaField,
    validators,
    widgets
)


# TODO: Add validators that use pydantic checking and produce verbose errors on
# the forms.

def double_str(item: str) -> Tuple[str, str]:
    """Return the provided string as a tuple containing itself twice."""
    return (item, item,)


class MultiCheckboxField(SelectMultipleField):
    """A multiple-select field with checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


def should_be_string(field=None) -> bool:
    """Determine if a pydantic Field should be represented by a string."""
    if field.type_ == str:
        # It's a simple string field
        return True
    if getattr(field.type_, '__args__') is not None:
        # It's a Union
        if ipaddress.IPv4Address in field.type_.__args__:
            # It's a union of IP addresses
            return True
        if ipaddress.IPv4Network in field.type_.__args__:
            # It's a union of IP networks
            return True
    # It's not a string-type field
    return False


def should_be_secret(field=None) -> bool:
    """Determine if a pydantic string field should be obscured."""
    alias = field.alias.lower()
    if 'password' in alias or 'secret' in alias:
        return True
    return False


def pydantic_field(field=None,
                   depth: int = 0,
                   parents: str = '') -> Tuple[str, Field]:
    """Return a WTForms Field of the appropriate type for the model field."""
    # Keep form field names unique through_nesting
    if parents != '':
        field_name = parents + f'_{field.name}'
    else:
        field_name = field.name
    # Always validate with pydantic
    field_validators = [field.validate]
    # If it's not marked as Optional in model, then make it required
    if field.required:
        field_validators.append(validators.required())
    # Build base positional args w/ friendly name and validator
    args = (field.alias, field_validators)
    # Build base keyword args w/ default and description
    kwargs = {
        "default": field.default,
        "description": field.field_info.description
    }

    if field.is_complex() and field.type_ == field.outer_type_:
        # This is a nested model
        # we need to recurse via field.type_.__fields__, and return a FlaskForm
        raise NotImplementedError
    elif field.is_complex():
        # This is a complex type like List[str]
        if field.type_ == str:
            # This list of strings should just have defaults set for choices
            return (field_name, MultiCheckboxField(
                *args,
                choices=[(v, v) for v in field.default],
                **kwargs
            ))
        elif field.type_.__class__ == enum.EnumMeta:
            # This list of Enums has set, hard-coded checkboxes
            return (field_name, MultiCheckboxField(
                *args,
                choices=[(v, v) for v in field.type_.list()],
                **kwargs
            ))
        elif getattr(field.type_, '__args__') is not None:
            # This is a list of IPAddress/IPNetwork unions
            return (field_name, FieldList(StringField(*args, **kwargs)))
    else:
        if should_be_string(field):
            if should_be_secret(field):
                # This is a secret or password
                return (field_name, PasswordField(*args, **kwargs))
            # This is a simple string field
            # TODO: Figure out how to identify TextArea fields
            return (field_name, StringField(*args, **kwargs))
        elif field.type_.__class__ == enum.EnumMeta:
            # This is a single-entry enum
            return (field_name, SelectField(
                *args,
                choices=[(v, v) for v in field.type_.items()]
                **kwargs
            )
    raise RuntimeError(f'Unable to classify field, {field_name}')


class ConfigForm(FlaskForm):
    """Faros Configuration Form."""

    def __init__(self, *args, **kwargs) -> None:
        """Dynamically build form fields."""
        for section in FarosConfig.__fields__:
            # Pull the Pydantic data for the subsection
            subsection = FarosConfig.__fields__[section]
            # Generate a form for the subsection
            subform = FormField(pydantic_field(subsection),
                                description=subsection.field_info.description)
            setattr(self, section, subform)

        self.submit = SubmitField('Submit')
        super().__init__(*args, **kwargs)
