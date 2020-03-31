# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
from json import dumps as json_dumps

from django.forms.widgets import DateTimeBaseInput, NumberInput, TextInput


class AmountInput(NumberInput):
    """
    This input type lets the user type amounts in euros, but forms receive data in cents
    """
    template_name = "note/amount_input.html"

    def format_value(self, value):
        return None if value is None or value == "" else "{:.02f}".format(value / 100, )

    def value_from_datadict(self, data, files, name):
        val = super().value_from_datadict(data, files, name)
        return str(int(100 * float(val))) if val else val


class Autocomplete(TextInput):
    template_name = "member/autocomplete_model.html"

    def __init__(self, model, attrs=None):
        super().__init__(attrs)

        self.model = model
        self.model_pk = None

    class Media:
        """JS/CSS resources needed to render the date-picker calendar."""

        js = ('js/autocomplete_model.js', )

    def format_value(self, value):
        if value:
            self.attrs["model_pk"] = int(value)
            return str(self.model.objects.get(pk=int(value)))
        return ""


"""
The remaining of this file comes from the project `django-bootstrap-datepicker-plus` available on Github:
https://github.com/monim67/django-bootstrap-datepicker-plus
This is distributed under Apache License 2.0.

This adds datetime pickers with bootstrap.
"""

"""Contains Base Date-Picker input class for widgets of this package."""


class DatePickerDictionary:
    """Keeps track of all date-picker input classes."""

    _i = 0
    items = dict()

    @classmethod
    def generate_id(cls):
        """Return a unique ID for each date-picker input class."""
        cls._i += 1
        return 'dp_%s' % cls._i


class BasePickerInput(DateTimeBaseInput):
    """Base Date-Picker input class for widgets of this package."""

    template_name = 'bootstrap_datepicker_plus/date_picker.html'
    picker_type = 'DATE'
    format = '%Y-%m-%d'
    config = {}
    _default_config = {
        'id': None,
        'picker_type': None,
        'linked_to': None,
        'options': {}  # final merged options
    }
    options = {}  # options extended by user
    options_param = {}  # options passed as parameter
    _default_options = {
        'showClose': True,
        'showClear': True,
        'showTodayButton': True,
        "locale": "fr",
    }

    # source: https://github.com/tutorcruncher/django-bootstrap3-datetimepicker
    # file: /blob/31fbb09/bootstrap3_datetime/widgets.py#L33
    format_map = (
        ('DDD', r'%j'),
        ('DD', r'%d'),
        ('MMMM', r'%B'),
        ('MMM', r'%b'),
        ('MM', r'%m'),
        ('YYYY', r'%Y'),
        ('YY', r'%y'),
        ('HH', r'%H'),
        ('hh', r'%I'),
        ('mm', r'%M'),
        ('ss', r'%S'),
        ('a', r'%p'),
        ('ZZ', r'%z'),
    )

    class Media:
        """JS/CSS resources needed to render the date-picker calendar."""

        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.9.0/'
            'moment-with-locales.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/'
            '4.17.47/js/bootstrap-datetimepicker.min.js',
            'bootstrap_datepicker_plus/js/datepicker-widget.js'
        )
        css = {'all': (
            'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/'
            '4.17.47/css/bootstrap-datetimepicker.css',
            'bootstrap_datepicker_plus/css/datepicker-widget.css'
        ), }

    @classmethod
    def format_py2js(cls, datetime_format):
        """Convert python datetime format to moment datetime format."""
        for js_format, py_format in cls.format_map:
            datetime_format = datetime_format.replace(py_format, js_format)
        return datetime_format

    @classmethod
    def format_js2py(cls, datetime_format):
        """Convert moment datetime format to python datetime format."""
        for js_format, py_format in cls.format_map:
            datetime_format = datetime_format.replace(js_format, py_format)
        return datetime_format

    def __init__(self, attrs=None, format=None, options=None):
        """Initialize the Date-picker widget."""
        self.format_param = format
        self.options_param = options if options else {}
        self.config = self._default_config.copy()
        self.config['id'] = DatePickerDictionary.generate_id()
        self.config['picker_type'] = self.picker_type
        self.config['options'] = self._calculate_options()
        attrs = attrs if attrs else {}
        if 'class' not in attrs:
            attrs['class'] = 'form-control'
        super().__init__(attrs, self._calculate_format())

    def _calculate_options(self):
        """Calculate and Return the options."""
        _options = self._default_options.copy()
        _options.update(self.options)
        if self.options_param:
            _options.update(self.options_param)
        return _options

    def _calculate_format(self):
        """Calculate and Return the datetime format."""
        _format = self.format_param if self.format_param else self.format
        if self.config['options'].get('format'):
            _format = self.format_js2py(self.config['options'].get('format'))
        else:
            self.config['options']['format'] = self.format_py2js(_format)
        return _format

    def get_context(self, name, value, attrs):
        """Return widget context dictionary."""
        context = super().get_context(
            name, value, attrs)
        context['widget']['attrs']['dp_config'] = json_dumps(self.config)
        return context

    def start_of(self, event_id):
        """
        Set Date-Picker as the start-date of a date-range.

        Args:
            - event_id (string): User-defined unique id for linking two fields
        """
        DatePickerDictionary.items[str(event_id)] = self
        return self

    def end_of(self, event_id, import_options=True):
        """
        Set Date-Picker as the end-date of a date-range.

        Args:
            - event_id (string): User-defined unique id for linking two fields
            - import_options (bool): inherit options from start-date input,
              default: TRUE
        """
        event_id = str(event_id)
        if event_id in DatePickerDictionary.items:
            linked_picker = DatePickerDictionary.items[event_id]
            self.config['linked_to'] = linked_picker.config['id']
            if import_options:
                backup_moment_format = self.config['options']['format']
                self.config['options'].update(linked_picker.config['options'])
                self.config['options'].update(self.options_param)
                if self.format_param or 'format' in self.options_param:
                    self.config['options']['format'] = backup_moment_format
                else:
                    self.format = linked_picker.format
            # Setting useCurrent is necessary, see following issue
            # https://github.com/Eonasdan/bootstrap-datetimepicker/issues/1075
            self.config['options']['useCurrent'] = False
            self._link_to(linked_picker)
        else:
            raise KeyError(
                'start-date not specified for event_id "%s"' % event_id)
        return self

    def _link_to(self, linked_picker):
        """
        Executed when two date-inputs are linked together.

        This method for sub-classes to override to customize the linking.
        """
        pass


