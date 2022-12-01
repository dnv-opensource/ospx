## #!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Generated  by generateDS.py.
# Python 3.10.2 (tags/v3.10.2:a58ebcc, Jan 17 2022, 14:12:15) [MSC v.1929 64 bit (AMD64)]
#
# Command line options:
#   ('-f', '')
#   ('-o', 'fmi2_api.py')
#   ('-s', 'fmi2_sub.py')
#   ('--no-dates', '')
#   ('--no-versions', '')
#   ('--no-redefine-groups', '')
#   ('--disable-generatedssuper-lookup', '')
#   ('--disable-xml', '')
#   ('--create-mandatory-children', '')
#
# Command line arguments:
#   fmi2ModelDescription.xsd
#
# Command line:
#   C:\Dev\ospx\.venv\Scripts\generateDS -f -o "fmi2_api.py" -s "fmi2_sub.py" --no-dates --no-versions --no-redefine-groups --disable-generatedssuper-lookup --disable-xml --create-mandatory-children fmi2ModelDescription.xsd
#
# Current working directory (os.getcwd()):
#   fmi2_generateds
#

import sys

try:
    ModulenotfoundExp_ = ModuleNotFoundError
except NameError:
    ModulenotfoundExp_ = ImportError
from six.moves import zip_longest
import os
import re as re_
import base64
import datetime as datetime_
import decimal as decimal_

## from lxml import etree as etree_

Validate_simpletypes_ = True
SaveElementTreeNode = True
TagNamePrefix = ""
if sys.version_info.major == 2:
    BaseStrType_ = basestring
else:
    BaseStrType_ = str

## def parsexml_(infile, parser=None, **kwargs):
##     if parser is None:
##         # Use the lxml ElementTree compatible parser so that, e.g.,
##         #   we ignore comments.
##         try:
##             parser = etree_.ETCompatXMLParser()
##         except AttributeError:
##             # fallback to xml.etree
##             parser = etree_.XMLParser()
##     try:
##         if isinstance(infile, os.PathLike):
##             infile = os.path.join(infile)
##     except AttributeError:
##         pass
##     doc = etree_.parse(infile, parser=parser, **kwargs)
##     return doc

## def parsexmlstring_(instring, parser=None, **kwargs):
##     if parser is None:
##         # Use the lxml ElementTree compatible parser so that, e.g.,
##         #   we ignore comments.
##         try:
##             parser = etree_.ETCompatXMLParser()
##         except AttributeError:
##             # fallback to xml.etree
##             parser = etree_.XMLParser()
##     element = etree_.fromstring(instring, parser=parser, **kwargs)
##     return element

#
# Namespace prefix definition table (and other attributes, too)
#
# The module generatedsnamespaces, if it is importable, must contain
# a dictionary named GeneratedsNamespaceDefs.  This Python dictionary
# should map element type names (strings) to XML schema namespace prefix
# definitions.  The export method for any class for which there is
# a namespace prefix definition, will export that definition in the
# XML representation of that element.  See the export method of
# any generated element type class for an example of the use of this
# table.
# A sample table is:
#
#     # File: generatedsnamespaces.py
#
#     GenerateDSNamespaceDefs = {
#         "ElementtypeA": "http://www.xxx.com/namespaceA",
#         "ElementtypeB": "http://www.xxx.com/namespaceB",
#     }
#
# Additionally, the generatedsnamespaces module can contain a python
# dictionary named GenerateDSNamespaceTypePrefixes that associates element
# types with the namespace prefixes that are to be added to the
# "xsi:type" attribute value.  See the _exportAttributes method of
# any generated element type and the generation of "xsi:type" for an
# example of the use of this table.
# An example table:
#
#     # File: generatedsnamespaces.py
#
#     GenerateDSNamespaceTypePrefixes = {
#         "ElementtypeC": "aaa:",
#         "ElementtypeD": "bbb:",
#     }
#

try:
    from generatedsnamespaces import GenerateDSNamespaceDefs as GenerateDSNamespaceDefs_
except ModulenotfoundExp_:
    GenerateDSNamespaceDefs_ = {}
try:
    from generatedsnamespaces import (
        GenerateDSNamespaceTypePrefixes as GenerateDSNamespaceTypePrefixes_,
    )
except ModulenotfoundExp_:
    GenerateDSNamespaceTypePrefixes_ = {}

#
# You can replace the following class definition by defining an
# importable module named "generatedscollector" containing a class
# named "GdsCollector".  See the default class definition below for
# clues about the possible content of that class.
#
try:
    from generatedscollector import GdsCollector as GdsCollector_
except ModulenotfoundExp_:

    class GdsCollector_(object):
        def __init__(self, messages=None):
            if messages is None:
                self.messages = []
            else:
                self.messages = messages

        def add_message(self, msg):
            self.messages.append(msg)

        def get_messages(self):
            return self.messages

        def clear_messages(self):
            self.messages = []

        def print_messages(self):
            for msg in self.messages:
                print("Warning: {}".format(msg))

        def write_messages(self, outstream):
            for msg in self.messages:
                outstream.write("Warning: {}\n".format(msg))


#
# The super-class for enum types
#

try:
    from enum import Enum
except ModulenotfoundExp_:
    Enum = object

#
# The root super-class for element type classes
#
# Calls to the methods in these classes are generated by generateDS.py.
# You can replace these methods by re-implementing the following class
#   in a module named generatedssuper.py.


