import xml.etree.ElementTree as ET
from lxml import etree
from typing import Optional, Dict, List, Any
import os
import re
from datetime import datetime
from urllib.parse import urlparse

class CCMMMetadataHandler:
    def __init__(self, ccmm_path: str = "./schemas/CCMM"):
        self.ccmm_path = ccmm_path
        self.metadata = ET.Element('dataset')
        self.required_fields = {
            'title': False,
            'publication_year': False,
            'identifier': False
        }

    def add_identifier(self, value: str, scheme: str, iri: Optional[str] = None):
        self._validate_identifier(value)
        self._validate_identifier(scheme)
        if iri:
            self._validate_uri(iri)
        identifier = ET.SubElement(self.metadata, 'identifier')
        ET.SubElement(identifier, 'value').text = value
        ET.SubElement(identifier, 'scheme').text = scheme
        if iri:
            ET.SubElement(identifier, 'iri').text = iri
        self.required_fields['identifier'] = True

    def add_description(self, text: str):
        if not text.strip():
            raise ValueError("Description cannot be empty.")
        description = ET.SubElement(self.metadata, 'has_description')
        ET.SubElement(description, 'description_text').text = text

    def validate_against_xsd(self, xsd_file: str):
        xsd_path = os.path.join(self.ccmm_path, xsd_file)
        with open(xsd_path, 'r') as f:
            schema = etree.XMLSchema(etree.parse(f))
        xml_string = ET.tostring(self.metadata, encoding='unicode')
        xml_doc = etree.fromstring(xml_string)
        is_valid = schema.validate(xml_doc)
        if not is_valid:
            print(f"XSD validation errors: {schema.error_log}")
        return is_valid

    def load_from_file(self, xml_file_path: str) -> bool:
        try:
            tree = ET.parse(xml_file_path)
            self.metadata = tree.getroot()
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def set_title(self, title: str):
        """Set the title of the dataset."""
        if not title.strip():
            raise ValueError("Title cannot be empty.")
        existing_title = self.metadata.find('title')
        if existing_title is not None:
            existing_title.text = title
        else:
            ET.SubElement(self.metadata, 'title').text = title
        self.required_fields['title'] = True

    def set_publication_year(self, year: int):
        """Set the publication year of the dataset."""
        self._validate_year(year)
        existing_year = self.metadata.find('publication_year')
        if existing_year is not None:
            existing_year.text = str(year)
        else:
            ET.SubElement(self.metadata, 'publication_year').text = str(year)
        self.required_fields['publication_year'] = True

    def set_version(self, version: str):
        """Set the version of the dataset."""
        self._validate_non_empty_string(version, "Version")
        existing_version = self.metadata.find('version')
        if existing_version is not None:
            existing_version.text = version
        else:
            ET.SubElement(self.metadata, 'version').text = version

    def add_alternate_title(self, title: str, title_type: Optional[str] = None):
        """Add an alternate title to the dataset."""
        self._validate_non_empty_string(title, "Alternate title")
        alternate_title = ET.SubElement(self.metadata, 'alternate_title')
        ET.SubElement(alternate_title, 'title').text = title
        if title_type:
            self._validate_non_empty_string(title_type, "Title type")
            ET.SubElement(alternate_title, 'title_type').text = title_type

    def add_subject(self, subject: str, scheme: Optional[str] = None):
        """Add a subject/keyword to the dataset."""
        self._validate_non_empty_string(subject, "Subject")
        subject_elem = ET.SubElement(self.metadata, 'subject')
        ET.SubElement(subject_elem, 'subject_value').text = subject
        if scheme:
            self._validate_non_empty_string(scheme, "Subject scheme")
            ET.SubElement(subject_elem, 'subject_scheme').text = scheme

    def add_agent_relationship(self, agent_name: str, role: str, agent_type: str = "person"):
        """Add an agent relationship (e.g., creator, contributor)."""
        self._validate_non_empty_string(agent_name, "Agent name")
        self._validate_non_empty_string(role, "Role")
        self._validate_non_empty_string(agent_type, "Agent type")
        relationship = ET.SubElement(self.metadata, 'qualified_relation')
        ET.SubElement(relationship, 'agent_name').text = agent_name
        ET.SubElement(relationship, 'role').text = role
        ET.SubElement(relationship, 'agent_type').text = agent_type

    def add_distribution(self, access_url: str, format_type: Optional[str] = None):
        """Add a distribution (access point) for the dataset."""
        self._validate_uri(access_url)
        distribution = ET.SubElement(self.metadata, 'distribution')
        ET.SubElement(distribution, 'access_url').text = access_url
        if format_type:
            self._validate_non_empty_string(format_type, "Format type")
            ET.SubElement(distribution, 'format').text = format_type

    def add_location(self, location: str, location_type: Optional[str] = None):
        """Add a geographical location for the dataset."""
        self._validate_non_empty_string(location, "Location")
        location_elem = ET.SubElement(self.metadata, 'location')
        ET.SubElement(location_elem, 'location_value').text = location
        if location_type:
            self._validate_non_empty_string(location_type, "Location type")
            ET.SubElement(location_elem, 'location_type').text = location_type

    def add_time_reference(self, time_value: str, time_type: str = "created"):
        """Add a time reference for the dataset."""
        self._validate_non_empty_string(time_value, "Time value")
        self._validate_non_empty_string(time_type, "Time type")
        time_ref = ET.SubElement(self.metadata, 'time_reference')
        ET.SubElement(time_ref, 'time_value').text = time_value
        ET.SubElement(time_ref, 'time_type').text = time_type

    def validate_required_fields(self) -> Dict[str, bool]:
        """Validate that all required fields are present."""
        validation_result = {}
        for field, is_set in self.required_fields.items():
            validation_result[field] = is_set
        return validation_result

    def is_valid(self) -> bool:
        """Check if all required fields are filled and validate against XSD schema."""
        # Check required fields
        if not all(self.required_fields.values()):
            return False
        
        # Reorder elements before validation
        self._reorder_elements()
        
        # Validate against XSD schema
        try:
            return self.validate_against_xsd("dataset/schema.xsd")
        except Exception as e:
            print(f"XSD validation error: {e}")
            return False

    def to_xml_string(self, pretty_print: bool = True) -> str:
        """Convert metadata to XML string."""
        # Reorder elements to match XSD schema
        self._reorder_elements()
        if pretty_print:
            self._indent(self.metadata)
        return ET.tostring(self.metadata, encoding='unicode')

    def save_to_file(self, file_path: str):
        """Save metadata to XML file."""
        self._reorder_elements()
        self._indent(self.metadata)
        tree = ET.ElementTree(self.metadata)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)

    def _indent(self, elem, level=0):
        """Helper method to format XML with proper indentation."""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def get_field_value(self, field_name: str) -> Optional[str]:
        """Get the value of a specific field."""
        element = self.metadata.find(field_name)
        return element.text if element is not None else None

    def get_all_fields(self) -> Dict[str, Any]:
        """Get all fields as a dictionary."""
        result = {}
        for child in self.metadata:
            if child.tag not in result:
                result[child.tag] = []
            if len(child) > 0:
                child_dict = {}
                for grandchild in child:
                    child_dict[grandchild.tag] = grandchild.text
                result[child.tag].append(child_dict)
            else:
                result[child.tag].append(child.text)
        return result
    
    def _validate_identifier(self, identifier: str):
        """Validate identifier format."""
        if not identifier or not identifier.strip():
            raise ValueError("Identifier cannot be empty.")
        if len(identifier) > 255:
            raise ValueError("Identifier is too long (max 255 characters).")
    
    def _validate_uri(self, uri: str):
        """Validate URI format."""
        if not uri or not uri.strip():
            raise ValueError("URI cannot be empty.")
        try:
            result = urlparse(uri)
            if not result.scheme or not result.netloc:
                raise ValueError(f"Invalid URI format: {uri}")
        except Exception as e:
            raise ValueError(f"Invalid URI format: {uri} - {e}")
    
    def _validate_year(self, year: int):
        """Validate publication year."""
        current_year = datetime.now().year
        if year < 1000 or year > current_year + 10:
            raise ValueError(f"Publication year must be between 1000 and {current_year + 10}.")
    
    def _validate_email(self, email: str):
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError(f"Invalid email format: {email}")
    
    def _validate_non_empty_string(self, value: str, field_name: str):
        """Validate that string is not empty."""
        if not value or not value.strip():
            raise ValueError(f"{field_name} cannot be empty.")
    
    def _reorder_elements(self):
        """Reorder elements to match XSD schema sequence."""
        # XSD sequence order according to dataset/schema.xsd
        xsd_order = [
            'iri', 'publication_year', 'version', 'title', 'has_description', 'alternate_title',
            'is_described_by', 'identifier', 'location', 'provenance', 'qualified_relation',
            'time_reference', 'subject', 'validation_result', 'distribution', 'funding_reference',
            'terms_of_use', 'related_resource', 'resource_type', 'other_language', 'primary_language'
        ]
        
        # Map our element names to XSD names
        element_mapping = {
            'has_description': 'has_description',
            'alternate_title': 'alternate_title',
            'identifier': 'identifier',
            'location': 'location',
            'qualified_relation': 'qualified_relation',
            'time_reference': 'time_reference',
            'subject': 'subject',
            'distribution': 'distribution'
        }
        
        # Collect all elements
        elements = {}
        for child in list(self.metadata):
            mapped_name = element_mapping.get(child.tag, child.tag)
            if mapped_name not in elements:
                elements[mapped_name] = []
            elements[mapped_name].append(child)
        
        # Clear all children
        self.metadata.clear()
        
        # Add elements in XSD order
        for element_name in xsd_order:
            if element_name in elements:
                for element in elements[element_name]:
                    self.metadata.append(element)
