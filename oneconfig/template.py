"""Generate some files from the information in the config using some template.

The templates are located in the ``templates/`` folder and will be loaded by jinja2.
"""

from jinja2 import Environment, PackageLoader, select_autoescape


def customfilter(method):
    """A decorator specifying that this is a filter."""
    method.is_custom_filter = True
    return method


class Generator():
    """The file generator, which creates files from templates."""
    def __init__(self):
        self.env = Environment(
            loader=PackageLoader('oneconfig', 'templates'),
            autoescape=select_autoescape(['html', 'xml'], default_for_string=False),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # add all the customfilter methods in this class
        for name, method in self.__dict__.items():
            if getattr(method, 'is_custom_filter', False):
                self.env.filters[name] = method

    @customfilter
    def datetimeformat(value, format='%Y-%d-%m %H:%M:%S'):
        try:
            return value.strftime(format)  # TODO: actual method to do this
        except ValueError:  # TODO: wrong error
            return ''

    def generate(self, file: str, template, **options) -> None:
        encoding = options.get('encoding', 'utf-8')  # default encoding utf-8
        with open(file, mode='w', encoding=encoding) as f:
            f.write(self.generate_str(file, template, **options))

    def generate_str(self, file: str, template, **options) -> str:
        template = self.env.get_template('template')

        return template.render(the='variables', go='here')