class GeneratedsSuper(object):
    __hash__ = object.__hash__
    tzoff_pattern = re_.compile(r"(\+|-)((0\d|1[0-3]):[0-5]\d|14:00)$")

    class _FixedOffsetTZ(datetime_.tzinfo):
        def __init__(self, offset, name):
            self.__offset = datetime_.timedelta(minutes=offset)
            self.__name = name

        def utcoffset(self, dt):
            return self.__offset

        def tzname(self, dt):
            return self.__name

        def dst(self, dt):
            return None

    ##     def __str__(self):
    ##         settings = {
    ##             'str_pretty_print': True,
    ##             'str_indent_level': 0,
    ##             'str_namespaceprefix': '',
    ##             'str_name': self.__class__.__name__,
    ##             'str_namespacedefs': '',
    ##         }
    ##         for n in settings:
    ##             if hasattr(self, n):
    ##                 settings[n] = getattr(self, n)
    ##         if sys.version_info.major == 2:
    ##             from StringIO import StringIO
    ##         else:
    ##             from io import StringIO
    ##         output = StringIO()
    ##         self.export(
    ##             output,
    ##             settings['str_indent_level'],
    ##             pretty_print=settings['str_pretty_print'],
    ##             namespaceprefix_=settings['str_namespaceprefix'],
    ##             name_=settings['str_name'],
    ##             namespacedef_=settings['str_namespacedefs']
    ##         )
    ##         strval = output.getvalue()
    ##         output.close()
    ##         return strval

    def gds_format_string(self, input_data, input_name=""):
        return input_data

    def gds_parse_string(self, input_data, node=None, input_name=""):
        return input_data

    def gds_validate_string(self, input_data, node=None, input_name=""):
        if not input_data:
            return ""
        else:
            return input_data

    def gds_format_base64(self, input_data, input_name=""):
        return base64.b64encode(input_data).decode("ascii")

    def gds_validate_base64(self, input_data, node=None, input_name=""):
        return input_data

    def gds_format_integer(self, input_data, input_name=""):
        return "%d" % int(input_data)

    def gds_parse_integer(self, input_data, node=None, input_name=""):
        try:
            ival = int(input_data)
        except (TypeError, ValueError) as exp:
            raise_parse_error(node, "Requires integer value: %s" % exp)
        return ival

    def gds_validate_integer(self, input_data, node=None, input_name=""):
        try:
            value = int(input_data)
        except (TypeError, ValueError):
            raise_parse_error(node, "Requires integer value")
        return value

    def gds_format_integer_list(self, input_data, input_name=""):
        if len(input_data) > 0 and not isinstance(input_data[0], BaseStrType_):
            input_data = [str(s) for s in input_data]
        return "%s" % " ".join(input_data)

    def gds_validate_integer_list(self, input_data, node=None, input_name=""):
        values = input_data.split()
        for value in values:
            try:
                int(value)
            except (TypeError, ValueError):
                raise_parse_error(node, "Requires sequence of integer values")
        return values

    def gds_format_float(self, input_data, input_name=""):
        return ("%.15f" % float(input_data)).rstrip("0")

    def gds_parse_float(self, input_data, node=None, input_name=""):
        try:
            fval_ = float(input_data)
        except (TypeError, ValueError) as exp:
            raise_parse_error(node, "Requires float or double value: %s" % exp)
        return fval_

    def gds_validate_float(self, input_data, node=None, input_name=""):
        try:
            value = float(input_data)
        except (TypeError, ValueError):
            raise_parse_error(node, "Requires float value")
        return value

    def gds_format_float_list(self, input_data, input_name=""):
        if len(input_data) > 0 and not isinstance(input_data[0], BaseStrType_):
            input_data = [str(s) for s in input_data]
        return "%s" % " ".join(input_data)

    def gds_validate_float_list(self, input_data, node=None, input_name=""):
        values = input_data.split()
        for value in values:
            try:
                float(value)
            except (TypeError, ValueError):
                raise_parse_error(node, "Requires sequence of float values")
        return values

    def gds_format_decimal(self, input_data, input_name=""):
        return_value = "%s" % input_data
        if "." in return_value:
            return_value = return_value.rstrip("0")
            if return_value.endswith("."):
                return_value = return_value.rstrip(".")
        return return_value

    def gds_parse_decimal(self, input_data, node=None, input_name=""):
        try:
            decimal_value = decimal_.Decimal(input_data)
        except (TypeError, ValueError):
            raise_parse_error(node, "Requires decimal value")
        return decimal_value

    def gds_validate_decimal(self, input_data, node=None, input_name=""):
        try:
            value = decimal_.Decimal(input_data)
        except (TypeError, ValueError):
            raise_parse_error(node, "Requires decimal value")
        return value

    def gds_format_decimal_list(self, input_data, input_name=""):
        if len(input_data) > 0 and not isinstance(input_data[0], BaseStrType_):
            input_data = [str(s) for s in input_data]
        return " ".join([self.gds_format_decimal(item) for item in input_data])

    def gds_validate_decimal_list(self, input_data, node=None, input_name=""):
        values = input_data.split()
        for value in values:
            try:
                decimal_.Decimal(value)
            except (TypeError, ValueError):
                raise_parse_error(node, "Requires sequence of decimal values")
        return values

    def gds_format_double(self, input_data, input_name=""):
        return "%s" % input_data

    def gds_parse_double(self, input_data, node=None, input_name=""):
        try:
            fval_ = float(input_data)
        except (TypeError, ValueError) as exp:
            raise_parse_error(node, "Requires double or float value: %s" % exp)
        return fval_

    def gds_validate_double(self, input_data, node=None, input_name=""):
        try:
            value = float(input_data)
        except (TypeError, ValueError):
            raise_parse_error(node, "Requires double or float value")
        return value

    def gds_format_double_list(self, input_data, input_name=""):
        if len(input_data) > 0 and not isinstance(input_data[0], BaseStrType_):
            input_data = [str(s) for s in input_data]
        return "%s" % " ".join(input_data)

    def gds_validate_double_list(self, input_data, node=None, input_name=""):
        values = input_data.split()
        for value in values:
            try:
                float(value)
            except (TypeError, ValueError):
                raise_parse_error(node, "Requires sequence of double or float values")
        return values

    def gds_format_boolean(self, input_data, input_name=""):
        return ("%s" % input_data).lower()

    def gds_parse_boolean(self, input_data, node=None, input_name=""):
        input_data = input_data.strip()
        if input_data in ("true", "1"):
            bval = True
        elif input_data in ("false", "0"):
            bval = False
        else:
            raise_parse_error(node, "Requires boolean value")
        return bval

    def gds_validate_boolean(self, input_data, node=None, input_name=""):
        if input_data not in (
            True,
            1,
            False,
            0,
        ):
            raise_parse_error(
                node, "Requires boolean value " "(one of True, 1, False, 0)"
            )
        return input_data

    def gds_format_boolean_list(self, input_data, input_name=""):
        if len(input_data) > 0 and not isinstance(input_data[0], BaseStrType_):
            input_data = [str(s) for s in input_data]
        return "%s" % " ".join(input_data)

    def gds_validate_boolean_list(self, input_data, node=None, input_name=""):
        values = input_data.split()
        for value in values:
            value = self.gds_parse_boolean(value, node, input_name)
            if value not in (
                True,
                1,
                False,
                0,
            ):
                raise_parse_error(
                    node,
                    "Requires sequence of boolean values " "(one of True, 1, False, 0)",
                )
        return values

    def gds_validate_datetime(self, input_data, node=None, input_name=""):
        return input_data

    def gds_format_datetime(self, input_data, input_name=""):
        if input_data.microsecond == 0:
            _svalue = "%04d-%02d-%02dT%02d:%02d:%02d" % (
                input_data.year,
                input_data.month,
                input_data.day,
                input_data.hour,
                input_data.minute,
                input_data.second,
            )
        else:
            _svalue = "%04d-%02d-%02dT%02d:%02d:%02d.%s" % (
                input_data.year,
                input_data.month,
                input_data.day,
                input_data.hour,
                input_data.minute,
                input_data.second,
                ("%f" % (float(input_data.microsecond) / 1000000))[2:],
            )
        if input_data.tzinfo is not None:
            tzoff = input_data.tzinfo.utcoffset(input_data)
            if tzoff is not None:
                total_seconds = tzoff.seconds + (86400 * tzoff.days)
                if total_seconds == 0:
                    _svalue += "Z"
                else:
                    if total_seconds < 0:
                        _svalue += "-"
                        total_seconds *= -1
                    else:
                        _svalue += "+"
                    hours = total_seconds // 3600
                    minutes = (total_seconds - (hours * 3600)) // 60
                    _svalue += "{0:02d}:{1:02d}".format(hours, minutes)
        return _svalue

    @classmethod
    def gds_parse_datetime(cls, input_data):
        tz = None
        if input_data[-1] == "Z":
            tz = GeneratedsSuper._FixedOffsetTZ(0, "UTC")
            input_data = input_data[:-1]
        else:
            results = GeneratedsSuper.tzoff_pattern.search(input_data)
            if results is not None:
                tzoff_parts = results.group(2).split(":")
                tzoff = int(tzoff_parts[0]) * 60 + int(tzoff_parts[1])
                if results.group(1) == "-":
                    tzoff *= -1
                tz = GeneratedsSuper._FixedOffsetTZ(tzoff, results.group(0))
                input_data = input_data[:-6]
        time_parts = input_data.split(".")
        if len(time_parts) > 1:
            micro_seconds = int(float("0." + time_parts[1]) * 1000000)
            input_data = "%s.%s" % (
                time_parts[0],
                "{}".format(micro_seconds).rjust(6, "0"),
            )
            dt = datetime_.datetime.strptime(input_data, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            dt = datetime_.datetime.strptime(input_data, "%Y-%m-%dT%H:%M:%S")
        dt = dt.replace(tzinfo=tz)
        return dt

    def gds_validate_date(self, input_data, node=None, input_name=""):
        return input_data

    def gds_format_date(self, input_data, input_name=""):
        _svalue = "%04d-%02d-%02d" % (
            input_data.year,
            input_data.month,
            input_data.day,
        )
        try:
            if input_data.tzinfo is not None:
                tzoff = input_data.tzinfo.utcoffset(input_data)
                if tzoff is not None:
                    total_seconds = tzoff.seconds + (86400 * tzoff.days)
                    if total_seconds == 0:
                        _svalue += "Z"
                    else:
                        if total_seconds < 0:
                            _svalue += "-"
                            total_seconds *= -1
                        else:
                            _svalue += "+"
                        hours = total_seconds // 3600
                        minutes = (total_seconds - (hours * 3600)) // 60
                        _svalue += "{0:02d}:{1:02d}".format(hours, minutes)
        except AttributeError:
            pass
        return _svalue

    @classmethod
    def gds_parse_date(cls, input_data):
        tz = None
        if input_data[-1] == "Z":
            tz = GeneratedsSuper._FixedOffsetTZ(0, "UTC")
            input_data = input_data[:-1]
        else:
            results = GeneratedsSuper.tzoff_pattern.search(input_data)
            if results is not None:
                tzoff_parts = results.group(2).split(":")
                tzoff = int(tzoff_parts[0]) * 60 + int(tzoff_parts[1])
                if results.group(1) == "-":
                    tzoff *= -1
                tz = GeneratedsSuper._FixedOffsetTZ(tzoff, results.group(0))
                input_data = input_data[:-6]
        dt = datetime_.datetime.strptime(input_data, "%Y-%m-%d")
        dt = dt.replace(tzinfo=tz)
        return dt.date()

    def gds_validate_time(self, input_data, node=None, input_name=""):
        return input_data

    def gds_format_time(self, input_data, input_name=""):
        if input_data.microsecond == 0:
            _svalue = "%02d:%02d:%02d" % (
                input_data.hour,
                input_data.minute,
                input_data.second,
            )
        else:
            _svalue = "%02d:%02d:%02d.%s" % (
                input_data.hour,
                input_data.minute,
                input_data.second,
                ("%f" % (float(input_data.microsecond) / 1000000))[2:],
            )
        if input_data.tzinfo is not None:
            tzoff = input_data.tzinfo.utcoffset(input_data)
            if tzoff is not None:
                total_seconds = tzoff.seconds + (86400 * tzoff.days)
                if total_seconds == 0:
                    _svalue += "Z"
                else:
                    if total_seconds < 0:
                        _svalue += "-"
                        total_seconds *= -1
                    else:
                        _svalue += "+"
                    hours = total_seconds // 3600
                    minutes = (total_seconds - (hours * 3600)) // 60
                    _svalue += "{0:02d}:{1:02d}".format(hours, minutes)
        return _svalue

    def gds_validate_simple_patterns(self, patterns, target):
        # pat is a list of lists of strings/patterns.
        # The target value must match at least one of the patterns
        # in order for the test to succeed.
        found1 = True
        target = str(target)
        for patterns1 in patterns:
            found2 = False
            for patterns2 in patterns1:
                mo = re_.search(patterns2, target)
                if mo is not None and len(mo.group(0)) == len(target):
                    found2 = True
                    break
            if not found2:
                found1 = False
                break
        return found1

    @classmethod
    def gds_parse_time(cls, input_data):
        tz = None
        if input_data[-1] == "Z":
            tz = GeneratedsSuper._FixedOffsetTZ(0, "UTC")
            input_data = input_data[:-1]
        else:
            results = GeneratedsSuper.tzoff_pattern.search(input_data)
            if results is not None:
                tzoff_parts = results.group(2).split(":")
                tzoff = int(tzoff_parts[0]) * 60 + int(tzoff_parts[1])
                if results.group(1) == "-":
                    tzoff *= -1
                tz = GeneratedsSuper._FixedOffsetTZ(tzoff, results.group(0))
                input_data = input_data[:-6]
        if len(input_data.split(".")) > 1:
            dt = datetime_.datetime.strptime(input_data, "%H:%M:%S.%f")
        else:
            dt = datetime_.datetime.strptime(input_data, "%H:%M:%S")
        dt = dt.replace(tzinfo=tz)
        return dt.time()

    def gds_check_cardinality_(
        self, value, input_name, min_occurs=0, max_occurs=1, required=None
    ):
        if value is None:
            length = 0
        elif isinstance(value, list):
            length = len(value)
        else:
            length = 1
        if required is not None:
            if required and length < 1:
                self.gds_collector_.add_message(
                    "Required value {}{} is missing".format(
                        input_name, self.gds_get_node_lineno_()
                    )
                )
        if length < min_occurs:
            self.gds_collector_.add_message(
                "Number of values for {}{} is below "
                "the minimum allowed, "
                "expected at least {}, found {}".format(
                    input_name, self.gds_get_node_lineno_(), min_occurs, length
                )
            )
        elif length > max_occurs:
            self.gds_collector_.add_message(
                "Number of values for {}{} is above "
                "the maximum allowed, "
                "expected at most {}, found {}".format(
                    input_name, self.gds_get_node_lineno_(), max_occurs, length
                )
            )

    def gds_validate_builtin_ST_(
        self,
        validator,
        value,
        input_name,
        min_occurs=None,
        max_occurs=None,
        required=None,
    ):
        if value is not None:
            try:
                validator(value, input_name=input_name)
            except GDSParseError as parse_error:
                self.gds_collector_.add_message(str(parse_error))

    def gds_validate_defined_ST_(
        self,
        validator,
        value,
        input_name,
        min_occurs=None,
        max_occurs=None,
        required=None,
    ):
        if value is not None:
            try:
                validator(value)
            except GDSParseError as parse_error:
                self.gds_collector_.add_message(str(parse_error))

    def gds_str_lower(self, instring):
        return instring.lower()

    def get_path_(self, node):
        path_list = []
        self.get_path_list_(node, path_list)
        path_list.reverse()
        path = "/".join(path_list)
        return path

    Tag_strip_pattern_ = re_.compile(r"\{.*\}")

    def get_path_list_(self, node, path_list):
        if node is None:
            return
        tag = GeneratedsSuper.Tag_strip_pattern_.sub("", node.tag)
        if tag:
            path_list.append(tag)
        self.get_path_list_(node.getparent(), path_list)

    def get_class_obj_(self, node, default_class=None):
        class_obj1 = default_class
        if "xsi" in node.nsmap:
            classname = node.get("{%s}type" % node.nsmap["xsi"])
            if classname is not None:
                names = classname.split(":")
                if len(names) == 2:
                    classname = names[1]
                class_obj2 = globals().get(classname)
                if class_obj2 is not None:
                    class_obj1 = class_obj2
        return class_obj1

    def gds_build_any(self, node, type_name=None):
        # provide default value in case option --disable-xml is used.
        content = ""
        ##         content = etree_.tostring(node, encoding="unicode")
        return content

    @classmethod
    def gds_reverse_node_mapping(cls, mapping):
        return dict(((v, k) for k, v in mapping.items()))

    @staticmethod
    def gds_encode(instring):
        if sys.version_info.major == 2:
            if ExternalEncoding:
                encoding = ExternalEncoding
            else:
                encoding = "utf-8"
            return instring.encode(encoding)
        else:
            return instring

    @staticmethod
    def convert_unicode(instring):
        if isinstance(instring, str):
            result = quote_xml(instring)
        elif sys.version_info.major == 2 and isinstance(instring, unicode):
            result = quote_xml(instring).encode("utf8")
        else:
            result = GeneratedsSuper.gds_encode(str(instring))
        return result

    def __eq__(self, other):
        def excl_select_objs_(obj):
            return obj[0] != "parent_object_" and obj[0] != "gds_collector_"

        if type(self) != type(other):
            return False
        return all(
            x == y
            for x, y in zip_longest(
                filter(excl_select_objs_, self.__dict__.items()),
                filter(excl_select_objs_, other.__dict__.items()),
            )
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    # Django ETL transform hooks.
    def gds_djo_etl_transform(self):
        pass

    def gds_djo_etl_transform_db_obj(self, dbobj):
        pass

    # SQLAlchemy ETL transform hooks.
    def gds_sqa_etl_transform(self):
        return 0, None

    def gds_sqa_etl_transform_db_obj(self, dbobj):
        pass

    def gds_get_node_lineno_(self):
        if (
            hasattr(self, "gds_elementtree_node_")
            and self.gds_elementtree_node_ is not None
        ):
            return " near line {}".format(self.gds_elementtree_node_.sourceline)
        else:
            return ""


def getSubclassFromModule_(module, class_):
    """Get the subclass of a class from a specific module."""
    name = class_.__name__ + "Sub"
    if hasattr(module, name):
        return getattr(module, name)
    else:
        return None


#
# If you have installed IPython you can uncomment and use the following.
# IPython is available from http://ipython.scipy.org/.
#

## from IPython.Shell import IPShellEmbed
## args = ''
## ipshell = IPShellEmbed(args,
##     banner = 'Dropping into IPython',
##     exit_msg = 'Leaving Interpreter, back to program.')

# Then use the following line where and when you want to drop into the
# IPython shell:
#    ipshell('<some message> -- Entering ipshell.\nHit Ctrl-D to exit')

#
# Globals
#

ExternalEncoding = ""
# Set this to false in order to deactivate during export, the use of
# name space prefixes captured from the input document.
UseCapturedNS_ = True
CapturedNsmap_ = {}
Tag_pattern_ = re_.compile(r"({.*})?(.*)")
String_cleanup_pat_ = re_.compile(r"[\n\r\s]+")
Namespace_extract_pat_ = re_.compile(r"{(.*)}(.*)")
CDATA_pattern_ = re_.compile(r"<!\[CDATA\[.*?\]\]>", re_.DOTALL)

# Change this to redirect the generated superclass module to use a
# specific subclass module.
CurrentSubclassModule_ = None

#
# Support/utility functions.
#


def showIndent(outfile, level, pretty_print=True):
    if pretty_print:
        for idx in range(level):
            outfile.write("    ")


def quote_xml(inStr):
    "Escape markup chars, but do not modify CDATA sections."
    if not inStr:
        return ""
    s1 = isinstance(inStr, BaseStrType_) and inStr or "%s" % inStr
    s2 = ""
    pos = 0
    matchobjects = CDATA_pattern_.finditer(s1)
    for mo in matchobjects:
        s3 = s1[pos : mo.start()]
        s2 += quote_xml_aux(s3)
        s2 += s1[mo.start() : mo.end()]
        pos = mo.end()
    s3 = s1[pos:]
    s2 += quote_xml_aux(s3)
    return s2


def quote_xml_aux(inStr):
    s1 = inStr.replace("&", "&amp;")
    s1 = s1.replace("<", "&lt;")
    s1 = s1.replace(">", "&gt;")
    return s1


def quote_attrib(inStr):
    s1 = isinstance(inStr, BaseStrType_) and inStr or "%s" % inStr
    s1 = s1.replace("&", "&amp;")
    s1 = s1.replace("<", "&lt;")
    s1 = s1.replace(">", "&gt;")
    s1 = s1.replace("\n", "&#10;")
    if '"' in s1:
        if "'" in s1:
            s1 = '"%s"' % s1.replace('"', "&quot;")
        else:
            s1 = "'%s'" % s1
    else:
        s1 = '"%s"' % s1
    return s1


def quote_python(inStr):
    s1 = inStr
    if s1.find("'") == -1:
        if s1.find("\n") == -1:
            return "'%s'" % s1
        else:
            return "'''%s'''" % s1
    else:
        if s1.find('"') != -1:
            s1 = s1.replace('"', '\\"')
        if s1.find("\n") == -1:
            return '"%s"' % s1
        else:
            return '"""%s"""' % s1


def get_all_text_(node):
    if node.text is not None:
        text = node.text
    else:
        text = ""
    for child in node:
        if child.tail is not None:
            text += child.tail
    return text


def find_attr_value_(attr_name, node):
    attrs = node.attrib
    attr_parts = attr_name.split(":")
    value = None
    if len(attr_parts) == 1:
        value = attrs.get(attr_name)
    elif len(attr_parts) == 2:
        prefix, name = attr_parts
        if prefix == "xml":
            namespace = "http://www.w3.org/XML/1998/namespace"
        else:
            namespace = node.nsmap.get(prefix)
        if namespace is not None:
            value = attrs.get(
                "{%s}%s"
                % (
                    namespace,
                    name,
                )
            )
    return value


def encode_str_2_3(instr):
    return instr


class GDSParseError(Exception):
    pass


def raise_parse_error(node, msg):
    if node is not None:
        msg = "%s (element %s/line %d)" % (
            msg,
            node.tag,
            node.sourceline,
        )
    raise GDSParseError(msg)


class MixedContainer:
    # Constants for category:
    CategoryNone = 0
    CategoryText = 1
    CategorySimple = 2
    CategoryComplex = 3
    # Constants for content_type:
    TypeNone = 0
    TypeText = 1
    TypeString = 2
    TypeInteger = 3
    TypeFloat = 4
    TypeDecimal = 5
    TypeDouble = 6
    TypeBoolean = 7
    TypeBase64 = 8

    def __init__(self, category, content_type, name, value):
        self.category = category
        self.content_type = content_type
        self.name = name
        self.value = value

    def getCategory(self):
        return self.category

    def getContenttype(self, content_type):
        return self.content_type

    def getValue(self):
        return self.value

    def getName(self):
        return self.name


##     def export(self, outfile, level, name, namespace,
##                pretty_print=True):
##         if self.category == MixedContainer.CategoryText:
##             # Prevent exporting empty content as empty lines.
##             if self.value.strip():
##                 outfile.write(self.value)
##         elif self.category == MixedContainer.CategorySimple:
##             self.exportSimple(outfile, level, name)
##         else:    # category == MixedContainer.CategoryComplex
##             self.value.export(
##                 outfile, level, namespace, name_=name,
##                 pretty_print=pretty_print)
##     def exportSimple(self, outfile, level, name):
##         if self.content_type == MixedContainer.TypeString:
##             outfile.write('<%s>%s</%s>' % (
##                 self.name, self.value, self.name))
##         elif self.content_type == MixedContainer.TypeInteger or \
##                 self.content_type == MixedContainer.TypeBoolean:
##             outfile.write('<%s>%d</%s>' % (
##                 self.name, self.value, self.name))
##         elif self.content_type == MixedContainer.TypeFloat or \
##                 self.content_type == MixedContainer.TypeDecimal:
##             outfile.write('<%s>%f</%s>' % (
##                 self.name, self.value, self.name))
##         elif self.content_type == MixedContainer.TypeDouble:
##             outfile.write('<%s>%g</%s>' % (
##                 self.name, self.value, self.name))
##         elif self.content_type == MixedContainer.TypeBase64:
##             outfile.write('<%s>%s</%s>' % (
##                 self.name,
##                 base64.b64encode(self.value),
##                 self.name))
##     def to_etree(self, element, mapping_=None, reverse_mapping_=None, nsmap_=None):
##         if self.category == MixedContainer.CategoryText:
##             # Prevent exporting empty content as empty lines.
##             if self.value.strip():
##                 if len(element) > 0:
##                     if element[-1].tail is None:
##                         element[-1].tail = self.value
##                     else:
##                         element[-1].tail += self.value
##                 else:
##                     if element.text is None:
##                         element.text = self.value
##                     else:
##                         element.text += self.value
##         elif self.category == MixedContainer.CategorySimple:
##             subelement = etree_.SubElement(
##                 element, '%s' % self.name)
##             subelement.text = self.to_etree_simple()
##         else:    # category == MixedContainer.CategoryComplex
##             self.value.to_etree(element)
##     def to_etree_simple(self, mapping_=None, reverse_mapping_=None, nsmap_=None):
##         if self.content_type == MixedContainer.TypeString:
##             text = self.value
##         elif (self.content_type == MixedContainer.TypeInteger or
##                 self.content_type == MixedContainer.TypeBoolean):
##             text = '%d' % self.value
##         elif (self.content_type == MixedContainer.TypeFloat or
##                 self.content_type == MixedContainer.TypeDecimal):
##             text = '%f' % self.value
##         elif self.content_type == MixedContainer.TypeDouble:
##             text = '%g' % self.value
##         elif self.content_type == MixedContainer.TypeBase64:
##             text = '%s' % base64.b64encode(self.value)
##         return text
##     def exportLiteral(self, outfile, level, name):
##         if self.category == MixedContainer.CategoryText:
##             showIndent(outfile, level)
##             outfile.write(
##                 'model_.MixedContainer(%d, %d, "%s", "%s"),\n' % (
##                     self.category, self.content_type,
##                     self.name, self.value))
##         elif self.category == MixedContainer.CategorySimple:
##             showIndent(outfile, level)
##             outfile.write(
##                 'model_.MixedContainer(%d, %d, "%s", "%s"),\n' % (
##                     self.category, self.content_type,
##                     self.name, self.value))
##         else:    # category == MixedContainer.CategoryComplex
##             showIndent(outfile, level)
##             outfile.write(
##                 'model_.MixedContainer(%d, %d, "%s",\n' % (
##                     self.category, self.content_type, self.name,))
##             self.value.exportLiteral(outfile, level + 1)
##             showIndent(outfile, level)
##             outfile.write(')\n')


class MemberSpec_(object):
    def __init__(
        self,
        name="",
        data_type="",
        container=0,
        optional=0,
        child_attrs=None,
        choice=None,
    ):
        self.name = name
        self.data_type = data_type
        self.container = container
        self.child_attrs = child_attrs
        self.choice = choice
        self.optional = optional

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_data_type(self, data_type):
        self.data_type = data_type

    def get_data_type_chain(self):
        return self.data_type

    def get_data_type(self):
        if isinstance(self.data_type, list):
            if len(self.data_type) > 0:
                return self.data_type[-1]
            else:
                return "xs:string"
        else:
            return self.data_type

    def set_container(self, container):
        self.container = container

    def get_container(self):
        return self.container

    def set_child_attrs(self, child_attrs):
        self.child_attrs = child_attrs

    def get_child_attrs(self):
        return self.child_attrs

    def set_choice(self, choice):
        self.choice = choice

    def get_choice(self):
        return self.choice

    def set_optional(self, optional):
        self.optional = optional

    def get_optional(self):
        return self.optional


def _cast(typ, value):
    if typ is None or value is None:
        return value
    return typ(value)


#
# Data representation classes.
#


class causalityType(str, Enum):
    """causalityType -- parameter: independent parameter
    calculatedParameter: calculated parameter
    input/output: can be used in connections
    local: variable calculated from other variables
    independent: independent variable (usually time)

    """

    PARAMETER = "parameter"
    CALCULATED_PARAMETER = "calculatedParameter"
    INPUT = "input"
    OUTPUT = "output"
    LOCAL = "local"
    INDEPENDENT = "independent"


class dependenciesKindType(str, Enum):
    """dependenciesKindType -- If not present, it must be assumed that the Unknown depends on the Knowns without a particular structure. Otherwise, the corresponding Known v enters the equation as:
    = "dependent": no particular structure, f(v)
    = "constant"   : constant factor, c*v (only for Real variables)
    If "dependenciesKind" is present, "dependencies" must be present and must have the same number of list elements.

    """

    DEPENDENT = "dependent"
    CONSTANT = "constant"
    FIXED = "fixed"
    TUNABLE = "tunable"
    DISCRETE = "discrete"


class dependenciesKindType5(str, Enum):
    """dependenciesKindType5 -- If not present, it must be assumed that the Unknown depends on the Knowns without a particular structure. Otherwise, the corresponding Known v enters the equation as:
    = "dependent": no particular structure, f(v)
    = "constant"   : constant factor, c*v (only for Real variablse)
    = "fixed"        : fixed factor, p*v (only for Real variables)
    = "tunable"    : tunable factor, p*v (only for Real variables)
    = "discrete"    : discrete factor, d*v (only for Real variables)
    If "dependenciesKind" is present, "dependencies" must be present and must have the same number of list elements.

    """

    DEPENDENT = "dependent"
    CONSTANT = "constant"
    FIXED = "fixed"
    TUNABLE = "tunable"
    DISCRETE = "discrete"


class initialType(str, Enum):
    """initialType -- exact: initialized with start value
    approx: iteration variable that starts with start value
    calculated: calculated from other variables.
    If not provided, initial is deduced from causality and variability (details see specification)

    """

    EXACT = "exact"
    APPROX = "approx"
    CALCULATED = "calculated"


class variabilityType(str, Enum):
    """variabilityType -- constant: value never changes
    fixed: value fixed after initialization
    tunable: value constant between external events
    discrete: value constant between internal events
    continuous: no restriction on value changes

    """

    CONSTANT = "constant"
    FIXED = "fixed"
    TUNABLE = "tunable"
    DISCRETE = "discrete"
    CONTINUOUS = "continuous"


class variableNamingConventionType(str, Enum):
    FLAT = "flat"
    STRUCTURED = "structured"


class fmiModelDescription(GeneratedsSuper):
    """fmiModelDescription -- At least one of the elements must be present
    fmiVersion -- Version of FMI (Clarification for FMI 2.0.2: for FMI 2.0.x revisions fmiVersion is defined as "2.0").
    modelName -- Class name of FMU, e.g. "A.B.C" (several FMU instances are possible)
    guid -- Fingerprint of xml-file content to verify that xml-file and C-functions are compatible to each other
    version -- Version of FMU, e.g., "1.4.1"
    copyright -- Information on intellectual property copyright for this FMU, such as
    “
    ©
    MyCompany 2011
    “
    license -- Information on intellectual property licensing for this FMU, such as
    “
    BSD license
    ”
    , "Proprietary", or "Public Domain"
    ModelExchange -- The FMU includes a model or the communication to a tool that provides a model. The environment provides the simulation engine for the model.
    CoSimulation -- The FMU includes a model and the simulation engine, or the communication to a tool that provides this. The environment provides the master algorithm for the Co-Simulation coupling.
    LogCategories -- Log categories available in FMU
    VendorAnnotations -- Tool specific data (ignored by other tools)
    ModelVariables -- Ordered list of all variables (first definition has index = 1).
    ModelStructure -- Ordered lists of outputs, exposed state derivatives,
    and the initial unknowns. Optionally, the functional
    dependency of these variables can be defined.

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        fmiVersion="2.0",
        modelName=None,
        guid=None,
        description=None,
        author=None,
        version=None,
        copyright=None,
        license=None,
        generationTool=None,
        generationDateAndTime=None,
        variableNamingConvention="flat",
        numberOfEventIndicators=None,
        ModelExchange=None,
        CoSimulation=None,
        UnitDefinitions=None,
        TypeDefinitions=None,
        LogCategories=None,
        DefaultExperiment=None,
        VendorAnnotations=None,
        ModelVariables=None,
        ModelStructure=None,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.fmiVersion = _cast(None, fmiVersion)
        self.modelName = _cast(None, modelName)
        self.guid = _cast(None, guid)
        self.description = _cast(None, description)
        self.author = _cast(None, author)
        self.version = _cast(None, version)
        self.copyright = _cast(None, copyright)
        self.license = _cast(None, license)
        self.generationTool = _cast(None, generationTool)
        if isinstance(generationDateAndTime, BaseStrType_):
            initvalue_ = datetime_.datetime.strptime(
                generationDateAndTime, "%Y-%m-%dT%H:%M:%S"
            )
        else:
            initvalue_ = generationDateAndTime
        self.generationDateAndTime = initvalue_
        self.variableNamingConvention = _cast(None, variableNamingConvention)
        self.numberOfEventIndicators = _cast(int, numberOfEventIndicators)
        if ModelExchange is None:
            self.ModelExchange = []
        else:
            self.ModelExchange = ModelExchange
        if CoSimulation is None:
            self.CoSimulation = []
        else:
            self.CoSimulation = CoSimulation
        self.UnitDefinitions = UnitDefinitions
        self.TypeDefinitions = TypeDefinitions
        self.LogCategories = LogCategories
        self.DefaultExperiment = DefaultExperiment
        self.VendorAnnotations = VendorAnnotations
        if ModelVariables is None:
            self.ModelVariables = globals()["ModelVariablesType"]()
        else:
            self.ModelVariables = ModelVariables
        if ModelStructure is None:
            self.ModelStructure = globals()["ModelStructureType"]()
        else:
            self.ModelStructure = ModelStructure

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, fmiModelDescription
            )
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if fmiModelDescription.subclass:
            return fmiModelDescription.subclass(*args_, **kwargs_)
        else:
            return fmiModelDescription(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_ModelExchange(self):
        return self.ModelExchange

    def set_ModelExchange(self, ModelExchange):
        self.ModelExchange = ModelExchange

    def add_ModelExchange(self, value):
        self.ModelExchange.append(value)

    def insert_ModelExchange_at(self, index, value):
        self.ModelExchange.insert(index, value)

    def replace_ModelExchange_at(self, index, value):
        self.ModelExchange[index] = value

    def get_CoSimulation(self):
        return self.CoSimulation

    def set_CoSimulation(self, CoSimulation):
        self.CoSimulation = CoSimulation

    def add_CoSimulation(self, value):
        self.CoSimulation.append(value)

    def insert_CoSimulation_at(self, index, value):
        self.CoSimulation.insert(index, value)

    def replace_CoSimulation_at(self, index, value):
        self.CoSimulation[index] = value

    def get_UnitDefinitions(self):
        return self.UnitDefinitions

    def set_UnitDefinitions(self, UnitDefinitions):
        self.UnitDefinitions = UnitDefinitions

    def get_TypeDefinitions(self):
        return self.TypeDefinitions

    def set_TypeDefinitions(self, TypeDefinitions):
        self.TypeDefinitions = TypeDefinitions

    def get_LogCategories(self):
        return self.LogCategories

    def set_LogCategories(self, LogCategories):
        self.LogCategories = LogCategories

    def get_DefaultExperiment(self):
        return self.DefaultExperiment

    def set_DefaultExperiment(self, DefaultExperiment):
        self.DefaultExperiment = DefaultExperiment

    def get_VendorAnnotations(self):
        return self.VendorAnnotations

    def set_VendorAnnotations(self, VendorAnnotations):
        self.VendorAnnotations = VendorAnnotations

    def get_ModelVariables(self):
        return self.ModelVariables

    def set_ModelVariables(self, ModelVariables):
        self.ModelVariables = ModelVariables

    def get_ModelStructure(self):
        return self.ModelStructure

    def set_ModelStructure(self, ModelStructure):
        self.ModelStructure = ModelStructure

    def get_fmiVersion(self):
        return self.fmiVersion

    def set_fmiVersion(self, fmiVersion):
        self.fmiVersion = fmiVersion

    def get_modelName(self):
        return self.modelName

    def set_modelName(self, modelName):
        self.modelName = modelName

    def get_guid(self):
        return self.guid

    def set_guid(self, guid):
        self.guid = guid

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_author(self):
        return self.author

    def set_author(self, author):
        self.author = author

    def get_version(self):
        return self.version

    def set_version(self, version):
        self.version = version

    def get_copyright(self):
        return self.copyright

    def set_copyright(self, copyright):
        self.copyright = copyright

    def get_license(self):
        return self.license

    def set_license(self, license):
        self.license = license

    def get_generationTool(self):
        return self.generationTool

    def set_generationTool(self, generationTool):
        self.generationTool = generationTool

    def get_generationDateAndTime(self):
        return self.generationDateAndTime

    def set_generationDateAndTime(self, generationDateAndTime):
        self.generationDateAndTime = generationDateAndTime

    def get_variableNamingConvention(self):
        return self.variableNamingConvention

    def set_variableNamingConvention(self, variableNamingConvention):
        self.variableNamingConvention = variableNamingConvention

    def get_numberOfEventIndicators(self):
        return self.numberOfEventIndicators

    def set_numberOfEventIndicators(self, numberOfEventIndicators):
        self.numberOfEventIndicators = numberOfEventIndicators

    def validate_variableNamingConventionType(self, value):
        # Validate type variableNamingConventionType, a restriction on xs:normalizedString.
        if (
            value is not None
            and Validate_simpletypes_
            and self.gds_collector_ is not None
        ):
            if not isinstance(value, str):
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message(
                    'Value "%(value)s"%(lineno)s is not of the correct base simple type (str)'
                    % {
                        "value": value,
                        "lineno": lineno,
                    }
                )
                return False
            value = value
            enumerations = ["flat", "structured"]
            if value not in enumerations:
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message(
                    'Value "%(value)s"%(lineno)s does not match xsd enumeration restriction on variableNamingConventionType'
                    % {"value": encode_str_2_3(value), "lineno": lineno}
                )
                result = False

    def _hasContent(self):
        if (
            self.ModelExchange
            or self.CoSimulation
            or self.UnitDefinitions is not None
            or self.TypeDefinitions is not None
            or self.LogCategories is not None
            or self.DefaultExperiment is not None
            or self.VendorAnnotations is not None
            or self.ModelVariables is not None
            or self.ModelStructure is not None
        ):
            return True
        else:
            return False


# end class fmiModelDescription


class fmi2ScalarVariable(GeneratedsSuper):
    """fmi2ScalarVariable -- Properties of a scalar variable
    name -- Identifier of variable, e.g. "a.b.mod[3,4].'#123'.c". "name" must be unique with respect to all other elements of the ModelVariables list
    valueReference -- Identifier for variable value in FMI2 function calls (not necessarily unique with respect to all variables)
    causality -- parameter: independent parameter
    calculatedParameter: calculated parameter
    input/output: can be used in connections
    local: variable calculated from other variables
    independent: independent variable (usually time)
    variability -- constant: value never changes
    fixed: value fixed after initialization
    tunable: value constant between external events
    discrete: value constant between internal events
    continuous: no restriction on value changes
    initial -- exact: initialized with start value
    approx: iteration variable that starts with start value
    calculated: calculated from other variables.
    If not provided, initial is deduced from causality and variability (details see specification)
    canHandleMultipleSetPerTimeInstant -- Only for ModelExchange and only for variables with variability = "input":
    If present with value = false, then only one fmi2SetXXX call is allowed at one super dense time instant. In other words, this input is not allowed to appear in an algebraic loop.
    Annotations -- Additional data of the scalar variable, e.g., for the dialog menu or the graphical layout

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        name=None,
        valueReference=None,
        description=None,
        causality="local",
        variability="continuous",
        initial=None,
        canHandleMultipleSetPerTimeInstant=None,
        Real=None,
        Integer=None,
        Boolean=None,
        String=None,
        Enumeration=None,
        Annotations=None,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.name = _cast(None, name)
        self.valueReference = _cast(int, valueReference)
        self.description = _cast(None, description)
        self.causality = _cast(None, causality)
        self.variability = _cast(None, variability)
        self.initial = _cast(None, initial)
        self.canHandleMultipleSetPerTimeInstant = _cast(
            bool, canHandleMultipleSetPerTimeInstant
        )
        if Real is None:
            self.Real = globals()["RealType"]()
        else:
            self.Real = Real
        if Integer is None:
            self.Integer = globals()["IntegerType"]()
        else:
            self.Integer = Integer
        if Boolean is None:
            self.Boolean = globals()["BooleanType"]()
        else:
            self.Boolean = Boolean
        if String is None:
            self.String = globals()["StringType"]()
        else:
            self.String = String
        if Enumeration is None:
            self.Enumeration = globals()["EnumerationType"]()
        else:
            self.Enumeration = Enumeration
        self.Annotations = Annotations

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, fmi2ScalarVariable
            )
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if fmi2ScalarVariable.subclass:
            return fmi2ScalarVariable.subclass(*args_, **kwargs_)
        else:
            return fmi2ScalarVariable(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_Real(self):
        return self.Real

    def set_Real(self, Real):
        self.Real = Real

    def get_Integer(self):
        return self.Integer

    def set_Integer(self, Integer):
        self.Integer = Integer

    def get_Boolean(self):
        return self.Boolean

    def set_Boolean(self, Boolean):
        self.Boolean = Boolean

    def get_String(self):
        return self.String

    def set_String(self, String):
        self.String = String

    def get_Enumeration(self):
        return self.Enumeration

    def set_Enumeration(self, Enumeration):
        self.Enumeration = Enumeration

    def get_Annotations(self):
        return self.Annotations

    def set_Annotations(self, Annotations):
        self.Annotations = Annotations

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_valueReference(self):
        return self.valueReference

    def set_valueReference(self, valueReference):
        self.valueReference = valueReference

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_causality(self):
        return self.causality

    def set_causality(self, causality):
        self.causality = causality

    def get_variability(self):
        return self.variability

    def set_variability(self, variability):
        self.variability = variability

    def get_initial(self):
        return self.initial

    def set_initial(self, initial):
        self.initial = initial

    def get_canHandleMultipleSetPerTimeInstant(self):
        return self.canHandleMultipleSetPerTimeInstant

    def set_canHandleMultipleSetPerTimeInstant(
        self, canHandleMultipleSetPerTimeInstant
    ):
        self.canHandleMultipleSetPerTimeInstant = canHandleMultipleSetPerTimeInstant

    def validate_causalityType(self, value):
        # Validate type causalityType, a restriction on xs:normalizedString.
        if (
            value is not None
            and Validate_simpletypes_
            and self.gds_collector_ is not None
        ):
            if not isinstance(value, str):
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message(
                    'Value "%(value)s"%(lineno)s is not of the correct base simple type (str)'
                    % {
                        "value": value,
                        "lineno": lineno,
                    }
                )
                return False
            value = value
            enumerations = [
                "parameter",
                "calculatedParameter",
                "input",
                "output",
                "local",
                "independent",
            ]
            if value not in enumerations:
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message(
                    'Value "%(value)s"%(lineno)s does not match xsd enumeration restriction on causalityType'
                    % {"value": encode_str_2_3(value), "lineno": lineno}
                )
                result = False

    def validate_variabilityType(self, value):
        # Validate type variabilityType, a restriction on xs:normalizedString.
        if (
            value is not None
            and Validate_simpletypes_
            and self.gds_collector_ is not None
        ):
            if not isinstance(value, str):
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message(
                    'Value "%(value)s"%(lineno)s is not of the correct base simple type (str)'
                    % {
                        "value": value,
                        "lineno": lineno,
                    }
                )
                return False
            value = value
            enumerations = ["constant", "fixed", "tunable", "discrete", "continuous"]
            if value not in enumerations:
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message(
                    'Value "%(value)s"%(lineno)s does not match xsd enumeration restriction on variabilityType'
                    % {"value": encode_str_2_3(value), "lineno": lineno}
                )
                result = False

    def validate_initialType(self, value):
        # Validate type initialType, a restriction on xs:normalizedString.
        if (
            value is not None
            and Validate_simpletypes_
            and self.gds_collector_ is not None
        ):
            if not isinstance(value, str):
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message(
                    'Value "%(value)s"%(lineno)s is not of the correct base simple type (str)'
                    % {
                        "value": value,
                        "lineno": lineno,
                    }
                )
                return False
            value = value
            enumerations = ["exact", "approx", "calculated"]
            if value not in enumerations:
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message(
                    'Value "%(value)s"%(lineno)s does not match xsd enumeration restriction on initialType'
                    % {"value": encode_str_2_3(value), "lineno": lineno}
                )
                result = False

    def _hasContent(self):
        if (
            self.Real is not None
            or self.Integer is not None
            or self.Boolean is not None
            or self.String is not None
            or self.Enumeration is not None
            or self.Annotations is not None
        ):
            return True
        else:
            return False


# end class fmi2ScalarVariable


class fmi2Annotation(GeneratedsSuper):
    """Tool -- Tool specific annotation (ignored by other tools)."""

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, Tool=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        if Tool is None:
            self.Tool = []
        else:
            self.Tool = Tool

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, fmi2Annotation)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if fmi2Annotation.subclass:
            return fmi2Annotation.subclass(*args_, **kwargs_)
        else:
            return fmi2Annotation(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_Tool(self):
        return self.Tool

    def set_Tool(self, Tool):
        self.Tool = Tool

    def add_Tool(self, value):
        self.Tool.append(value)

    def insert_Tool_at(self, index, value):
        self.Tool.insert(index, value)

    def replace_Tool_at(self, index, value):
        self.Tool[index] = value

    def _hasContent(self):
        if self.Tool:
            return True
        else:
            return False


# end class fmi2Annotation


class fmi2VariableDependency(GeneratedsSuper):
    """Dependency of scalar Unknown from Knowns
    Unknown -- Dependency of scalar Unknown from Knowns
    in Continuous-Time and Event Mode (ModelExchange),
    and at Communication Points (CoSimulation):
    Unknown=f(Known_1, Known_2, ...).
    The Knowns are "inputs", "continuous states" and
    "independent variable" (usually time)".

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, Unknown=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        if Unknown is None:
            self.Unknown = []
        else:
            self.Unknown = Unknown

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, fmi2VariableDependency
            )
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if fmi2VariableDependency.subclass:
            return fmi2VariableDependency.subclass(*args_, **kwargs_)
        else:
            return fmi2VariableDependency(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_Unknown(self):
        return self.Unknown

    def set_Unknown(self, Unknown):
        self.Unknown = Unknown

    def add_Unknown(self, value):
        self.Unknown.append(value)

    def insert_Unknown_at(self, index, value):
        self.Unknown.insert(index, value)

    def replace_Unknown_at(self, index, value):
        self.Unknown[index] = value

    def _hasContent(self):
        if self.Unknown:
            return True
        else:
            return False


# end class fmi2VariableDependency


class fmi2Unit(GeneratedsSuper):
    """fmi2Unit -- Unit definition (with respect to SI base units) and default display units
    name -- Name of Unit element, e.g. "N.m", "Nm",  "%/s". "name" must be unique will respect to all other elements of the UnitDefinitions list. The variable values of fmi2SetXXX and fmi2GetXXX are with respect to this unit.
    BaseUnit -- BaseUnit_value = factor*Unit_value + offset
    DisplayUnit -- DisplayUnit_value = factor*Unit_value + offset

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self, name=None, BaseUnit=None, DisplayUnit=None, gds_collector_=None, **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.name = _cast(None, name)
        self.BaseUnit = BaseUnit
        if DisplayUnit is None:
            self.DisplayUnit = []
        else:
            self.DisplayUnit = DisplayUnit

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, fmi2Unit)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if fmi2Unit.subclass:
            return fmi2Unit.subclass(*args_, **kwargs_)
        else:
            return fmi2Unit(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_BaseUnit(self):
        return self.BaseUnit

    def set_BaseUnit(self, BaseUnit):
        self.BaseUnit = BaseUnit

    def get_DisplayUnit(self):
        return self.DisplayUnit

    def set_DisplayUnit(self, DisplayUnit):
        self.DisplayUnit = DisplayUnit

    def add_DisplayUnit(self, value):
        self.DisplayUnit.append(value)

    def insert_DisplayUnit_at(self, index, value):
        self.DisplayUnit.insert(index, value)

    def replace_DisplayUnit_at(self, index, value):
        self.DisplayUnit[index] = value

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def _hasContent(self):
        if self.BaseUnit is not None or self.DisplayUnit:
            return True
        else:
            return False


# end class fmi2Unit


class fmi2SimpleType(GeneratedsSuper):
    """fmi2SimpleType -- Type attributes of a scalar variable
    name -- Name of SimpleType element. "name" must be unique with respect to all other elements of the TypeDefinitions list. Furthermore,  "name" of a SimpleType must be different to all "name"s of ScalarVariable.
    description -- Description of the SimpleType

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        name=None,
        description=None,
        Real=None,
        Integer=None,
        Boolean=None,
        String=None,
        Enumeration=None,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.name = _cast(None, name)
        self.description = _cast(None, description)
        if Real is None:
            self.Real = globals()["RealType6"]()
        else:
            self.Real = Real
        if Integer is None:
            self.Integer = globals()["IntegerType7"]()
        else:
            self.Integer = Integer
        self.Boolean = Boolean
        self.String = String
        if Enumeration is None:
            self.Enumeration = globals()["EnumerationType8"]()
        else:
            self.Enumeration = Enumeration

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, fmi2SimpleType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if fmi2SimpleType.subclass:
            return fmi2SimpleType.subclass(*args_, **kwargs_)
        else:
            return fmi2SimpleType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_Real(self):
        return self.Real

    def set_Real(self, Real):
        self.Real = Real

    def get_Integer(self):
        return self.Integer

    def set_Integer(self, Integer):
        self.Integer = Integer

    def get_Boolean(self):
        return self.Boolean

    def set_Boolean(self, Boolean):
        self.Boolean = Boolean

    def get_String(self):
        return self.String

    def set_String(self, String):
        self.String = String

    def get_Enumeration(self):
        return self.Enumeration

    def set_Enumeration(self, Enumeration):
        self.Enumeration = Enumeration

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def _hasContent(self):
        if (
            self.Real is not None
            or self.Integer is not None
            or self.Boolean is not None
            or self.String is not None
            or self.Enumeration is not None
        ):
            return True
        else:
            return False


# end class fmi2SimpleType


class Boolean(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, Boolean)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if Boolean.subclass:
            return Boolean.subclass(*args_, **kwargs_)
        else:
            return Boolean(*args_, **kwargs_)

    factory = staticmethod(factory)

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class Boolean


class String(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, String)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if String.subclass:
            return String.subclass(*args_, **kwargs_)
        else:
            return String(*args_, **kwargs_)

    factory = staticmethod(factory)

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class String


class ModelExchangeType(GeneratedsSuper):
    """ModelExchangeType -- The FMU includes a model or the communication to a tool that provides a model. The environment provides the simulation engine for the model.
    List of capability flags that an FMI2 Model Exchange interface can provide
    modelIdentifier -- Short class name according to C-syntax, e.g. "A_B_C". Used as prefix for FMI2 functions if the functions are provided in C source code or in static libraries, but not if the functions are provided by a DLL/SharedObject. modelIdentifier is also used as name of the static library or DLL/SharedObject.
    needsExecutionTool -- If true, a tool is needed to execute the model and the FMU just contains the communication to this tool.
    SourceFiles -- List of source file names that are present in the "sources" directory of the FMU and need to be compiled in order to generate the binary of the FMU (only meaningful for source code FMUs).

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        modelIdentifier=None,
        needsExecutionTool=False,
        completedIntegratorStepNotNeeded=False,
        canBeInstantiatedOnlyOncePerProcess=False,
        canNotUseMemoryManagementFunctions=False,
        canGetAndSetFMUstate=False,
        canSerializeFMUstate=False,
        providesDirectionalDerivative=False,
        SourceFiles=None,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.modelIdentifier = _cast(None, modelIdentifier)
        self.needsExecutionTool = _cast(bool, needsExecutionTool)
        self.completedIntegratorStepNotNeeded = _cast(
            bool, completedIntegratorStepNotNeeded
        )
        self.canBeInstantiatedOnlyOncePerProcess = _cast(
            bool, canBeInstantiatedOnlyOncePerProcess
        )
        self.canNotUseMemoryManagementFunctions = _cast(
            bool, canNotUseMemoryManagementFunctions
        )
        self.canGetAndSetFMUstate = _cast(bool, canGetAndSetFMUstate)
        self.canSerializeFMUstate = _cast(bool, canSerializeFMUstate)
        self.providesDirectionalDerivative = _cast(bool, providesDirectionalDerivative)
        self.SourceFiles = SourceFiles

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, ModelExchangeType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if ModelExchangeType.subclass:
            return ModelExchangeType.subclass(*args_, **kwargs_)
        else:
            return ModelExchangeType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_SourceFiles(self):
        return self.SourceFiles

    def set_SourceFiles(self, SourceFiles):
        self.SourceFiles = SourceFiles

    def get_modelIdentifier(self):
        return self.modelIdentifier

    def set_modelIdentifier(self, modelIdentifier):
        self.modelIdentifier = modelIdentifier

    def get_needsExecutionTool(self):
        return self.needsExecutionTool

    def set_needsExecutionTool(self, needsExecutionTool):
        self.needsExecutionTool = needsExecutionTool

    def get_completedIntegratorStepNotNeeded(self):
        return self.completedIntegratorStepNotNeeded

    def set_completedIntegratorStepNotNeeded(self, completedIntegratorStepNotNeeded):
        self.completedIntegratorStepNotNeeded = completedIntegratorStepNotNeeded

    def get_canBeInstantiatedOnlyOncePerProcess(self):
        return self.canBeInstantiatedOnlyOncePerProcess

    def set_canBeInstantiatedOnlyOncePerProcess(
        self, canBeInstantiatedOnlyOncePerProcess
    ):
        self.canBeInstantiatedOnlyOncePerProcess = canBeInstantiatedOnlyOncePerProcess

    def get_canNotUseMemoryManagementFunctions(self):
        return self.canNotUseMemoryManagementFunctions

    def set_canNotUseMemoryManagementFunctions(
        self, canNotUseMemoryManagementFunctions
    ):
        self.canNotUseMemoryManagementFunctions = canNotUseMemoryManagementFunctions

    def get_canGetAndSetFMUstate(self):
        return self.canGetAndSetFMUstate

    def set_canGetAndSetFMUstate(self, canGetAndSetFMUstate):
        self.canGetAndSetFMUstate = canGetAndSetFMUstate

    def get_canSerializeFMUstate(self):
        return self.canSerializeFMUstate

    def set_canSerializeFMUstate(self, canSerializeFMUstate):
        self.canSerializeFMUstate = canSerializeFMUstate

    def get_providesDirectionalDerivative(self):
        return self.providesDirectionalDerivative

    def set_providesDirectionalDerivative(self, providesDirectionalDerivative):
        self.providesDirectionalDerivative = providesDirectionalDerivative

    def _hasContent(self):
        if self.SourceFiles is not None:
            return True
        else:
            return False


# end class ModelExchangeType


class SourceFilesType(GeneratedsSuper):
    """SourceFilesType -- List of source file names that are present in the "sources" directory of the FMU and need to be compiled in order to generate the binary of the FMU (only meaningful for source code FMUs)."""

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, File=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        if File is None:
            self.File = []
        else:
            self.File = File

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, SourceFilesType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if SourceFilesType.subclass:
            return SourceFilesType.subclass(*args_, **kwargs_)
        else:
            return SourceFilesType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_File(self):
        return self.File

    def set_File(self, File):
        self.File = File

    def add_File(self, value):
        self.File.append(value)

    def insert_File_at(self, index, value):
        self.File.insert(index, value)

    def replace_File_at(self, index, value):
        self.File[index] = value

    def _hasContent(self):
        if self.File:
            return True
        else:
            return False


# end class SourceFilesType


class FileType(GeneratedsSuper):
    """name -- Name of the file including the path relative to the sources directory, using the forward slash as separator (for example: name = "myFMU.c"; name = "modelExchange/solve.c")"""

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, name=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.name = _cast(None, name)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, FileType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if FileType.subclass:
            return FileType.subclass(*args_, **kwargs_)
        else:
            return FileType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class FileType


class CoSimulationType(GeneratedsSuper):
    """CoSimulationType -- The FMU includes a model and the simulation engine, or the communication to a tool that provides this. The environment provides the master algorithm for the Co-Simulation coupling.
    modelIdentifier -- Short class name according to C-syntax, e.g. "A_B_C". Used as prefix for FMI2 functions if the functions are provided in C source code or in static libraries, but not if the functions are provided by a DLL/SharedObject. modelIdentifier is also used as name of the static library or DLL/SharedObject.
    needsExecutionTool -- If true, a tool is needed to execute the model and the FMU just contains the communication to this tool.
    providesDirectionalDerivative -- Directional derivatives at communication points
    SourceFiles -- List of source file names that are present in the "sources" directory of the FMU and need to be compiled in order to generate the binary of the FMU (only meaningful for source code FMUs).

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        modelIdentifier=None,
        needsExecutionTool=False,
        canHandleVariableCommunicationStepSize=False,
        canInterpolateInputs=False,
        maxOutputDerivativeOrder=0,
        canRunAsynchronuously=False,
        canBeInstantiatedOnlyOncePerProcess=False,
        canNotUseMemoryManagementFunctions=False,
        canGetAndSetFMUstate=False,
        canSerializeFMUstate=False,
        providesDirectionalDerivative=False,
        SourceFiles=None,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.modelIdentifier = _cast(None, modelIdentifier)
        self.needsExecutionTool = _cast(bool, needsExecutionTool)
        self.canHandleVariableCommunicationStepSize = _cast(
            bool, canHandleVariableCommunicationStepSize
        )
        self.canInterpolateInputs = _cast(bool, canInterpolateInputs)
        self.maxOutputDerivativeOrder = _cast(int, maxOutputDerivativeOrder)
        self.canRunAsynchronuously = _cast(bool, canRunAsynchronuously)
        self.canBeInstantiatedOnlyOncePerProcess = _cast(
            bool, canBeInstantiatedOnlyOncePerProcess
        )
        self.canNotUseMemoryManagementFunctions = _cast(
            bool, canNotUseMemoryManagementFunctions
        )
        self.canGetAndSetFMUstate = _cast(bool, canGetAndSetFMUstate)
        self.canSerializeFMUstate = _cast(bool, canSerializeFMUstate)
        self.providesDirectionalDerivative = _cast(bool, providesDirectionalDerivative)
        self.SourceFiles = SourceFiles

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, CoSimulationType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if CoSimulationType.subclass:
            return CoSimulationType.subclass(*args_, **kwargs_)
        else:
            return CoSimulationType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_SourceFiles(self):
        return self.SourceFiles

    def set_SourceFiles(self, SourceFiles):
        self.SourceFiles = SourceFiles

    def get_modelIdentifier(self):
        return self.modelIdentifier

    def set_modelIdentifier(self, modelIdentifier):
        self.modelIdentifier = modelIdentifier

    def get_needsExecutionTool(self):
        return self.needsExecutionTool

    def set_needsExecutionTool(self, needsExecutionTool):
        self.needsExecutionTool = needsExecutionTool

    def get_canHandleVariableCommunicationStepSize(self):
        return self.canHandleVariableCommunicationStepSize

    def set_canHandleVariableCommunicationStepSize(
        self, canHandleVariableCommunicationStepSize
    ):
        self.canHandleVariableCommunicationStepSize = (
            canHandleVariableCommunicationStepSize
        )

    def get_canInterpolateInputs(self):
        return self.canInterpolateInputs

    def set_canInterpolateInputs(self, canInterpolateInputs):
        self.canInterpolateInputs = canInterpolateInputs

    def get_maxOutputDerivativeOrder(self):
        return self.maxOutputDerivativeOrder

    def set_maxOutputDerivativeOrder(self, maxOutputDerivativeOrder):
        self.maxOutputDerivativeOrder = maxOutputDerivativeOrder

    def get_canRunAsynchronuously(self):
        return self.canRunAsynchronuously

    def set_canRunAsynchronuously(self, canRunAsynchronuously):
        self.canRunAsynchronuously = canRunAsynchronuously

    def get_canBeInstantiatedOnlyOncePerProcess(self):
        return self.canBeInstantiatedOnlyOncePerProcess

    def set_canBeInstantiatedOnlyOncePerProcess(
        self, canBeInstantiatedOnlyOncePerProcess
    ):
        self.canBeInstantiatedOnlyOncePerProcess = canBeInstantiatedOnlyOncePerProcess

    def get_canNotUseMemoryManagementFunctions(self):
        return self.canNotUseMemoryManagementFunctions

    def set_canNotUseMemoryManagementFunctions(
        self, canNotUseMemoryManagementFunctions
    ):
        self.canNotUseMemoryManagementFunctions = canNotUseMemoryManagementFunctions

    def get_canGetAndSetFMUstate(self):
        return self.canGetAndSetFMUstate

    def set_canGetAndSetFMUstate(self, canGetAndSetFMUstate):
        self.canGetAndSetFMUstate = canGetAndSetFMUstate

    def get_canSerializeFMUstate(self):
        return self.canSerializeFMUstate

    def set_canSerializeFMUstate(self, canSerializeFMUstate):
        self.canSerializeFMUstate = canSerializeFMUstate

    def get_providesDirectionalDerivative(self):
        return self.providesDirectionalDerivative

    def set_providesDirectionalDerivative(self, providesDirectionalDerivative):
        self.providesDirectionalDerivative = providesDirectionalDerivative

    def _hasContent(self):
        if self.SourceFiles is not None:
            return True
        else:
            return False


# end class CoSimulationType


class SourceFilesType1(GeneratedsSuper):
    """SourceFilesType1 -- List of source file names that are present in the "sources" directory of the FMU and need to be compiled in order to generate the binary of the FMU (only meaningful for source code FMUs)."""

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, File=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        if File is None:
            self.File = []
        else:
            self.File = File

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, SourceFilesType1)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if SourceFilesType1.subclass:
            return SourceFilesType1.subclass(*args_, **kwargs_)
        else:
            return SourceFilesType1(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_File(self):
        return self.File

    def set_File(self, File):
        self.File = File

    def add_File(self, value):
        self.File.append(value)

    def insert_File_at(self, index, value):
        self.File.insert(index, value)

    def replace_File_at(self, index, value):
        self.File[index] = value

    def _hasContent(self):
        if self.File:
            return True
        else:
            return False


# end class SourceFilesType1


class FileType2(GeneratedsSuper):
    """name -- Name of the file including the path relative to the sources directory, using the forward slash as separator (for example: name = "myFMU.c"; name = "coSimulation/solve.c")"""

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, name=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.name = _cast(None, name)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, FileType2)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if FileType2.subclass:
            return FileType2.subclass(*args_, **kwargs_)
        else:
            return FileType2(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class FileType2


class UnitDefinitionsType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, Unit=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        if Unit is None:
            self.Unit = []
        else:
            self.Unit = Unit

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, UnitDefinitionsType
            )
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if UnitDefinitionsType.subclass:
            return UnitDefinitionsType.subclass(*args_, **kwargs_)
        else:
            return UnitDefinitionsType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_Unit(self):
        return self.Unit

    def set_Unit(self, Unit):
        self.Unit = Unit

    def add_Unit(self, value):
        self.Unit.append(value)

    def insert_Unit_at(self, index, value):
        self.Unit.insert(index, value)

    def replace_Unit_at(self, index, value):
        self.Unit[index] = value

    def _hasContent(self):
        if self.Unit:
            return True
        else:
            return False


# end class UnitDefinitionsType


class TypeDefinitionsType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, SimpleType=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        if SimpleType is None:
            self.SimpleType = []
        else:
            self.SimpleType = SimpleType

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, TypeDefinitionsType
            )
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if TypeDefinitionsType.subclass:
            return TypeDefinitionsType.subclass(*args_, **kwargs_)
        else:
            return TypeDefinitionsType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_SimpleType(self):
        return self.SimpleType

    def set_SimpleType(self, SimpleType):
        self.SimpleType = SimpleType

    def add_SimpleType(self, value):
        self.SimpleType.append(value)

    def insert_SimpleType_at(self, index, value):
        self.SimpleType.insert(index, value)

    def replace_SimpleType_at(self, index, value):
        self.SimpleType[index] = value

    def _hasContent(self):
        if self.SimpleType:
            return True
        else:
            return False


# end class TypeDefinitionsType


class LogCategoriesType(GeneratedsSuper):
    """LogCategoriesType -- Log categories available in FMU"""

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, Category=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        if Category is None:
            self.Category = []
        else:
            self.Category = Category

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, LogCategoriesType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if LogCategoriesType.subclass:
            return LogCategoriesType.subclass(*args_, **kwargs_)
        else:
            return LogCategoriesType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_Category(self):
        return self.Category

    def set_Category(self, Category):
        self.Category = Category

    def add_Category(self, value):
        self.Category.append(value)

    def insert_Category_at(self, index, value):
        self.Category.insert(index, value)

    def replace_Category_at(self, index, value):
        self.Category[index] = value

    def _hasContent(self):
        if self.Category:
            return True
        else:
            return False


# end class LogCategoriesType


class CategoryType(GeneratedsSuper):
    """name -- Name of Category element. "name" must be unique with respect to all other elements of the LogCategories list. Standardized names: "logEvents", "logSingularLinearSystems", "logNonlinearSystems", "logDynamicStateSelection", "logStatusWarning", "logStatusDiscard", "logStatusError", "logStatusFatal", "logStatusPending", "logAll"
    description -- Description of the log category

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, name=None, description=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.name = _cast(None, name)
        self.description = _cast(None, description)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, CategoryType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if CategoryType.subclass:
            return CategoryType.subclass(*args_, **kwargs_)
        else:
            return CategoryType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class CategoryType


class DefaultExperimentType(GeneratedsSuper):
    """startTime -- Default start time of simulation
    stopTime -- Default stop time of simulation
    tolerance -- Default relative integration tolerance
    stepSize -- ModelExchange: Default step size for fixed step integrators.
    CoSimulation: Preferred communicationStepSize.

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        startTime=None,
        stopTime=None,
        tolerance=None,
        stepSize=None,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.startTime = _cast(float, startTime)
        self.stopTime = _cast(float, stopTime)
        self.tolerance = _cast(float, tolerance)
        self.stepSize = _cast(float, stepSize)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, DefaultExperimentType
            )
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if DefaultExperimentType.subclass:
            return DefaultExperimentType.subclass(*args_, **kwargs_)
        else:
            return DefaultExperimentType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_startTime(self):
        return self.startTime

    def set_startTime(self, startTime):
        self.startTime = startTime

    def get_stopTime(self):
        return self.stopTime

    def set_stopTime(self, stopTime):
        self.stopTime = stopTime

    def get_tolerance(self):
        return self.tolerance

    def set_tolerance(self, tolerance):
        self.tolerance = tolerance

    def get_stepSize(self):
        return self.stepSize

    def set_stepSize(self, stepSize):
        self.stepSize = stepSize

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class DefaultExperimentType


class ModelVariablesType(GeneratedsSuper):
    """ModelVariablesType -- Ordered list of all variables (first definition has index = 1)."""

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, ScalarVariable=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        if ScalarVariable is None:
            self.ScalarVariable = []
        else:
            self.ScalarVariable = ScalarVariable

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, ModelVariablesType
            )
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if ModelVariablesType.subclass:
            return ModelVariablesType.subclass(*args_, **kwargs_)
        else:
            return ModelVariablesType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_ScalarVariable(self):
        return self.ScalarVariable

    def set_ScalarVariable(self, ScalarVariable):
        self.ScalarVariable = ScalarVariable

    def add_ScalarVariable(self, value):
        self.ScalarVariable.append(value)

    def insert_ScalarVariable_at(self, index, value):
        self.ScalarVariable.insert(index, value)

    def replace_ScalarVariable_at(self, index, value):
        self.ScalarVariable[index] = value

    def _hasContent(self):
        if self.ScalarVariable:
            return True
        else:
            return False


# end class ModelVariablesType


class ModelStructureType(GeneratedsSuper):
    """ModelStructureType -- Ordered lists of outputs, exposed state derivatives,
    and the initial unknowns. Optionally, the functional
    dependency of these variables can be defined.
    Outputs -- Ordered list of all outputs. Exactly all variables with causality="output" must be in this list. The dependency definition holds for Continuous-Time and for Event Mode (ModelExchange) and for Communication Points (CoSimulation).
    Derivatives -- Ordered list of all exposed state derivatives (and therefore implicitely associated continuous-time states). Exactly all state derivatives of a ModelExchange FMU must be in this list. A CoSimulation FMU need not expose its state derivatives. If a model has dynamic state selection, introduce dummy state variables. The dependency definition holds for Continuous-Time and for Event Mode (ModelExchange) and for Communication Points (CoSimulation).
    InitialUnknowns -- Ordered list of all exposed Unknowns in Initialization Mode. This list consists of all variables with (1) causality = "output" and (initial="approx" or calculated"), (2) causality = "calculatedParameter", and (3) all continuous-time states and all state derivatives (defined with element Derivatives from ModelStructure)with initial=("approx" or "calculated"). The resulting list is not allowed to have duplicates (e.g. if a state is also an output, it is included only once in the list). The Unknowns in this list must be ordered according to their ScalarVariable index (e.g. if for two variables A and B the  ScalarVariable index of A is less than the index of B, then A must appear before B in InitialUnknowns).

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        Outputs=None,
        Derivatives=None,
        InitialUnknowns=None,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.Outputs = Outputs
        self.Derivatives = Derivatives
        self.InitialUnknowns = InitialUnknowns

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, ModelStructureType
            )
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if ModelStructureType.subclass:
            return ModelStructureType.subclass(*args_, **kwargs_)
        else:
            return ModelStructureType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_Outputs(self):
        return self.Outputs

    def set_Outputs(self, Outputs):
        self.Outputs = Outputs

    def get_Derivatives(self):
        return self.Derivatives

    def set_Derivatives(self, Derivatives):
        self.Derivatives = Derivatives

    def get_InitialUnknowns(self):
        return self.InitialUnknowns

    def set_InitialUnknowns(self, InitialUnknowns):
        self.InitialUnknowns = InitialUnknowns

    def _hasContent(self):
        if (
            self.Outputs is not None
            or self.Derivatives is not None
            or self.InitialUnknowns is not None
        ):
            return True
        else:
            return False


# end class ModelStructureType


class InitialUnknownsType(GeneratedsSuper):
    """InitialUnknownsType -- Ordered list of all exposed Unknowns in Initialization Mode. This list consists of all variables with (1) causality = "output" and (initial="approx" or calculated"), (2) causality = "calculatedParameter", and (3) all continuous-time states and all state derivatives (defined with element Derivatives from ModelStructure)with initial=("approx" or "calculated"). The resulting list is not allowed to have duplicates (e.g. if a state is also an output, it is included only once in the list). The Unknowns in this list must be ordered according to their ScalarVariable index (e.g. if for two variables A and B the  ScalarVariable index of A is less than the index of B, then A must appear before B in InitialUnknowns).
    Unknown -- Dependency of scalar Unknown from Knowns:
    Unknown=f(Known_1, Known_2, ...).
    The Knowns are "inputs",
    "variables with initial=exact", and
    "independent variable".

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, Unknown=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        if Unknown is None:
            self.Unknown = []
        else:
            self.Unknown = Unknown

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, InitialUnknownsType
            )
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if InitialUnknownsType.subclass:
            return InitialUnknownsType.subclass(*args_, **kwargs_)
        else:
            return InitialUnknownsType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_Unknown(self):
        return self.Unknown

    def set_Unknown(self, Unknown):
        self.Unknown = Unknown

    def add_Unknown(self, value):
        self.Unknown.append(value)

    def insert_Unknown_at(self, index, value):
        self.Unknown.insert(index, value)

    def replace_Unknown_at(self, index, value):
        self.Unknown[index] = value

    def _hasContent(self):
        if self.Unknown:
            return True
        else:
            return False


# end class InitialUnknownsType


class UnknownType(GeneratedsSuper):
    """UnknownType -- Dependency of scalar Unknown from Knowns:
    Unknown=f(Known_1, Known_2, ...).
    The Knowns are "inputs",
    "variables with initial=exact", and
    "independent variable".
    index -- ScalarVariable index of Unknown
    dependencies -- Defines the dependency of the Unknown (directly or indirectly via auxiliary variables) on the Knowns in the Initialization Mode. If not present, it must be assumed that the Unknown depends on all Knowns. If present as empty list, the Unknown depends on none of the Knowns. Otherwise the Unknown depends on the Knowns defined by the given ScalarVariable indices. The indices are ordered according to size, starting with the smallest index.
    dependenciesKind -- If not present, it must be assumed that the Unknown depends on the Knowns without a particular structure. Otherwise, the corresponding Known v enters the equation as:
    = "dependent": no particular structure, f(v)
    = "constant"   : constant factor, c*v (only for Real variables)
    If "dependenciesKind" is present, "dependencies" must be present and must have the same number of list elements.

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        index=None,
        dependencies=None,
        dependenciesKind=None,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.index = _cast(int, index)
        self.dependencies = dependencies
        self.dependenciesKind = dependenciesKind

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, UnknownType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if UnknownType.subclass:
            return UnknownType.subclass(*args_, **kwargs_)
        else:
            return UnknownType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

    def get_dependencies(self):
        return self.dependencies

    def set_dependencies(self, dependencies):
        self.dependencies = dependencies

    def get_dependenciesKind(self):
        return self.dependenciesKind

    def set_dependenciesKind(self, dependenciesKind):
        self.dependenciesKind = dependenciesKind

    def validate_dependenciesType(self, value):
        # Validate type dependenciesType, a restriction on xs:unsignedInt.
        pass

    def validate_dependenciesKindType(self, value):
        # Validate type dependenciesKindType, a restriction on xs:normalizedString.
        pass

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class UnknownType


class RealType(GeneratedsSuper):
    """declaredType -- If present, name of type defined with TypeDefinitions / SimpleType providing defaults.
    start -- Value before initialization, if initial=exact or approx.
    max
    >
    = start
    >
    = min required
    derivative -- If present, this variable is the derivative of variable with ScalarVariable index "derivative".
    reinit -- Only for ModelExchange and if variable is a continuous-time state:
    If true, state can be reinitialized at an event by the FMU
    If false, state will never be reinitialized at an event by the FMU

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        declaredType=None,
        start=None,
        derivative=None,
        reinit=False,
        quantity=None,
        unit=None,
        displayUnit=None,
        relativeQuantity=False,
        min=None,
        max=None,
        nominal=None,
        unbounded=False,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.declaredType = _cast(None, declaredType)
        self.start = _cast(float, start)
        self.derivative = _cast(int, derivative)
        self.reinit = _cast(bool, reinit)
        self.quantity = _cast(None, quantity)
        self.unit = _cast(None, unit)
        self.displayUnit = _cast(None, displayUnit)
        self.relativeQuantity = _cast(bool, relativeQuantity)
        self.min = _cast(float, min)
        self.max = _cast(float, max)
        self.nominal = _cast(float, nominal)
        self.unbounded = _cast(bool, unbounded)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, RealType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if RealType.subclass:
            return RealType.subclass(*args_, **kwargs_)
        else:
            return RealType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_declaredType(self):
        return self.declaredType

    def set_declaredType(self, declaredType):
        self.declaredType = declaredType

    def get_start(self):
        return self.start

    def set_start(self, start):
        self.start = start

    def get_derivative(self):
        return self.derivative

    def set_derivative(self, derivative):
        self.derivative = derivative

    def get_reinit(self):
        return self.reinit

    def set_reinit(self, reinit):
        self.reinit = reinit

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity):
        self.quantity = quantity

    def get_unit(self):
        return self.unit

    def set_unit(self, unit):
        self.unit = unit

    def get_displayUnit(self):
        return self.displayUnit

    def set_displayUnit(self, displayUnit):
        self.displayUnit = displayUnit

    def get_relativeQuantity(self):
        return self.relativeQuantity

    def set_relativeQuantity(self, relativeQuantity):
        self.relativeQuantity = relativeQuantity

    def get_min(self):
        return self.min

    def set_min(self, min):
        self.min = min

    def get_max(self):
        return self.max

    def set_max(self, max):
        self.max = max

    def get_nominal(self):
        return self.nominal

    def set_nominal(self, nominal):
        self.nominal = nominal

    def get_unbounded(self):
        return self.unbounded

    def set_unbounded(self, unbounded):
        self.unbounded = unbounded

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class RealType


class IntegerType(GeneratedsSuper):
    """declaredType -- If present, name of type defined with TypeDefinitions / SimpleType providing defaults.
    start -- Value before initialization, if initial=exact or approx.
    max
    >
    = start
    >
    = min required

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        declaredType=None,
        start=None,
        quantity=None,
        min=None,
        max=None,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.declaredType = _cast(None, declaredType)
        self.start = _cast(int, start)
        self.quantity = _cast(None, quantity)
        self.min = _cast(int, min)
        self.max = _cast(int, max)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, IntegerType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if IntegerType.subclass:
            return IntegerType.subclass(*args_, **kwargs_)
        else:
            return IntegerType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_declaredType(self):
        return self.declaredType

    def set_declaredType(self, declaredType):
        self.declaredType = declaredType

    def get_start(self):
        return self.start

    def set_start(self, start):
        self.start = start

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity):
        self.quantity = quantity

    def get_min(self):
        return self.min

    def set_min(self, min):
        self.min = min

    def get_max(self):
        return self.max

    def set_max(self, max):
        self.max = max

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class IntegerType


class BooleanType(GeneratedsSuper):
    """declaredType -- If present, name of type defined with TypeDefinitions / SimpleType providing defaults.
    start -- Value before initialization, if initial=exact or approx

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, declaredType=None, start=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.declaredType = _cast(None, declaredType)
        self.start = _cast(bool, start)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, BooleanType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if BooleanType.subclass:
            return BooleanType.subclass(*args_, **kwargs_)
        else:
            return BooleanType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_declaredType(self):
        return self.declaredType

    def set_declaredType(self, declaredType):
        self.declaredType = declaredType

    def get_start(self):
        return self.start

    def set_start(self, start):
        self.start = start

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class BooleanType


class StringType(GeneratedsSuper):
    """declaredType -- If present, name of type defined with TypeDefinitions / SimpleType providing defaults.
    start -- Value before initialization, if initial=exact or approx

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, declaredType=None, start=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.declaredType = _cast(None, declaredType)
        self.start = _cast(None, start)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, StringType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if StringType.subclass:
            return StringType.subclass(*args_, **kwargs_)
        else:
            return StringType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_declaredType(self):
        return self.declaredType

    def set_declaredType(self, declaredType):
        self.declaredType = declaredType

    def get_start(self):
        return self.start

    def set_start(self, start):
        self.start = start

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class StringType


class EnumerationType(GeneratedsSuper):
    """declaredType -- Name of type defined with TypeDefinitions / SimpleType
    max -- max
    >
    = min required
    start -- Value before initialization, if initial=exact or approx.
    max
    >
    = start
    >
    = min required

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        declaredType=None,
        quantity=None,
        min=None,
        max=None,
        start=None,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.declaredType = _cast(None, declaredType)
        self.quantity = _cast(None, quantity)
        self.min = _cast(int, min)
        self.max = _cast(int, max)
        self.start = _cast(int, start)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, EnumerationType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if EnumerationType.subclass:
            return EnumerationType.subclass(*args_, **kwargs_)
        else:
            return EnumerationType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_declaredType(self):
        return self.declaredType

    def set_declaredType(self, declaredType):
        self.declaredType = declaredType

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity):
        self.quantity = quantity

    def get_min(self):
        return self.min

    def set_min(self, min):
        self.min = min

    def get_max(self):
        return self.max

    def set_max(self, max):
        self.max = max

    def get_start(self):
        return self.start

    def set_start(self, start):
        self.start = start

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class EnumerationType


class ToolType(GeneratedsSuper):
    """ToolType -- Tool specific annotation (ignored by other tools).
    name -- Name of tool that can interpret the annotation. "name" must be unique with respect to all other elements of the VendorAnnotation list.

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, name=None, anytypeobjs_=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.name = _cast(None, name)
        self.anytypeobjs_ = anytypeobjs_

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, ToolType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if ToolType.subclass:
            return ToolType.subclass(*args_, **kwargs_)
        else:
            return ToolType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_anytypeobjs_(self):
        return self.anytypeobjs_

    def set_anytypeobjs_(self, anytypeobjs_):
        self.anytypeobjs_ = anytypeobjs_

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def _hasContent(self):
        if self.anytypeobjs_ is not None:
            return True
        else:
            return False


# end class ToolType


class UnknownType3(GeneratedsSuper):
    """UnknownType3 -- Dependency of scalar Unknown from Knowns
    in Continuous-Time and Event Mode (ModelExchange),
    and at Communication Points (CoSimulation):
    Unknown=f(Known_1, Known_2, ...).
    The Knowns are "inputs", "continuous states" and
    "independent variable" (usually time)".
    index -- ScalarVariable index of Unknown
    dependencies -- Defines the dependency of the Unknown (directly or indirectly via auxiliary variables) on the Knowns in Continuous-Time and Event Mode (ModelExchange) and at Communication Points (CoSimulation). If not present, it must be assumed that the Unknown depends on all Knowns. If present as empty list, the Unknown depends on none of the Knowns. Otherwise the Unknown depends on the Knowns defined by the given ScalarVariable indices. The indices are ordered according to size, starting with the smallest index.
    dependenciesKind -- If not present, it must be assumed that the Unknown depends on the Knowns without a particular structure. Otherwise, the corresponding Known v enters the equation as:
    = "dependent": no particular structure, f(v)
    = "constant"   : constant factor, c*v (only for Real variablse)
    = "fixed"        : fixed factor, p*v (only for Real variables)
    = "tunable"    : tunable factor, p*v (only for Real variables)
    = "discrete"    : discrete factor, d*v (only for Real variables)
    If "dependenciesKind" is present, "dependencies" must be present and must have the same number of list elements.

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        index=None,
        dependencies=None,
        dependenciesKind=None,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.index = _cast(int, index)
        self.dependencies = dependencies
        self.dependenciesKind = dependenciesKind

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, UnknownType3)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if UnknownType3.subclass:
            return UnknownType3.subclass(*args_, **kwargs_)
        else:
            return UnknownType3(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

    def get_dependencies(self):
        return self.dependencies

    def set_dependencies(self, dependencies):
        self.dependencies = dependencies

    def get_dependenciesKind(self):
        return self.dependenciesKind

    def set_dependenciesKind(self, dependenciesKind):
        self.dependenciesKind = dependenciesKind

    def validate_dependenciesType4(self, value):
        # Validate type dependenciesType4, a restriction on xs:unsignedInt.
        pass

    def validate_dependenciesKindType5(self, value):
        # Validate type dependenciesKindType5, a restriction on xs:normalizedString.
        pass

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class UnknownType3


class BaseUnitType(GeneratedsSuper):
    """BaseUnitType -- BaseUnit_value = factor*Unit_value + offset
    kg -- Exponent of SI base unit "kg"
    m -- Exponent of SI base unit "m"
    s -- Exponent of SI base unit "s"
    A -- Exponent of SI base unit "A"
    K -- Exponent of SI base unit "K"
    mol -- Exponent of SI base unit "mol"
    cd -- Exponent of SI base unit "cd"
    rad -- Exponent of SI derived unit "rad"

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        kg=0,
        m=0,
        s=0,
        A=0,
        K=0,
        mol=0,
        cd=0,
        rad=0,
        factor=1,
        offset=0,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.kg = _cast(int, kg)
        self.m = _cast(int, m)
        self.s = _cast(int, s)
        self.A = _cast(int, A)
        self.K = _cast(int, K)
        self.mol = _cast(int, mol)
        self.cd = _cast(int, cd)
        self.rad = _cast(int, rad)
        self.factor = _cast(float, factor)
        self.offset = _cast(float, offset)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, BaseUnitType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if BaseUnitType.subclass:
            return BaseUnitType.subclass(*args_, **kwargs_)
        else:
            return BaseUnitType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_kg(self):
        return self.kg

    def set_kg(self, kg):
        self.kg = kg

    def get_m(self):
        return self.m

    def set_m(self, m):
        self.m = m

    def get_s(self):
        return self.s

    def set_s(self, s):
        self.s = s

    def get_A(self):
        return self.A

    def set_A(self, A):
        self.A = A

    def get_K(self):
        return self.K

    def set_K(self, K):
        self.K = K

    def get_mol(self):
        return self.mol

    def set_mol(self, mol):
        self.mol = mol

    def get_cd(self):
        return self.cd

    def set_cd(self, cd):
        self.cd = cd

    def get_rad(self):
        return self.rad

    def set_rad(self, rad):
        self.rad = rad

    def get_factor(self):
        return self.factor

    def set_factor(self, factor):
        self.factor = factor

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class BaseUnitType


class DisplayUnitType(GeneratedsSuper):
    """DisplayUnitType -- DisplayUnit_value = factor*Unit_value + offset
    name -- Name of DisplayUnit element, e.g.
    ,
    . "name" must be unique with respect to all other "names" of the DisplayUnit definitions of the same Unit (different Unit elements may have the same DisplayUnit names).

    """

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, name=None, factor=1, offset=0, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.name = _cast(None, name)
        self.factor = _cast(float, factor)
        self.offset = _cast(float, offset)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, DisplayUnitType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if DisplayUnitType.subclass:
            return DisplayUnitType.subclass(*args_, **kwargs_)
        else:
            return DisplayUnitType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_factor(self):
        return self.factor

    def set_factor(self, factor):
        self.factor = factor

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class DisplayUnitType


class RealType6(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self,
        quantity=None,
        unit=None,
        displayUnit=None,
        relativeQuantity=False,
        min=None,
        max=None,
        nominal=None,
        unbounded=False,
        gds_collector_=None,
        **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.quantity = _cast(None, quantity)
        self.unit = _cast(None, unit)
        self.displayUnit = _cast(None, displayUnit)
        self.relativeQuantity = _cast(bool, relativeQuantity)
        self.min = _cast(float, min)
        self.max = _cast(float, max)
        self.nominal = _cast(float, nominal)
        self.unbounded = _cast(bool, unbounded)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, RealType6)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if RealType6.subclass:
            return RealType6.subclass(*args_, **kwargs_)
        else:
            return RealType6(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity):
        self.quantity = quantity

    def get_unit(self):
        return self.unit

    def set_unit(self, unit):
        self.unit = unit

    def get_displayUnit(self):
        return self.displayUnit

    def set_displayUnit(self, displayUnit):
        self.displayUnit = displayUnit

    def get_relativeQuantity(self):
        return self.relativeQuantity

    def set_relativeQuantity(self, relativeQuantity):
        self.relativeQuantity = relativeQuantity

    def get_min(self):
        return self.min

    def set_min(self, min):
        self.min = min

    def get_max(self):
        return self.max

    def set_max(self, max):
        self.max = max

    def get_nominal(self):
        return self.nominal

    def set_nominal(self, nominal):
        self.nominal = nominal

    def get_unbounded(self):
        return self.unbounded

    def set_unbounded(self, unbounded):
        self.unbounded = unbounded

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class RealType6


class IntegerType7(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self, quantity=None, min=None, max=None, gds_collector_=None, **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.quantity = _cast(None, quantity)
        self.min = _cast(int, min)
        self.max = _cast(int, max)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, IntegerType7)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if IntegerType7.subclass:
            return IntegerType7.subclass(*args_, **kwargs_)
        else:
            return IntegerType7(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity):
        self.quantity = quantity

    def get_min(self):
        return self.min

    def set_min(self, min):
        self.min = min

    def get_max(self):
        return self.max

    def set_max(self, max):
        self.max = max

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class IntegerType7


class EnumerationType8(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(self, quantity=None, Item=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.quantity = _cast(None, quantity)
        if Item is None:
            self.Item = []
        else:
            self.Item = Item

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, EnumerationType8)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if EnumerationType8.subclass:
            return EnumerationType8.subclass(*args_, **kwargs_)
        else:
            return EnumerationType8(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_Item(self):
        return self.Item

    def set_Item(self, Item):
        self.Item = Item

    def add_Item(self, value):
        self.Item.append(value)

    def insert_Item_at(self, index, value):
        self.Item.insert(index, value)

    def replace_Item_at(self, index, value):
        self.Item[index] = value

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity):
        self.quantity = quantity

    def _hasContent(self):
        if self.Item:
            return True
        else:
            return False


# end class EnumerationType8


class ItemType(GeneratedsSuper):
    """value -- Must be a unique number in the same enumeration"""

    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None

    def __init__(
        self, name=None, value=None, description=None, gds_collector_=None, **kwargs_
    ):
        self.gds_collector_ = gds_collector_
        self.name = _cast(None, name)
        self.value = _cast(int, value)
        self.description = _cast(None, description)

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(CurrentSubclassModule_, ItemType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if ItemType.subclass:
            return ItemType.subclass(*args_, **kwargs_)
        else:
            return ItemType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def _hasContent(self):
        if ():
            return True
        else:
            return False


# end class ItemType

GDSClassesMapping = {}

RenameMappings_ = {}

#
# Mapping of namespaces to types defined in them
# and the file in which each is defined.
# simpleTypes are marked "ST" and complexTypes "CT".
NamespaceToDefMappings_ = {}

__all__ = [
    "BaseUnitType",
    "Boolean",
    "BooleanType",
    "CategoryType",
    "CoSimulationType",
    "DefaultExperimentType",
    "DisplayUnitType",
    "EnumerationType",
    "EnumerationType8",
    "FileType",
    "FileType2",
    "InitialUnknownsType",
    "IntegerType",
    "IntegerType7",
    "ItemType",
    "LogCategoriesType",
    "ModelExchangeType",
    "ModelStructureType",
    "ModelVariablesType",
    "RealType",
    "RealType6",
    "SourceFilesType",
    "SourceFilesType1",
    "String",
    "StringType",
    "ToolType",
    "TypeDefinitionsType",
    "UnitDefinitionsType",
    "UnknownType",
    "UnknownType3",
    "fmi2Annotation",
    "fmi2ScalarVariable",
    "fmi2SimpleType",
    "fmi2Unit",
    "fmi2VariableDependency",
    "fmiModelDescription",
]
