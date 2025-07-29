#!/usr/bin/env python3
"""
Test XSD validation
"""

from pyccmm.ccmm_handler import CCMMHandler
from pyccmm.ccmm_models import *
from datetime import date

def test_xsd_validation():
    print("=== Test XSD validation ===")
    
    handler = CCMMHandler()
    
    # Minimal dataset
    handler.set_title("Test dataset")
    handler.set_publication_year(2024)
    handler.add_identifier("10.1234/test", IdentifierScheme.DOI)
    handler.add_subject("test", Language.CS, subject_scheme=SubjectScheme.KEYWORD)
    handler.add_agent_relationship("Test Author", AgentRole.CREATOR)
    handler.add_time_reference("2024-01-01", TimeReferenceType.CREATED)
    
    # Metadata record
    metadata_agent = Agent(name="Cataloguer", agent_type=AgentType.PERSON)
    metadata_relationship = ResourceToAgentRelationship(agent=metadata_agent, role=AgentRole.CURATOR)
    handler.add_metadata_record([metadata_relationship])
    
    # Validation test
    print("Testing XSD validation...")
    is_valid = handler.is_valid()
    print(f"Result: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Export XML for manual check
    xml_content = handler.to_xml_string()
    print(f"\nXML (first 800 characters):")
    print(xml_content[:800])
    
    # Save for manual check (only if valid)
    if is_valid:
        handler.save_to_file("xsd_test.xml")
        print("\n✅ XML saved to 'xsd_test.xml'")
    else:
        # Save even if invalid for debugging
        with open("xsd_test.xml", "w") as f:
            f.write(xml_content)
        print("\n⚠️  XML saved to 'xsd_test.xml' (invalid but saved for debugging)")

if __name__ == "__main__":
    test_xsd_validation()