class DatePickerInput(BasePickerInput):
    """
    Widget to display a Date-Picker Calendar on a DateField property.

    Args:
        - attrs (dict): HTML attributes of rendered HTML input
        - format (string): Python DateTime format eg. "%Y-%m-%d"
        - options (dict): Options to customize the widget, see README
    """

    picker_type = 'DATE'
    format = '%Y-%m-%d'
    format_key = 'DATE_INPUT_FORMATS'


class TimePickerInput(BasePickerInput):
    """
    Widget to display a Time-Picker Calendar on a TimeField property.

    Args:
        - attrs (dict): HTML attributes of rendered HTML input
        - format (string): Python DateTime format eg. "%Y-%m-%d"
        - options (dict): Options to customize the widget, see README
    """

    picker_type = 'TIME'
    format = '%H:%M'
    format_key = 'TIME_INPUT_FORMATS'
    template_name = 'bootstrap_datepicker_plus/time_picker.html'


class DateTimePickerInput(BasePickerInput):
    """
    Widget to display a DateTime-Picker Calendar on a DateTimeField property.

    Args:
        - attrs (dict): HTML attributes of rendered HTML input
        - format (string): Python DateTime format eg. "%Y-%m-%d"
        - options (dict): Options to customize the widget, see README
    """

    picker_type = 'DATETIME'
    format = '%Y-%m-%d %H:%M'
    format_key = 'DATETIME_INPUT_FORMATS'


class MonthPickerInput(BasePickerInput):
    """
    Widget to display a Month-Picker Calendar on a DateField property.

    Args:
        - attrs (dict): HTML attributes of rendered HTML input
        - format (string): Python DateTime format eg. "%Y-%m-%d"
        - options (dict): Options to customize the widget, see README
    """

    picker_type = 'MONTH'
    format = '01/%m/%Y'
    format_key = 'DATE_INPUT_FORMATS'


class YearPickerInput(BasePickerInput):
    """
    Widget to display a Year-Picker Calendar on a DateField property.

    Args:
        - attrs (dict): HTML attributes of rendered HTML input
        - format (string): Python DateTime format eg. "%Y-%m-%d"
        - options (dict): Options to customize the widget, see README
    """

    picker_type = 'YEAR'
    format = '01/01/%Y'
    format_key = 'DATE_INPUT_FORMATS'

    def _link_to(self, linked_picker):
        """Customize the options when linked with other date-time input"""
        yformat = self.config['options']['format'].replace('-01-01', '-12-31')
        self.config['options']['format'] = yformat
