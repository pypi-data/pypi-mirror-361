#!/usr/bin/env python3
"""
CCMM Data Models - Python objects for representing CCMM metadata
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import date, datetime
import xml.etree.ElementTree as ET

# Enums for valid values
class Language(Enum):
    CS = "cs"
    EN = "en"
    DE = "de"
    FR = "fr"
    ES = "es"
    IT = "it"
    SK = "sk"

class AgentType(Enum):
    PERSON = "person"
    ORGANIZATION = "organization"

class AgentRole(Enum):
    CREATOR = "creator"
    CONTRIBUTOR = "contributor"
    EDITOR = "editor"
    PUBLISHER = "publisher"
    CURATOR = "curator"
    REVIEWER = "reviewer"
    CONTACT_PERSON = "contact_person"

class IdentifierScheme(Enum):
    DOI = "DOI"
    HANDLE = "Handle"
    ARK = "ARK"
    ORCID = "ORCID"
    URL = "URL"
    UUID = "UUID"

class SubjectScheme(Enum):
    KEYWORD = "keyword"
    CLASSIFICATION = "classification"
    FIELD_OF_SCIENCE = "field_of_science"

class TimeReferenceType(Enum):
    CREATED = "created"
    UPDATED = "updated"
    ISSUED = "issued"
    AVAILABLE = "available"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    COLLECTED = "collected"

class ResourceType(Enum):
    DATASET = "dataset"
    SOFTWARE = "software"
    TEXT = "text"
    IMAGE = "image"
    AUDIOVISUAL = "audiovisual"
    COLLECTION = "collection"
    OTHER = "other"

class LocationType(Enum):
    PLACE = "place"
    REGION = "region"
    COUNTRY = "country"
    COORDINATES = "coordinates"

class DistributionFormat(Enum):
    CSV = "text/csv"
    JSON = "application/json"
    XML = "application/xml"
    PDF = "application/pdf"
    ZIP = "application/zip"
    HTML = "text/html"
    PLAIN_TEXT = "text/plain"

# Basic class for multilingual texts
@dataclass
class MultiLanguageText:
    """Class for texts with language attributes"""
    text: str
    language: Language = Language.CS
    
    def to_xml_element(self, element_name: str) -> ET.Element:
        elem = ET.Element(element_name)
        elem.text = self.text
        elem.set("{http://www.w3.org/XML/1998/namespace}lang", self.language.value)
        return elem

# Identifier
@dataclass
class Identifier:
    """CCMM Identifier"""
    value: str
    scheme: IdentifierScheme
    iri: Optional[str] = None
    
    def to_xml_element(self) -> ET.Element:
        """Convert to XML according to XSD schema identifier"""
        elem = ET.Element("identifier")
        if self.iri:
            iri_elem = ET.SubElement(elem, "iri")
            iri_elem.text = self.iri
        value_elem = ET.SubElement(elem, "value")
        value_elem.text = self.value
        
        # Scheme element must contain identifier_scheme with iri element
        scheme_elem = ET.SubElement(elem, "scheme")
        scheme_iri = ET.SubElement(scheme_elem, "iri")
        scheme_iri.text = self.scheme.value
        
        return elem

# Alternate title
@dataclass
class AlternateTitle:
    """CCMM Alternate Title"""
    titles: List[MultiLanguageText]
    alternate_title_type: Optional[str] = None
    iri: Optional[str] = None
    
    def to_xml_element(self) -> ET.Element:
        elem = ET.Element("alternate_title")
        if self.iri:
            iri_elem = ET.SubElement(elem, "iri")
            iri_elem.text = self.iri
        for title in self.titles:
            elem.append(title.to_xml_element("title"))
        if self.alternate_title_type:
            type_elem = ET.SubElement(elem, "alternate_title_type")
            type_iri = ET.SubElement(type_elem, "iri")
            type_iri.text = self.alternate_title_type
        return elem

# Description
@dataclass
class Description:
    """CCMM Description"""
    description_text: str
    description_type: Optional[str] = None
    iri: Optional[str] = None
    
    def to_xml_element(self) -> ET.Element:
        elem = ET.Element("has_description")
        if self.iri:
            iri_elem = ET.SubElement(elem, "iri")
            iri_elem.text = self.iri
        desc_text_elem = ET.SubElement(elem, "description_text")
        desc_text_elem.text = self.description_text
        if self.description_type:
            type_elem = ET.SubElement(elem, "has_description_type")
            type_iri = ET.SubElement(type_elem, "iri")
            type_iri.text = self.description_type
        return elem

# Subject
@dataclass
class Subject:
    """CCMM Subject"""
    titles: List[MultiLanguageText]
    classification_code: Optional[str] = None
    subject_scheme: Optional[SubjectScheme] = None
    definitions: List[MultiLanguageText] = field(default_factory=list)
    iri: Optional[str] = None
    
    def to_xml_element(self) -> ET.Element:
        elem = ET.Element("subject")
        if self.iri:
            iri_elem = ET.SubElement(elem, "iri")
            iri_elem.text = self.iri
        for definition in self.definitions:
            elem.append(definition.to_xml_element("definition"))
        for title in self.titles:
            elem.append(title.to_xml_element("title"))
        if self.classification_code:
            code_elem = ET.SubElement(elem, "classification_code")
            code_elem.text = self.classification_code
        if self.subject_scheme:
            scheme_elem = ET.SubElement(elem, "subject_scheme")
            scheme_iri = ET.SubElement(scheme_elem, "iri")
            scheme_iri.text = self.subject_scheme.value
        return elem

# Agent
@dataclass
class Agent:
    """CCMM Agent"""
    name: str
    agent_type: AgentType
    identifier: Optional[Identifier] = None
    email: Optional[str] = None
    affiliation: Optional[str] = None
    iri: Optional[str] = None

# Resource to Agent Relationship
@dataclass
class ResourceToAgentRelationship:
    """CCMM Resource to Agent Relationship"""
    agent: Agent
    role: AgentRole
    iri: Optional[str] = None
    
    def to_xml_element(self) -> ET.Element:
        """Convert to XML according to XSD schema resource-to-agent-relationship"""
        elem = ET.Element("qualified_relation")
        
        # According to XSD: iri, role, relation (agent)
        if self.iri:
            iri_elem = ET.SubElement(elem, "iri")
            iri_elem.text = self.iri
        
        # Role as anyURI
        role_elem = ET.SubElement(elem, "role")
        role_elem.text = self.role.value
        
        # Relation contains agent
        relation_elem = ET.SubElement(elem, "relation")
        
        # Agent has xs:choice between organization and person
        if self.agent.agent_type == AgentType.ORGANIZATION:
            org_elem = ET.SubElement(relation_elem, "organization")
            if self.agent.iri:
                ET.SubElement(org_elem, "iri").text = self.agent.iri
            ET.SubElement(org_elem, "name").text = self.agent.name
            if self.agent.identifier:
                org_elem.append(self.agent.identifier.to_xml_element())
        else:
            person_elem = ET.SubElement(relation_elem, "person")
            if self.agent.iri:
                ET.SubElement(person_elem, "iri").text = self.agent.iri
            ET.SubElement(person_elem, "name").text = self.agent.name
            if self.agent.identifier:
                person_elem.append(self.agent.identifier.to_xml_element())
        
        return elem

# Time Reference
@dataclass
class TimeReference:
    """CCMM Time Reference"""
    time_value: str
    time_type: TimeReferenceType
    iri: Optional[str] = None
    
    def to_xml_element(self) -> ET.Element:
        """Convert to XML according to XSD schema time_reference"""
        elem = ET.Element("time_reference")
        
        # According to XSD: xs:choice between time_interval and time_instant
        # For simplicity, we use time_instant
        instant_elem = ET.SubElement(elem, "time_instant")
        
        if self.iri:
            iri_elem = ET.SubElement(instant_elem, "iri")
            iri_elem.text = self.iri
        
        # date_type is required
        date_type_elem = ET.SubElement(instant_elem, "date_type")
        date_type_iri = ET.SubElement(date_type_elem, "iri")
        date_type_iri.text = self.time_type.value
        
        # date or date_time (we use date)
        date_elem = ET.SubElement(instant_elem, "date")
        date_elem.text = self.time_value
        
        return elem

# Location
@dataclass
class Location:
    """CCMM Location"""
    location_value: str
    location_type: LocationType
    iri: Optional[str] = None
    
    def to_xml_element(self) -> ET.Element:
        """Convert to XML according to XSD schema location"""
        elem = ET.Element("location")
        if self.iri:
            iri_elem = ET.SubElement(elem, "iri")
            iri_elem.text = self.iri
        
        # According to XSD: name instead of value
        name_elem = ET.SubElement(elem, "name")
        name_elem.text = self.location_value
        
        # relation_type is a required element
        relation_type_elem = ET.SubElement(elem, "relation_type")
        relation_type_iri = ET.SubElement(relation_type_elem, "iri")
        relation_type_iri.text = self.location_type.value
        
        return elem

# Distribution
@dataclass
class Distribution:
    """CCMM Distribution"""
    access_url: str
    format_type: Optional[DistributionFormat] = None
    title: Optional[str] = None
    description: Optional[str] = None
    iri: Optional[str] = None
    
    def to_xml_element(self) -> ET.Element:
        """Convert to XML according to XSD schema distribution"""
        elem = ET.Element("distribution")
        
        # According to XSD: xs:choice between distribution_-_data_service and distribution_-_downloadable_file
        # We use distribution_-_downloadable_file
        downloadable_elem = ET.SubElement(elem, "distribution_-_downloadable_file")
        
        if self.iri:
            iri_elem = ET.SubElement(downloadable_elem, "iri")
            iri_elem.text = self.iri
        
        # title is required with xml:lang attribute
        title_elem = ET.SubElement(downloadable_elem, "title")
        title_elem.text = self.title if self.title else "Dataset file"
        title_elem.set("{http://www.w3.org/XML/1998/namespace}lang", "cs")
        
        # byte_size is required for downloadable_file
        byte_size_elem = ET.SubElement(downloadable_elem, "byte_size")
        byte_size_elem.text = "1000"  # placeholder
        
        # access_url is required - type file
        access_elem = ET.SubElement(downloadable_elem, "access_url")
        access_iri = ET.SubElement(access_elem, "iri")
        access_iri.text = self.access_url
        
        # format is required
        if self.format_type:
            format_elem = ET.SubElement(downloadable_elem, "format")
            format_iri = ET.SubElement(format_elem, "iri")
            format_iri.text = self.format_type.value
        
        return elem

# Terms of Use
@dataclass
class TermsOfUse:
    """CCMM Terms of Use"""
    access_rights: str
    license_name: str
    iri: Optional[str] = None
    description: Optional[str] = None
    
    def to_xml_element(self) -> ET.Element:
        """Convert to XML according to XSD schema terms_of_use"""
        elem = ET.Element("terms_of_use")
        
        if self.iri:
            iri_elem = ET.SubElement(elem, "iri")
            iri_elem.text = self.iri
        
        if self.description:
            desc_elem = ET.SubElement(elem, "description")
            desc_elem.text = self.description
            desc_elem.set("{http://www.w3.org/XML/1998/namespace}lang", "cs")
        
        # access_rights is required
        access_elem = ET.SubElement(elem, "access_rights")
        access_iri = ET.SubElement(access_elem, "iri")
        access_iri.text = self.access_rights
        
        # license is required
        license_elem = ET.SubElement(elem, "license")
        license_iri = ET.SubElement(license_elem, "iri")
        license_iri.text = self.license_name
        
        return elem

# Metadata Record
@dataclass
class MetadataRecord:
    """CCMM Metadata Record"""
    qualified_relations: List[ResourceToAgentRelationship]
    date_created: Optional[date] = None
    date_updated: List[date] = field(default_factory=list)
    languages: List[Language] = field(default_factory=list)
    iri: Optional[str] = None
    
    def to_xml_element(self) -> ET.Element:
        elem = ET.Element("is_described_by")
        if self.iri:
            iri_elem = ET.SubElement(elem, "iri")
            iri_elem.text = self.iri
        
        for updated in self.date_updated:
            updated_elem = ET.SubElement(elem, "date_updated")
            updated_elem.text = updated.isoformat()
        
        if self.date_created:
            created_elem = ET.SubElement(elem, "date_created")
            created_elem.text = self.date_created.isoformat()
        
        for relation in self.qualified_relations:
            elem.append(relation.to_xml_element())
        
        for lang in self.languages:
            lang_elem = ET.SubElement(elem, "language")
            lang_iri = ET.SubElement(lang_elem, "iri")
            lang_iri.text = lang.value
        
        return elem

# Main Dataset class
@dataclass
class Dataset:
    """CCMM Dataset - main class"""
    # Required elements
    title: str
    publication_year: int
    identifiers: List[Identifier]
    metadata_records: List[MetadataRecord]
    qualified_relations: List[ResourceToAgentRelationship]
    time_references: List[TimeReference]
    subjects: List[Subject]
    terms_of_use: TermsOfUse
    
    # Optional elements
    iri: Optional[str] = None
    version: Optional[str] = None
    descriptions: List[Description] = field(default_factory=list)
    alternate_titles: List[AlternateTitle] = field(default_factory=list)
    locations: List[Location] = field(default_factory=list)
    distributions: List[Distribution] = field(default_factory=list)
    primary_language: Optional[Language] = None
    other_languages: List[Language] = field(default_factory=list)
    
    def to_xml_element(self) -> ET.Element:
        """Convert to XML element according to XSD order"""
        elem = ET.Element("dataset")
        
        # XSD order podle schema.xsd
        # 1. iri (volitelné)
        if self.iri:
            iri_elem = ET.SubElement(elem, "iri")
            iri_elem.text = self.iri
        
        # 2. publication_year (povinné)
        year_elem = ET.SubElement(elem, "publication_year")
        year_elem.text = str(self.publication_year)
        
        # 3. version (volitelné)
        if self.version:
            version_elem = ET.SubElement(elem, "version")
            version_elem.text = self.version
        
        # 4. title (povinné)
        title_elem = ET.SubElement(elem, "title")
        title_elem.text = self.title
        
        # 5. has_description (volitelné, více)
        for desc in self.descriptions:
            elem.append(desc.to_xml_element())
        
        # 6. alternate_title (volitelné, více)
        for alt_title in self.alternate_titles:
            elem.append(alt_title.to_xml_element())
        
        # 7. is_described_by (povinné, více) - metadata records
        for record in self.metadata_records:
            elem.append(record.to_xml_element())
        
        # 8. identifier (povinné, více)
        for identifier in self.identifiers:
            elem.append(identifier.to_xml_element())
        
        # 9. location (volitelné, více)
        for location in self.locations:
            elem.append(location.to_xml_element())
        
        # 10. provenance (volitelné, více) - zatím neimplementováno
        
        # 11. qualified_relation (povinné, minimum 2, více)
        for relation in self.qualified_relations:
            elem.append(relation.to_xml_element())
        
        # 12. time_reference (povinné, více)
        for time_ref in self.time_references:
            elem.append(time_ref.to_xml_element())
        
        # 13. subject (povinné, více)
        for subject in self.subjects:
            elem.append(subject.to_xml_element())
        
        # 14. validation_result (volitelné, více) - zatím neimplementováno
        
        # 15. distribution (volitelné, více)
        for distribution in self.distributions:
            elem.append(distribution.to_xml_element())
        
        # 16. funding_reference (volitelné, více) - zatím neimplementováno
        
        # 17. terms_of_use (povinné)
        elem.append(self.terms_of_use.to_xml_element())
        
        # 18. related_resource (volitelné, více) - zatím neimplementováno
        
        # 19. resource_type (volitelné) - zatím neimplementováno
        
        # 20. other_language (volitelné, více)
        for lang in self.other_languages:
            lang_elem = ET.SubElement(elem, "other_language")
            lang_iri = ET.SubElement(lang_elem, "iri")
            lang_iri.text = lang.value
        
        # 21. primary_language (volitelné)
        if self.primary_language:
            lang_elem = ET.SubElement(elem, "primary_language")
            lang_iri = ET.SubElement(lang_elem, "iri")
            lang_iri.text = self.primary_language.value
        
        return elem
