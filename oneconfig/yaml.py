"""Supplies methods used to load and save the YAML based configurations."""

from typing import Any, Union
import yaml
import re
from .formatter import Formatter  # format awesome stuff


# Extension to an existing argument -----------------------------------------------------------------------

class ExtendedArgument(object):
    """An Extension to an existing argument."""
    # TODO: Add usage examples and tests
    formatter = Formatter(dot_item_access=True)  # use a more powerfull formatter

    def __init__(self, value_pattern):
        """Create an extended property which uses other properties.

        Arguments:
            value_pattern:  the new value for the option
            format:         use format on strings to interpolate old properties

        """
        self.value_pattern = value_pattern

    def __repr__(self):
        """Represent as a string."""
        return f"{self.__class__.__name__}('{self.value_pattern}')"

    def __str__(self):
        """Return the calculated value."""
        return self.__get__()

    def __get__(self, instance=None, cls=None, root=None) -> str:
        """Get the value for this."""
        if root is not None:
            substitutions = root
        elif instance is not None:
            substitutions = instance
        else:
            substitutions = {}

        try:
            return self.formatter.format(self.value_pattern, **substitutions)
        except (KeyError, IndexError) as e:
            raise KeyError(f'The value pattern "{self.value_pattern}" could not be resolved')

    def __set__(self, instance, value: str) -> None:
        """Set the value for this."""
        self.value_pattern = value


# Decorators ----------------------------------------------------------------------------------------------------------

def auto_attach_yaml_constructors(cls):
    """Adds all functions starting with 'construct_' to the Loader.

    To achieve this the docstring must start with ``classname``,
    where ``classname`` is the name of the class you want to use.
    """
    for attr in dir(cls):
        if attr.startswith('construct_'):
            method = getattr(cls, attr)
            doc = str(method.__doc__)
            matches = re.match(r'''^['"](![A-Z_][A-Z_0-9\.]*)['"] ''', doc, re.IGNORECASE)
            if matches:
                cls.add_constructor(matches[1], method)
    return cls

def auto_attach_yaml_representers(cls):
    """Adds all functions starting with 'represent_' to the Dumper.

    To achieve this the typehint for the ``data`` argument must be the type you want to represent.
    """
    for attr in dir(cls):
        if attr.startswith('represent_'):
            method = getattr(cls, attr)
            doc = str(method.__doc__)

            try:
                annotation = method.__annotations__['data']
            except KeyError:
                pass
            else:
                cls.add_representer(annotation, method)

    return cls


# Loader and Dumper ---------------------------------------------------------------------------------------------------

@auto_attach_yaml_constructors
class ConfigYamlLoader(yaml.SafeLoader):
    """A config loader for all Deep8 projects."""

    def construct_pd_timestamp(self, node) -> pd.Timestamp:
        """"!Timestamp" constructs a pandas Timestamp from the string."""
        string_repr = self.construct_scalar(node)
        return pd.Timestamp(string_repr)

    def construct_pd_timedelta(self, node) -> pd.Timedelta:
        """"!Timedelta" constructs a pandas Timedelta from the string."""
        string_repr = self.construct_scalar(node)
        return pd.Timedelta(string_repr)

    def construct_extended_argument(self, node) -> ExtendedArgument:
        """"!r" constructs an `ExtendedArgument` instance."""
        string_repr = self.construct_scalar(node)
        return ExtendedArgument(string_repr)

@auto_attach_yaml_representers
class ConfigYamlDumper(yaml.SafeDumper):

    def represent_pd_timestamp(self, data: pd.Timestamp):
        """Turn timestamp into representation."""
        return self.represent_scalar('!Timestamp', str(data))

    def represent_pd_timedelta(self, data: pd.Timedelta):
        """Turn time delta into representation."""
        return self.represent_scalar('!Timedelta', str(data))


# Configuration class -------------------------------------------------------------------------------------------------

class Configuration(dict):
    """Configuration object.

    To access attributes you can use square brackets or call the object with a json-path.
    """

    def __init__(self, *args, **kwargs):
        if 'source_filename' in kwargs:
            self.source_filename =  kwargs['source_filename']
        else:
            self.source_filename = None
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({super().__repr__()})'

    def resolve_extended_arguments(self, data: Any):
        if isinstance(data, ExtendedArgument):
            return data.__get__(root=self)
        elif isinstance(data, dict):
            for key, node in data.items():
                data[key] = self.resolve_extended_arguments(node)
        elif isinstance(data, list):
            for i, node in enumerate(data):
                data[i] = self.resolve_extended_arguments(node)
        return data  # return the result

    @classmethod
    def load_from_yaml(cls, filename: str) -> 'Configuration':
        with open(filename, 'r', encoding='utf8') as f:
            return cls.from_yaml(input_stream=f, source_filename=filename)

    @classmethod
    def from_yaml(cls, input_stream, source_filename=None) -> 'Configuration':
        config = Configuration(yaml.load(input_stream, Loader=ConfigYamlLoader), source_filename=source_filename)
        return config.resolve_extended_arguments(config)

    def save_as_yaml(self, filename: str) -> None:
        with open(filename, 'w') as f:
            self.as_yaml(output_stream=f)  # return value is ignored

    def as_yaml(self, output_stream=None) -> str:
        return yaml.dump(self, output_stream, default_flow_style=False, Dumper=ConfigYamlDumper)

    def __call__(self, path: str, default: str = NotImplemented):
        """Get a node in the config tree by it’s (json) path."""
        node = self
        for match in re.findall(r'([A-Z_][A-Z_0-9]*)|\[(-?[0-9]+)\][.|$]', path, re.IGNORECASE):
            # print(path, match[1], match[2])
            try:
                node = node[match[0] or int(match[1])]
            except (KeyError, IndexError):
                if default is NotImplemented:  raise ValueError(f'"{path}" not found in the config')
                else:                          return default
        return node

    def set(self, path: str, value) -> None:
        """Set a node in the config tree to a value."""
        node = self
        matches = re.findall(r'([A-Z_][A-Z_0-9]*)|\[(-?[0-9]+)\][.|$]', path, re.IGNORECASE)

        for match in matches[:-1]:
            # print(path, match[0], match[1])
            key_or_index = match[0] or int(match[1])
            try:
                node = node[key_or_index]
            except (KeyError, IndexError):
                node[key_or_index] = {}
                node = node[key_or_index]

        match = matches[-1]
        node[match[0] or int(match[1])] = value

    def check_integrity(self, template: dict):
        """Check whether the config adheres to the given template.

        Attributes:
            template:      Template to be checked against

        """
        # TODO: create this functionality, that checks
        raise NotImplementedError('No integrity check yet')
