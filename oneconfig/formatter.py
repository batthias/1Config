"""Provide an extended Formatter, with more abilities."""
from string import Formatter as BaseFormatter, _string  # base versions


def list_to_str(names: list, pattern: str = '{n}', sep: str = ', ', last_sep: str = None):
    """Convert a list to a string.

    Example:
        >>> list_to_str([1,2,3,4], '{n}', ' and ', ' and also ')
        "1 and 2 and 3 and also 4"
    """
    if last_sep is None:  # by default use the same
        last_sep = sep
    max_i = len(names) - 1
    return sep.join([
        pattern.format(n=n)
        for n in names[:-1]
    ]) + last_sep + pattern.format(n=names[-1])


class Formatter(Formatter):
    """An extended format string formatter.

    Formatter with extended conversion symbol
    """
    def __init__(self, from_containers: bool = False, dot_item_access: bool = False):
        """Initialize the Formatter.

        Arguments:
            from_class:  use the arguments given to format as classes/dictionaries to look in.

        """
        self._from_containers = from_containers
        self._dot_item_access = dot_item_access

    def convert_field(self, value, conversion):
        """ Extend conversion symbol
        Following additional symbol has been added
        * l: convert to string and lowercase
        * u: convert to string and uppercase
        * t: convert string to titlecase
        * n: convert list to comma seperated string

        default are:
        * s: convert with str()
        * r: convert with repr()
        * a: convert with ascii()
        """
        try:
            conversion_function = getattr(self, '_convert_field_' + conversion)
        except (AttributeError, TypeError):
            # Do the default conversion or raise error if no matching conversion found
            return super().convert_field(value, conversion)
        else:
            return conversion_function(value)

    def _convert_field_u(self, value):
        """Convert to upper case."""
        return str(value).upper()

    def _convert_field_l(self, value):
        """Convert to lower case."""
        return str(value).lower()

    def _convert_field_t(self, value):
        """Convert to title case."""
        return str(value).title()

    def _convert_field_d(self, value):
        """Convert to a list of double quoted names."""
        return list_to_str(value, '"{n}"')

    def get_field(self, field_name, args, kwargs):
        first, rest = _string.formatter_field_name_split(field_name)
        obj = self.get_value(first, args, kwargs)

        # loop through the rest of the field_name, doing
        #  getattr or getitem as needed
        for is_attr, i in rest:
            if is_attr and not self._dot_item_access:
                obj = getattr(obj, i)
            else:
                obj = obj[i]
        return obj, first
        # return super().get_field(field_name, args, kwargs)

    def get_value(self, key, args, kwargs):
        """Get the value."""
        if self._from_containers:  # use args as classes / dicts
            for container in args:
                if isinstance(container, dict):
                    try:
                        return container[key]
                    except KeyError:
                        continue  # try the next one
                else:
                    try:
                        return getattr(container, key)
                    except AttributeError:
                        continue  # try the next one
            raise AttributeError(f'No attribute or item named {key} in any of the containers')

        else:   # use old implementation
            return super().get_value(key, args, kwargs)
