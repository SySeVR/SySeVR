#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013-2014, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
An implementation of URIs from RFC 3986 (URI Generic Syntax).

See: http://www.ietf.org/rfc/rfc3986.txt
"""


from __future__ import unicode_literals

import re
try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote, unquote

from .kvlist import KeyValueList
from .util import bstr, ustr, xstr


__all__ = ["general_delimiters", "subcomponent_delimiters",
           "reserved", "unreserved", "percent_encode", "percent_decode",
           "ParameterString", "Authority", "Path", "Query", "URI"]


# RFC 3986 § 2.2.
general_delimiters = ":/?#[]@"
subcomponent_delimiters = "!$&'()*+,;="
reserved = general_delimiters + subcomponent_delimiters

# RFC 3986 § 2.3.
unreserved = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
              "abcdefghijklmnopqrstuvwxyz"
              "0123456789-._~")


# RFC 3986 § 2.1.
def percent_encode(data, safe=None):
    """ Percent encode a string of data, optionally keeping certain characters
    unencoded.

    """
    if data is None:
        return None
    if isinstance(data, (tuple, list, set)):
        return "&".join(
            percent_encode(value, safe=safe)
            for value in data
        )
    if isinstance(data, dict):
        return "&".join(
            key + "=" + percent_encode(value, safe=safe)
            for key, value in data.items()
        )
    return quote(bstr(data), safe or b"")


def percent_decode(data):
    """ Percent decode a string of data.

    """
    if data is None:
        return None
    return unquote(xstr(data))


class Part(object):
    """ Internal base class for all URI component parts.
    """

    @classmethod
    def _cast(cls, obj):
        """ Convert the object supplied to an instance of this class, if
        possible.
        """
        if obj is None:
            return cls(None)
        elif isinstance(obj, cls):
            return obj
        else:
            return cls(ustr(obj))

    def __init__(self):
        pass

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, repr(self.string))

    def __str__(self):
        return self.string or ""

    def __eq__(self, other):
        if other is None:
            return self.string is None
        try:
            other_string = other.string
        except AttributeError:
            other_string = self._cast(other).string
        return self.string == other_string

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return bool(self.string)

    def __nonzero__(self):
        return bool(self.string)

    def __len__(self):
        return len(ustr(self))

    def __iter__(self):
        return iter(self.string)

    @property
    def string(self):
        raise NotImplementedError()


class ParameterString(Part):

    __string = NotImplemented

    def __init__(self, string, separator):
        super(ParameterString, self).__init__()
        self.__separator = separator
        self.__none = string is None
        self.__parameters = KeyValueList()
        if string:
            bits = string.split(self.__separator)
            for bit in bits:
                if "=" in bit:
                    key, value = map(percent_decode, bit.partition("=")[0::2])
                else:
                    key, value = percent_decode(bit), None
                self.__parameters.append(key, value)

    def __len__(self):
        return self.__parameters.__len__()

    def __bool__(self):
        return bool(self.__parameters)

    def __nonzero__(self):
        return bool(self.__parameters)

    def __contains__(self, item):
        return self.__parameters.__contains__(item)

    def __hash__(self):
        return hash(self.string)

    def __iter__(self):
        return self.__parameters.__iter__()

    def __getitem__(self, index):
        if isinstance(index, slice):
            out = ParameterString("", self.__separator)
            out.__parameters.extend(self.__parameters.__getitem__(index))
            return out
        else:
            return self.__parameters.__getitem__(index)

    def __getslice__(self, start, stop):
        out = ParameterString("", self.__separator)
        out.__parameters.extend(self.__parameters.__getslice__(start, stop))
        return out

    def get(self, name, index=0):
        if not self.__parameters.has_key(name):
            raise KeyError(name)
        for i, value in enumerate(self.__parameters.get(name)):
            if i == index:
                return value
        raise IndexError("Parameter {0} does not have {1} "
                         "values".format(name, index))

    def get_all(self, name):
        if not self.__parameters.has_key(name):
            raise KeyError(name)
        return list(self.__parameters.get(name))

    @property
    def string(self):
        if self.__string is NotImplemented:
            if self.__none:
                self.__string = None
            else:
                bits = []
                for key, value in self.__parameters:
                    if value is None:
                        bits.append(percent_encode(key))
                    else:
                        bits.append(percent_encode(key) + "=" + percent_encode(value))
                self.__string = self.__separator.join(bits)
        return self.__string


class Authority(Part):
    """ A host name plus optional port and user information detail.

    **Syntax**
        ``authority := [ user_info "@" ] host [ ":" port ]``

    .. seealso::
        `RFC 3986 § 3.2`_

    .. _`RFC 3986 § 3.2`: http://tools.ietf.org/html/rfc3986#section-3.2
    """

    @classmethod
    def _parse_host_port(cls, string):
        host, colon, port = string.rpartition(":")
        if colon:
            return host, int(port)
        else:
            return host, None

    __instances = {}

    def __new__(cls, string):
        try:
            inst = cls.__instances[string]
        except KeyError:
            inst = super(Authority, cls).__new__(cls)
            if string is not None:
                user_info, at, host_port = string.rpartition("@")
                if at:
                    inst.__user_info = percent_decode(user_info)
                inst.__host, inst.__port = cls._parse_host_port(host_port)
            cls.__instances[string] = inst
        return inst

    __user_info = None
    __host = None
    __port = None

    __string = NotImplemented

    def __init__(self, string):
        super(Authority, self).__init__()

    def __hash__(self):
        return hash(self.string)

    @property
    def host(self):
        """ The host part of this authority component, an empty string if host
        is empty or :py:const:`None` if undefined.

        ::

            >>> Authority(None).host
            None
            >>> Authority("").host
            ''
            >>> Authority("example.com").host
            'example.com'
            >>> Authority("example.com:8080").host
            'example.com'
            >>> Authority("bob@example.com").host
            'example.com'
            >>> Authority("bob@example.com:8080").host
            'example.com'

        :return:
        """
        return self.__host

    @property
    def host_port(self):
        """ The host and port parts of this authority component or
        :py:const:`None` if undefined.

        ::

            >>> Authority(None).host_port
            None
            >>> Authority("").host_port
            ''
            >>> Authority("example.com").host_port
            'example.com'
            >>> Authority("example.com:8080").host_port
            'example.com:8080'
            >>> Authority("bob@example.com").host_port
            'example.com'
            >>> Authority("bob@example.com:8080").host_port
            'example.com:8080'

        :return:
        """
        u = [self.__host]
        if self.__port is not None:
            u += [":", ustr(self.__port)]
        return "".join(u)

    @property
    def port(self):
        """ The port part of this authority component or :py:const:`None` if
        undefined.

        ::

            >>> Authority(None).port
            None
            >>> Authority("").port
            None
            >>> Authority("example.com").port
            None
            >>> Authority("example.com:8080").port
            8080
            >>> Authority("bob@example.com").port
            None
            >>> Authority("bob@example.com:8080").port
            8080

        :return:
        """
        return self.__port

    @property
    def string(self):
        """ The full string value of this authority component or
        :`py:const:`None` if undefined.

        ::

            >>> Authority(None).string
            None
            >>> Authority("").string
            ''
            >>> Authority("example.com").string
            'example.com'
            >>> Authority("example.com:8080").string
            'example.com:8080'
            >>> Authority("bob@example.com").string
            'bob@example.com'
            >>> Authority("bob@example.com:8080").string
            'bob@example.com:8080'

        :return:
        """
        if self.__string is NotImplemented:
            if self.__host is None:
                self.__string = None
            else:
                u = []
                if self.__user_info is not None:
                    u += [percent_encode(self.__user_info), "@"]
                u += [self.__host]
                if self.__port is not None:
                    u += [":", ustr(self.__port)]
                self.__string = "".join(u)
        return self.__string
        
    @property
    def user_info(self):
        """ The user information part of this authority component or
        :py:const:`None` if undefined.

        ::

            >>> Authority(None).user_info
            None
            >>> Authority("").user_info
            None
            >>> Authority("example.com").user_info
            None
            >>> Authority("example.com:8080").user_info
            None
            >>> Authority("bob@example.com").user_info
            'bob'
            >>> Authority("bob@example.com:8080").user_info
            'bob'

        :return:
        """
        return self.__user_info


class Path(Part):

    __segments = None
    __string = NotImplemented

    def __init__(self, string):
        super(Path, self).__init__()
        if string is not None:
            self.__segments = tuple(map(percent_decode, string.split("/")))

    def __hash__(self):
        return hash(self.string)

    @property
    def string(self):
        if self.__string is NotImplemented:
            if self.__segments is None:
                self.__string = None
            else:
                self.__string = "/".join(map(percent_encode, self.__segments))
        return self.__string

    @property
    def segments(self):
        if self.__segments is None:
            return ()
        else:
            return self.__segments

    def __iter__(self):
        return iter(self.__segments)

    def remove_dot_segments(self):
        """ Implementation of RFC3986, section 5.2.4
        """
        inp = self.string
        out = ""
        while inp:
            if inp.startswith("../"):
                inp = inp[3:]
            elif inp.startswith("./"):
                inp = inp[2:]
            elif inp.startswith("/./"):
                inp = inp[2:]
            elif inp == "/.":
                inp = "/"
            elif inp.startswith("/../"):
                inp = inp[3:]
                out = out.rpartition("/")[0]
            elif inp == "/..":
                inp = "/"
                out = out.rpartition("/")[0]
            elif inp in (".", ".."):
                inp = ""
            else:
                if inp.startswith("/"):
                    inp = inp[1:]
                    out += "/"
                seg, slash, inp = inp.partition("/")
                out += seg
                inp = slash + inp
        return Path(out)

    def with_trailing_slash(self):
        if self.__segments is None:
            return self
        s = self.string
        if s.endswith("/"):
            return self
        else:
            return Path(s + "/")

    def without_trailing_slash(self):
        if self.__segments is None:
            return self
        s = self.string
        if s.endswith("/"):
            return Path(s[:-1])
        else:
            return self


class Query(ParameterString):

    SEPARATOR = "&"

    def __init__(self, string):
        super(Query, self).__init__(string, self.SEPARATOR)

    def __hash__(self):
        return hash(self.string)


class URI(Part):
    """ Uniform Resource Identifier.

    .. seealso::
        `RFC 3986`_

    .. _`RFC 3986`: http://tools.ietf.org/html/rfc3986
    """

    @classmethod
    def build(cls, **parts):
        """ Build a URI object from named parts. The part names available are:

        - string
        - hierarchical_part
        - absolute_path_reference
        - authority
        - host_port
        - scheme
        - user_info
        - host
        - port
        - path
        - query
        - fragment

        """
        uri = URI(parts.get("string"))
        uri.__set_hierarchical_part(parts.get("hierarchical_part"))
        uri.__set_absolute_path_reference(parts.get("absolute_path_reference"))
        uri.__set_authority(parts.get("authority"))
        uri.__set_host_port(parts.get("host_port"))
        uri.__set_scheme(parts.get("scheme"))
        uri.__set_user_info(parts.get("user_info"))
        uri.__set_host(parts.get("host"))
        uri.__set_port(parts.get("port"))
        uri.__set_path(parts.get("path"))
        uri.__set_query(parts.get("query"))
        uri.__set_fragment(parts.get("fragment"))
        if parts and uri.__path is None:
            uri.__path = Path("")
        return uri

    @classmethod
    def _partition_fragment(cls, value):
        value, hash, fragment = value.partition("#")
        if fragment:
            return value, percent_decode(fragment)
        else:
            return value, None

    @classmethod
    def _partition_query(cls, value):
        value, question_mark, query = value.partition("?")
        if query:
            return value, Query(query)
        else:
            return value, None

    @classmethod
    def _parse_hierarchical_part(cls, value):
        if value.startswith("//"):
            authority, slash, path = value[2:].partition("/")
            if slash:
                return Authority(authority), Path(slash + path)
            else:
                return Authority(authority), Path("")
        else:
            return None, Path(value)

    def __new__(cls, value):
        if isinstance(value, cls):
            return value
        inst = super(cls, URI).__new__(cls)
        if value is None:
            return inst
        try:
            if value.__uri__ is None:
                return inst
        except AttributeError:
            pass
        try:
            value = ustr(value.__uri__)
        except AttributeError:
            value = ustr(value)
        # scheme
        if ":" in value:
            inst.__scheme, _, value = value.partition(":")
            inst.__scheme = percent_decode(inst.__scheme)
        else:
            inst.__scheme = None
        # fragment
        value, inst.__fragment = cls._partition_fragment(value)
        # query
        value, inst.__query = cls._partition_query(value)
        # hierarchical part
        inst.__authority, inst.__path = cls._parse_hierarchical_part(value)
        return inst

    __scheme = None
    __authority = None
    __path = None
    __query = None
    __fragment = None

    __string = NotImplemented

    def __init__(self, value):
        Part.__init__(self)

    def __hash__(self):
        return hash(self.string)

    def __add__(self, other):
        return URI("{0}{1}".format(self, other))

    @property
    def __uri__(self):
        return self.string

    def __set_hierarchical_part(self, string):
        if string is not None:
            self.__authority, self.__path = self._parse_hierarchical_part(string)

    def __set_absolute_path_reference(self, string):
        if string is not None:
            string, self.__fragment = self._partition_fragment(string)
            string, self.__query = self._partition_query(string)
            self.__path = Path(string)

    def __set_authority(self, string):
        if string is not None:
            self.__authority = Authority(string)

    def __set_host_port(self, string):
        if string is not None:
            if self.__authority is None:
                self.__authority = Authority(string)
            else:
                host, port = Authority._parse_host_port(string)
                self.__authority._Authority__host = host
                self.__authority._Authority__port = port

    def __set_scheme(self, string):
        if string is not None:
            self.__scheme = string

    def __set_user_info(self, string):
        if string is not None:
            if self.__authority is None:
                self.__authority = Authority("")
            self.__authority._Authority__user_info = string

    def __set_host(self, string):
        if string is not None:
            if self.__authority is None:
                self.__authority = Authority(string)
            else:
                self.__authority._Authority__host = string

    def __set_port(self, number):
        if number is not None:
            if self.__authority is None:
                self.__authority = Authority("")
            self.__authority._Authority__port = number

    def __set_path(self, string):
        if string is not None:
            self.__path = Path(string)

    def __set_query(self, string):
        if string is not None:
            self.__query = Query(string)

    def __set_fragment(self, string):
        if string is not None:
            self.__fragment = string

    @property
    def string(self):
        """ The full percent-encoded string value of this URI or
        :py:const:`None` if undefined.

        ::

            >>> URI(None).string
            None
            >>> URI("").string
            ''
            >>> URI("http://example.com").string
            'example.com'
            >>> URI("foo/bar").string
            'foo/bar'
            >>> URI("http://bob@example.com:8080/data/report.html?date=2000-12-25#summary").string
            'http://bob@example.com:8080/data/report.html?date=2000-12-25#summary'

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
            \___________________________________________________________________/
                                             |
                                           string

        :rtype: percent-encoded string or :py:const:`None`

        .. note::
            Unlike ``string``, the ``__str__`` method will always return a
            string, even when the URI is undefined; in this case, an empty
            string is returned instead of :py:const:`None`.
        """
        if self.__string is NotImplemented:
            if self.__path is None:
                self.__string = None
            else:
                u = []
                if self.__scheme is not None:
                    u += [percent_encode(self.__scheme), ":"]
                if self.__authority is not None:
                    u += ["//", ustr(self.__authority)]
                u += [ustr(self.__path)]
                if self.__query is not None:
                    u += ["?", ustr(self.__query)]
                if self.__fragment is not None:
                    u += ["#", percent_encode(self.__fragment)]
                self.__string = "".join(u)
        return self.__string

    @property
    def scheme(self):
        """ The scheme part of this URI or :py:const:`None` if undefined.

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
            \___/
              |
            scheme

        :rtype: unencoded string or :py:const:`None`
        """
        return self.__scheme

    @property
    def authority(self):
        """ The authority part of this URI or :py:const:`None` if undefined.

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
                    \__________________/
                             |
                         authority

        :rtype: :py:class:`Authority <httpstream.uri.Authority>` instance or
            :py:const:`None`
        """
        return self.__authority

    @property
    def user_info(self):
        """ The user information part of this URI or :py:const:`None` if
        undefined.

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
                    \_/
                     |
                 user_info

        :return: string value of user information part or :py:const:`None`
        :rtype: unencoded string or :py:const:`None`
        """
        if self.__authority is None:
            return None
        else:
            return self.__authority.user_info

    @property
    def host(self):
        """ The *host* part of this URI or :py:const:`None` if undefined.

        ::

            >>> URI(None).host
            None
            >>> URI("").host
            None
            >>> URI("http://example.com").host
            'example.com'
            >>> URI("http://example.com:8080/data").host
            'example.com'

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
                        \_________/
                             |
                            host

        :return:
        :rtype: unencoded string or :py:const:`None`
        """
        if self.__authority is None:
            return None
        else:
            return self.__authority.host
        
    @property
    def port(self):
        """ The *port* part of this URI or :py:const:`None` if undefined.

        ::

            >>> URI(None).port
            None
            >>> URI("").port
            None
            >>> URI("http://example.com").port
            None
            >>> URI("http://example.com:8080/data").port
            8080

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
                                    \__/
                                     |
                                    port

        :return:
        :rtype: integer or :py:const:`None`
        """
        if self.__authority is None:
            return None
        else:
            return self.__authority.port

    @property
    def host_port(self):
        """ The *host* and *port* parts of this URI separated by a colon or
        :py:const:`None` if both are undefined.

        ::

            >>> URI(None).host_port
            None
            >>> URI("").host_port
            None
            >>> URI("http://example.com").host_port
            'example.com'
            >>> URI("http://example.com:8080/data").host_port
            'example.com:8080'
            >>> URI("http://bob@example.com:8080/data").host_port
            'example.com:8080'

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
                        \______________/
                               |
                           host_port

        :return:
        :rtype: percent-encoded string or :py:const:`None`
        """
        if self.__authority is None:
            return None
        else:
            return self.__authority.host_port

    @property
    def path(self):
        """ The *path* part of this URI or :py:const:`None` if undefined.

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
                                        \_______________/
                                                |
                                               path

        :return:
        :rtype: :py:class:`Path <httpstream.uri.Path>` instance or
            :py:const:`None`
        """
        return self.__path

    @property
    def query(self):
        """ The *query* part of this URI or :py:const:`None` if undefined.

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
                                                          \_____________/
                                                                 |
                                                               query

        :rtype: :py:class:`Query <httpstream.uri.Query>` instance or
            :py:const:`None`
        """
        return self.__query

    @property
    def fragment(self):
        """ The *fragment* part of this URI or :py:const:`None` if undefined.

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
                                                                          \_____/
                                                                             |
                                                                          fragment

        :return:
        :rtype: unencoded string or :py:const:`None`
        """
        return self.__fragment

    @property
    def hierarchical_part(self):
        """ The authority and path parts of this URI or :py:const:`None` if
        undefined.

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
                    \___________________________________/
                                      |
                              hierarchical_part

        :return: combined string values of authority and path parts or
            :py:const:`None`
        :rtype: percent-encoded string or :py:const:`None`
        """
        if self.__path is None:
            return None
        u = []
        if self.__authority is not None:
            u += ["//", ustr(self.__authority)]
        u += [ustr(self.__path)]
        return "".join(u)

    @property
    def absolute_path_reference(self):
        """ The path, query and fragment parts of this URI or :py:const:`None`
        if undefined.

        **Component Definition:**
        ::

            https://bob@example.com:8080/data/report.html?date=2000-12-25#summary
                                        \_______________________________________/
                                                            |
                                                  absolute_path_reference

        :return: combined string values of path, query and fragment parts or
            :py:const:`None`
        :rtype: percent-encoded string or :py:const:`None`
        """
        if self.__path is None:
            return None
        u = [ustr(self.__path)]
        if self.__query is not None:
            u += ["?", ustr(self.__query)]
        if self.__fragment is not None:
            u += ["#", percent_encode(self.__fragment)]
        return "".join(u)

    def _merge_path(self, relative_path_reference):
        if self.__authority is not None and not self.__path:
            return Path("/" + ustr(relative_path_reference))
        elif "/" in self.__path.string:
            segments = self.__path.segments[:-1] + ("",)
            return Path("/".join(segments) + ustr(relative_path_reference))
        else:
            return relative_path_reference

    def resolve(self, reference, strict=True):
        """ Transform a reference relative to this URI to produce a full target
        URI.

        .. seealso::
            `RFC 3986 § 5.2.2`_

        .. _`RFC 3986 § 5.2.2`: http://tools.ietf.org/html/rfc3986#section-5.2.2
        """
        if reference is None:
            return None
        reference = self._cast(reference)
        target = URI(None)
        if not strict and reference.__scheme == self.__scheme:
            reference_scheme = None
        else:
            reference_scheme = reference.__scheme
        if reference_scheme is not None:
            target.__scheme = reference_scheme
            target.__authority = reference.__authority
            target.__path = reference.__path.remove_dot_segments()
            target.__query = reference.__query
        else:
            if reference.__authority is not None:
                target.__authority = reference.__authority
                target.__path = reference.__path.remove_dot_segments()
                target.__query = reference.__query
            else:
                if not reference.path:
                    target.__path = self.__path
                    if reference.__query is not None:
                        target.__query = reference.__query
                    else:
                        target.__query = self.__query
                else:
                    if ustr(reference.__path).startswith("/"):
                        target.__path = reference.__path.remove_dot_segments()
                    else:
                        target.__path = self._merge_path(reference.__path)
                        target.__path = target.__path.remove_dot_segments()
                    target.__query = reference.__query
                target.__authority = self.__authority
            target.__scheme = self.__scheme
        target.__fragment = reference.__fragment
        return target
