#!/usr/bin/env python3
"""
CCMM Handler - Handler for working with CCMM metadata using Python objects
"""

from typing import Optional, List, Dict, Any
from datetime import date
import xml.etree.ElementTree as ET
from lxml import etree
import os
import re
from urllib.parse import urlparse

from .ccmm_models import *
from .schemas import get_schema_path, get_ccmm_root


class CCMMHandler:
    """
    Handler for working with CCMM metadata.
    Data is kept in Python objects and exported to XML only when needed.
    
    Args:
        ccmm_path: Optional path to CCMM schemas directory. If None, uses bundled schemas.
    """
    
    def __init__(self, ccmm_path: Optional[str] = None):
        if ccmm_path is None:
            # Use bundled CCMM schemas
            self.ccmm_path = get_ccmm_root()
        else:
            self.ccmm_path = ccmm_path
        self.dataset: Optional[Dataset] = None
        self._init_empty_dataset()
    
    def _init_empty_dataset(self):
        """Initializes empty dataset with minimal requirements"""
        # Create basic terms_of_use
        default_terms = TermsOfUse(
            access_rights="http://purl.org/coar/access_right/c_abf2",
            license_name="http://creativecommons.org/licenses/by/4.0/",
            description="Default terms of use"
        )
        
        self.dataset = Dataset(
            title="",
            publication_year=2024,
            identifiers=[],
            metadata_records=[],
            qualified_relations=[],
            time_references=[],
            subjects=[],
            terms_of_use=default_terms
        )
    
    # === Basic methods ===
    
    def set_title(self, title: str):
        """Sets dataset title"""
        self._validate_non_empty_string(title, "Title")
        self.dataset.title = title
    
    def set_publication_year(self, year: int):
        """Sets publication year"""
        self._validate_year(year)
        self.dataset.publication_year = year
    
    def set_version(self, version: str):
        """Sets dataset version"""
        self._validate_non_empty_string(version, "Version")
        self.dataset.version = version
    
    def set_iri(self, iri: str):
        """Sets dataset IRI"""
        self._validate_uri(iri)
        self.dataset.iri = iri
    
    def set_primary_language(self, language: Language):
        """Sets primary language of dataset"""
        self.dataset.primary_language = language
    
    def add_other_language(self, language: Language):
        """Adds another language to dataset"""
        if language not in self.dataset.other_languages:
            self.dataset.other_languages.append(language)
    
    def set_terms_of_use(self, access_rights: str, license_name: str, description: Optional[str] = None, iri: Optional[str] = None):
        """Sets terms of use"""
        self._validate_non_empty_string(access_rights, "Access rights")
        self._validate_non_empty_string(license_name, "License name")
        if iri:
            self._validate_uri(iri)
        
        self.dataset.terms_of_use = TermsOfUse(
            access_rights=access_rights,
            license_name=license_name,
            description=description,
            iri=iri
        )
    
    # === Identifiers ===
    
    def add_identifier(self, value: str, scheme: IdentifierScheme, iri: Optional[str] = None):
        """Adds dataset identifier"""
        self._validate_non_empty_string(value, "Identifier value")
        if iri:
            self._validate_uri(iri)
        
        identifier = Identifier(value=value, scheme=scheme, iri=iri)
        self.dataset.identifiers.append(identifier)
    
    # === Descriptions ===
    
    def add_description(self, description_text: str, description_type: Optional[str] = None, iri: Optional[str] = None):
        """Adds dataset description"""
        self._validate_non_empty_string(description_text, "Description text")
        if iri:
            self._validate_uri(iri)
        
        description = Description(
            description_text=description_text,
            description_type=description_type,
            iri=iri
        )
        self.dataset.descriptions.append(description)
    
    # === Alternate titles ===
    
    def add_alternate_title(self, title: str, language: Language = Language.CS, 
                          alternate_title_type: Optional[str] = None, iri: Optional[str] = None):
        """Adds alternate title"""
        self._validate_non_empty_string(title, "Alternate title")
        if iri:
            self._validate_uri(iri)
        
        title_text = MultiLanguageText(text=title, language=language)
        alternate_title = AlternateTitle(
            titles=[title_text],
            alternate_title_type=alternate_title_type,
            iri=iri
        )
        self.dataset.alternate_titles.append(alternate_title)
    
    # === Subjects ===
    
    def add_subject(self, title: str, language: Language = Language.CS, 
                   classification_code: Optional[str] = None, 
                   subject_scheme: Optional[SubjectScheme] = None,
                   definition: Optional[str] = None,
                   iri: Optional[str] = None):
        """Adds subject/keyword"""
        self._validate_non_empty_string(title, "Subject title")
        if iri:
            self._validate_uri(iri)
        
        title_text = MultiLanguageText(text=title, language=language)
        definitions = []
        if definition:
            definitions.append(MultiLanguageText(text=definition, language=language))
        
        subject = Subject(
            titles=[title_text],
            classification_code=classification_code,
            subject_scheme=subject_scheme,
            definitions=definitions,
            iri=iri
        )
        self.dataset.subjects.append(subject)
    
    # === Agents and relationships ===
    
    def add_agent_relationship(self, agent_name: str, role: AgentRole, 
                             agent_type: AgentType = AgentType.PERSON,
                             agent_identifier: Optional[Identifier] = None,
                             agent_email: Optional[str] = None,
                             agent_affiliation: Optional[str] = None,
                             iri: Optional[str] = None):
        """Adds relationship to agent"""
        self._validate_non_empty_string(agent_name, "Agent name")
        if agent_email:
            self._validate_email(agent_email)
        if iri:
            self._validate_uri(iri)
        
        agent = Agent(
            name=agent_name,
            agent_type=agent_type,
            identifier=agent_identifier,
            email=agent_email,
            affiliation=agent_affiliation
        )
        
        relationship = ResourceToAgentRelationship(
            agent=agent,
            role=role,
            iri=iri
        )
        self.dataset.qualified_relations.append(relationship)
    
    # === Time references ===
    
    def add_time_reference(self, time_value: str, time_type: TimeReferenceType, iri: Optional[str] = None):
        """Adds time reference"""
        self._validate_non_empty_string(time_value, "Time value")
        if iri:
            self._validate_uri(iri)
        
        time_ref = TimeReference(
            time_value=time_value,
            time_type=time_type,
            iri=iri
        )
        self.dataset.time_references.append(time_ref)
    
    # === Locations ===
    
    def add_location(self, location_value: str, location_type: LocationType, iri: Optional[str] = None):
        """Adds a location"""
        self._validate_non_empty_string(location_value, "Location value")
        if iri:
            self._validate_uri(iri)
        
        location = Location(
            location_value=location_value,
            location_type=location_type,
            iri=iri
        )
        self.dataset.locations.append(location)
    
    # === Distribution ===
    
    def add_distribution(self, access_url: str, format_type: Optional[DistributionFormat] = None,
                        title: Optional[str] = None, description: Optional[str] = None,
                        iri: Optional[str] = None):
        """Adds a distribution"""
        self._validate_uri(access_url)
        if iri:
            self._validate_uri(iri)
        
        distribution = Distribution(
            access_url=access_url,
            format_type=format_type,
            title=title,
            description=description,
            iri=iri
        )
        self.dataset.distributions.append(distribution)
    
    # === Metadata Record ===
    
    def add_metadata_record(self, qualified_relations: List[ResourceToAgentRelationship],
                           date_created: Optional[date] = None,
                           date_updated: Optional[List[date]] = None,
                           languages: Optional[List[Language]] = None,
                           iri: Optional[str] = None):
        """Adds a metadata record"""
        if not qualified_relations:
            raise ValueError("Metadata record must have at least one qualified_relation")
        if iri:
            self._validate_uri(iri)
        
        metadata_record = MetadataRecord(
            qualified_relations=qualified_relations,
            date_created=date_created,
            date_updated=date_updated or [],
            languages=languages or [],
            iri=iri
        )
        self.dataset.metadata_records.append(metadata_record)
    
    # === Validation ===
    
    def is_valid(self) -> bool:
        """Checks if the dataset is valid"""
        try:
            # Basic validation
            if not self.dataset.title.strip():
                return False
            if not self.dataset.identifiers:
                return False
            if not self.dataset.metadata_records:
                return False
            if not self.dataset.qualified_relations:
                return False
            if not self.dataset.time_references:
                return False
            if not self.dataset.subjects:
                return False
            
            # XSD validation
            return self._validate_against_xsd()
        except Exception as e:
            print(f"Validation error: {e}")
            return False
    
    def _validate_against_xsd(self) -> bool:
        """Validation against XSD schema"""
        try:
            xml_elem = self.dataset.to_xml_element()
            xml_string = ET.tostring(xml_elem, encoding='unicode')
            
            xsd_path = get_schema_path("dataset")
            with open(xsd_path, 'r') as f:
                schema = etree.XMLSchema(etree.parse(f))
            
            xml_doc = etree.fromstring(xml_string)
            is_valid = schema.validate(xml_doc)
            
            if not is_valid:
                print(f"XSD validation errors: {schema.error_log}")
            
            return is_valid
        except Exception as e:
            print(f"XSD validation error: {e}")
            return False
    
    # === Export/Import ===
    
    def to_xml_string(self, pretty_print: bool = True) -> str:
        """Converts the dataset to an XML string"""
        xml_elem = self.dataset.to_xml_element()
        xml_string = ET.tostring(xml_elem, encoding='unicode')
        
        if pretty_print:
            # Reformat for better readability
            root = etree.fromstring(xml_string)
            return etree.tostring(root, pretty_print=True, encoding='unicode')
        
        return xml_string
    def save_to_file(self, file_path: str, validate: bool = True):
        """Saves the dataset to an XML file"""
        if validate and not self.is_valid():
            raise ValueError("Dataset is not valid. Fix validation errors before saving.")
        
        xml_elem = self.dataset.to_xml_element()
        
        # Reformat for better readability
        xml_string = ET.tostring(xml_elem, encoding='unicode')
        root = etree.fromstring(xml_string)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(etree.tostring(root, pretty_print=True, encoding='unicode'))
    
    def load_from_file(self, file_path: str) -> bool:
        """Loads the dataset from an XML file"""
        try:
            # TODO: Implement parsing XML back into Python objects
            print("Load from file is not implemented yet")
            return False
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    # === Validation methods ===
    
    def _validate_non_empty_string(self, value: str, field_name: str):
        """Validates that the string is not empty"""
        if not value or not value.strip():
            raise ValueError(f"{field_name} cannot be empty.")
    
    def _validate_uri(self, uri: str):
        """Validates URI format"""
        if not uri or not uri.strip():
            raise ValueError("URI cannot be empty.")
        try:
            result = urlparse(uri)
            if not result.scheme or not result.netloc:
                raise ValueError(f"Invalid URI format: {uri}")
        except Exception as e:
            raise ValueError(f"Invalid URI format: {uri} - {e}")
    
    def _validate_year(self, year: int):
        """Validates publication year"""
        from datetime import datetime
        current_year = datetime.now().year
        if year < 1000 or year > current_year + 10:
            raise ValueError(f"Publication year must be between 1000 and {current_year + 10}.")
    
    def _validate_email(self, email: str):
        """Validates email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError(f"Invalid email format: {email}")
    
    # === Getters ===
    
    def get_title(self) -> str:
        """Returns the dataset title"""
        return self.dataset.title
    
    def get_publication_year(self) -> int:
        """Returns the publication year"""
        return self.dataset.publication_year
    
    def get_identifiers(self) -> List[Identifier]:
        """Returns the list of identifiers"""
        return self.dataset.identifiers
    
    def get_subjects(self) -> List[Subject]:
        """Returns the list of subjects"""
        return self.dataset.subjects
    
    def get_descriptions(self) -> List[Description]:
        """Returns the list of descriptions"""
        return self.dataset.descriptions
    
    def get_distributions(self) -> List[Distribution]:
        """Returns the list of distributions"""
        return self.dataset.distributions
    
    def get_agent_relationships(self) -> List[ResourceToAgentRelationship]:
        """Returns the list of agent relationships"""
        return self.dataset.qualified_relations
    
    def get_summary(self) -> Dict[str, Any]:
        """Returns a summary of the dataset"""
        return {
            'title': self.dataset.title,
            'publication_year': self.dataset.publication_year,
            'version': self.dataset.version,
            'identifiers_count': len(self.dataset.identifiers),
            'descriptions_count': len(self.dataset.descriptions),
            'subjects_count': len(self.dataset.subjects),
            'agents_count': len(self.dataset.qualified_relations),
            'distributions_count': len(self.dataset.distributions),
            'primary_language': self.dataset.primary_language.value if self.dataset.primary_language else None,
            'other_languages': [lang.value for lang in self.dataset.other_languages]
        }
