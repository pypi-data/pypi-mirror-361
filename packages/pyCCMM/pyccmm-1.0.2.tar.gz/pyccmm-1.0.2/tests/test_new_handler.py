#!/usr/bin/env python3
"""
Test of the new CCMM Handler with Python objects
"""

from pyccmm.ccmm_handler import CCMMHandler
from pyccmm.ccmm_models import *
from datetime import date


def main():
    print("=== Test of the new CCMM Handler ===")
    
    # Create handler
    handler = CCMMHandler()
    
    # Set basic information
    handler.set_title("Test dataset with new handler")
    handler.set_publication_year(2024)
    handler.set_version("1.0")
    handler.set_primary_language(Language.CS)
    handler.add_other_language(Language.EN)
    
    # Add identifiers
    handler.add_identifier("10.1234/test", IdentifierScheme.DOI, "https://doi.org/10.1234/test")
    handler.add_identifier("ark:/12345/test", IdentifierScheme.ARK)
    
    # Add descriptions
    handler.add_description("This is a test dataset for the new CCMM handler.")
    handler.add_description("Another description of the dataset.", "TechnicalDescription")
    
    # Add alternate titles
    handler.add_alternate_title("Test Dataset", Language.EN)
    handler.add_alternate_title("Dataset di Test", Language.IT)
    
    # Add subjects
    handler.add_subject("Python", Language.EN, "001", SubjectScheme.CLASSIFICATION)
    handler.add_subject("metadata", Language.EN, subject_scheme=SubjectScheme.KEYWORD)
    handler.add_subject("CCMM", Language.CS, subject_scheme=SubjectScheme.KEYWORD)
    
    # Add agents
    handler.add_agent_relationship("Roman Dvořák", AgentRole.CREATOR, AgentType.PERSON)
    handler.add_agent_relationship("Technical University", AgentRole.PUBLISHER, AgentType.ORGANIZATION)
    
    # Add time references
    handler.add_time_reference("2024-01-01", TimeReferenceType.CREATED)
    handler.add_time_reference("2024-07-09", TimeReferenceType.UPDATED)
    
    # Add locations
    handler.add_location("Prague, Czech Republic", LocationType.PLACE)
    
    # Add distributions
    handler.add_distribution("https://example.com/dataset.csv", DistributionFormat.CSV, "CSV data")
    handler.add_distribution("https://example.com/dataset.json", DistributionFormat.JSON, "JSON data")
    
    # Add metadata record
    metadata_agent = Agent(name="Cataloguer", agent_type=AgentType.PERSON)
    metadata_relationship = ResourceToAgentRelationship(agent=metadata_agent, role=AgentRole.CURATOR)
    handler.add_metadata_record(
        qualified_relations=[metadata_relationship],
        date_created=date(2024, 1, 1),
        languages=[Language.CS, Language.EN]
    )
    
    # Show summary
    print("\n=== Dataset summary ===")
    summary = handler.get_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Validation test
    print("\n=== Validation ===")
    if handler.is_valid():
        print("✅ Dataset is valid!")
    else:
        print("❌ Dataset is not valid")
    
    # XML export
    print("\n=== XML Export ===")
    xml_output = handler.to_xml_string()
    print(xml_output[:500] + "..." if len(xml_output) > 500 else xml_output)
    
    # Save to file
    handler.save_to_file("test_new_dataset.xml")
    print("\n✅ Dataset saved to 'test_new_dataset.xml'")
    
    # Enum test
    print("\n=== Available Enums ===")
    print(f"Languages: {[lang.value for lang in Language]}")
    print(f"Agent types: {[agent.value for agent in AgentType]}")
    print(f"Agent roles: {[role.value for role in AgentRole]}")
    print(f"Identifier schemes: {[scheme.value for scheme in IdentifierScheme]}")
    print(f"Time reference types: {[time_type.value for time_type in TimeReferenceType]}")


if __name__ == "__main__":
    main()
