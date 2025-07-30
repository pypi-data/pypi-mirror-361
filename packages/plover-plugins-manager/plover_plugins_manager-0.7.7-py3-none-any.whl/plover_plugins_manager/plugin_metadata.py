from collections import namedtuple
from functools import total_ordering

from pkg_resources import parse_version

import logging
logger = logging.getLogger(__name__)


@total_ordering
class PluginMetadata(namedtuple('PluginMetadata', '''
                                author
                                author_email
                                description
                                description_content_type
                                home_page
                                keywords
                                license
                                name
                                summary
                                version
                                ''')):

    @property
    def requirement(self):
        return '%s==%s' % (self.name, self.version)

    @property
    def parsed_version(self):
        v = self.version
        logger.debug("parsed_version: raw value=%r type=%s", v, type(v).__name__)

        # Coerce packaging.version.Version → str
        try:
            from packaging.version import Version as PackagingVersion
            if isinstance(v, PackagingVersion):
                v = str(v)
                logger.debug("parsed_version: after packaging.Version → %r", v)
        except Exception:
            logger.debug("parsed_version: packaging import failed")

        # Decode raw bytes/bytearray → str
        if isinstance(v, (bytes, bytearray)):
            try:
                v = v.decode()
                logger.debug("parsed_version: after bytes decode → %r", v)
            except Exception:
                logger.debug("parsed_version: bytes decode failed")
                v = ''

        # Final fallback
        result = parse_version(str(v) or '0')
        logger.debug("parsed_version: final parsed result=%r", result)
        return result

    @classmethod
    def from_dict(cls, d):
        return cls(*(d.get(k, '') for k in cls._fields))

    @classmethod
    def from_kwargs(cls, **kwargs):
        return cls.from_dict(kwargs)

    def to_dict(self):
        return dict(zip(self._fields, self))

    def __eq__(self, other):
        return ((self.name.lower(), self.parsed_version) ==
                (other.name.lower(), other.parsed_version))

    def __lt__(self, other):
        return ((self.name.lower(), self.parsed_version) <
                (other.name.lower(), other.parsed_version))
