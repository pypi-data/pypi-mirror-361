"""Wrapper class for OSIS objects for easy serialization."""

import dataclasses

from typing_extensions import Self
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata_pydantic.bindings import XmlContext, XmlParser, XmlSerializer

import pyosis.generated
import pyosis.generated.osis_core_2_1_1

CONTEXT = XmlContext()
CONFIG = SerializerConfig(indent="  ")
PARSER = XmlParser(context=CONTEXT)
SERIALIZER = XmlSerializer(context=CONTEXT, config=CONFIG)


@dataclasses.dataclass
class OsisXML:
    """Wrapper class for OSIS objects for easy serialization."""

    osis: pyosis.generated.osis_core_2_1_1.Osis
    """OSIS object."""

    @classmethod
    def from_xml(cls, xml: str) -> Self:
        """Deserialize an XML string to an OSIS Object."""
        return cls(osis=PARSER.from_string(xml, pyosis.generated.Osis))

    def to_xml(self) -> str:
        """Serialize an OSIS object to an XML file."""
        return SERIALIZER.render(self.osis, ns_map={None: pyosis.generated.osis_core_2_1_1.__NAMESPACE__})
