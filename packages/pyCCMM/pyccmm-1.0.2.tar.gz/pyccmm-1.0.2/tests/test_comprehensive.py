#!/usr/bin/env python3
"""
Comprehensive test of the CCMM handler
"""

from pyccmm.ccmm_handler import CCMMHandler
from pyccmm.ccmm_models import *
from datetime import date

def create_full_dataset():
    """Creates a complete dataset with all available elements"""
    handler = CCMMHandler()
    
    # Basic information
    handler.set_title("Complete CCMM dataset")
    handler.set_publication_year(2024)
    handler.set_version("2.1.0")
    handler.set_iri("https://example.com/dataset/123")
    handler.set_primary_language(Language.CS)
    handler.add_other_language(Language.EN)
    handler.add_other_language(Language.DE)
    
    # Identifiers - various types
    handler.add_identifier("10.1234/comprehensive", IdentifierScheme.DOI, "https://doi.org/10.1234/comprehensive")
    handler.add_identifier("hdl:1234/dataset", IdentifierScheme.HANDLE, "https://hdl.handle.net/1234/dataset")
    handler.add_identifier("ark:/12345/comprehensive", IdentifierScheme.ARK)
    handler.add_identifier("550e8400-e29b-41d4-a716-446655440000", IdentifierScheme.UUID)
    
    # Descriptions - various types
    handler.add_description("Main description of the dataset for demonstrating CCMM functionality.")
    handler.add_description("Technical description of the implementation and architecture.", "TechnicalDescription")
    handler.add_description("Abstract of the research that led to the creation of this dataset.", "AbstractDescription")
    
    # Alternate titles
    handler.add_alternate_title("Comprehensive CCMM Dataset", Language.EN, "TranslatedTitle")
    handler.add_alternate_title("Vollständiger CCMM-Datensatz", Language.DE, "TranslatedTitle")
    handler.add_alternate_title("Dataset CCMM completo", Language.IT, "TranslatedTitle")
    
    # Subjects - various types
    handler.add_subject("Informatics", Language.CS, "01", SubjectScheme.CLASSIFICATION, "A scientific field dealing with information processing")
    handler.add_subject("Computer Science", Language.EN, "01", SubjectScheme.CLASSIFICATION, "Field of study dealing with information processing")
    handler.add_subject("metadata", Language.EN, subject_scheme=SubjectScheme.KEYWORD)
    handler.add_subject("CCMM", Language.CS, subject_scheme=SubjectScheme.KEYWORD)
    handler.add_subject("research data", Language.EN, subject_scheme=SubjectScheme.KEYWORD)
    handler.add_subject("research data", Language.CS, subject_scheme=SubjectScheme.KEYWORD)
    
    # Agents - various types and roles
    handler.add_agent_relationship("Prof. Jan Novak", AgentRole.CREATOR, AgentType.PERSON, agent_email="jan.novak@university.cz")
    handler.add_agent_relationship("Dr. Marie Svobodova", AgentRole.CONTRIBUTOR, AgentType.PERSON, agent_email="marie.svobodova@research.cz")
    handler.add_agent_relationship("Charles University", AgentRole.PUBLISHER, AgentType.ORGANIZATION)
    handler.add_agent_relationship("Technical Library", AgentRole.CURATOR, AgentType.ORGANIZATION)
    handler.add_agent_relationship("Ing. Petr Dvorak", AgentRole.CONTACT_PERSON, AgentType.PERSON, agent_email="petr.dvorak@tech.cz")
    
    # Time references
    handler.add_time_reference("2024-01-01", TimeReferenceType.CREATED)
    handler.add_time_reference("2024-06-15", TimeReferenceType.UPDATED)
    handler.add_time_reference("2024-07-01", TimeReferenceType.ISSUED)
    handler.add_time_reference("2024-07-09", TimeReferenceType.AVAILABLE)
    
    # Locations
    handler.add_location("Prague, Czech Republic", LocationType.PLACE)
    handler.add_location("Central Bohemia", LocationType.REGION)
    handler.add_location("Czech Republic", LocationType.COUNTRY)
    
    # Distributions - various formats
    handler.add_distribution("https://example.com/dataset.csv", DistributionFormat.CSV, "CSV data export", "Comma-separated values export")
    handler.add_distribution("https://example.com/dataset.json", DistributionFormat.JSON, "JSON data export", "JavaScript Object Notation export")
    handler.add_distribution("https://example.com/dataset.xml", DistributionFormat.XML, "XML data export", "eXtensible Markup Language export")
    handler.add_distribution("https://example.com/dataset.zip", DistributionFormat.ZIP, "Compressed data", "Zip archive with all files")
    
    # Metadata records
    metadata_agent1 = Agent(name="Cataloguer 1", agent_type=AgentType.PERSON)
    metadata_agent2 = Agent(name="Library XYZ", agent_type=AgentType.ORGANIZATION)
    metadata_rel1 = ResourceToAgentRelationship(agent=metadata_agent1, role=AgentRole.CURATOR)
    metadata_rel2 = ResourceToAgentRelationship(agent=metadata_agent2, role=AgentRole.PUBLISHER)
    
    handler.add_metadata_record(
        qualified_relations=[metadata_rel1, metadata_rel2],
        date_created=date(2024, 1, 1),
        date_updated=[date(2024, 6, 15), date(2024, 7, 9)],
        languages=[Language.CS, Language.EN, Language.DE]
    )
    
    return handler

def main():
    print("=== Comprehensive test of the CCMM handler ===")
    
    # Create the complete dataset
    handler = create_full_dataset()
    
    # Show summary
    print("\n=== Dataset summary ===")
    summary = handler.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Test all getters
    print("\n=== Getter test ===")
    print(f"Title: {handler.get_title()}")
    print(f"Publication year: {handler.get_publication_year()}")
    print(f"Number of identifiers: {len(handler.get_identifiers())}")
    print(f"Number of descriptions: {len(handler.get_descriptions())}")
    print(f"Number of subjects: {len(handler.get_subjects())}")
    print(f"Number of agents: {len(handler.get_agent_relationships())}")
    print(f"Number of distributions: {len(handler.get_distributions())}")
    
    # Export to file
    filename = "comprehensive_dataset.xml"
    handler.save_to_file(filename)
    print(f"\n✅ Dataset exported to '{filename}'")
    
    # Show first 1000 characters of XML
    xml_content = handler.to_xml_string()
    print(f"\n=== XML preview (first 1000 characters) ===")
    print(xml_content[:1000] + "..." if len(xml_content) > 1000 else xml_content)
    
    # Statistics
    print(f"\n=== Statistics ===")
    print(f"Total XML length: {len(xml_content)} characters")
    print(f"Number of XML lines: {xml_content.count(chr(10)) + 1}")
    
    # Test individual collections
    print(f"\n=== Identifier details ===")
    for i, identifier in enumerate(handler.get_identifiers(), 1):
        iri_part = f" ({identifier.iri})" if identifier.iri else ""
        print(f"  {i}. {identifier.scheme.value}: {identifier.value}{iri_part}")
    
    print(f"\n=== Subject details ===")
    for i, subject in enumerate(handler.get_subjects(), 1):
        title = subject.titles[0].text if subject.titles else "N/A"
        lang = subject.titles[0].language.value if subject.titles else "N/A"
        scheme = subject.subject_scheme.value if subject.subject_scheme else "N/A"
        print(f"  {i}. {title} ({lang}) - {scheme}")
    
    print(f"\n=== Agent details ===")
    for i, relationship in enumerate(handler.get_agent_relationships(), 1):
        agent_name = relationship.agent.name
        role = relationship.role.value
        agent_type = relationship.agent.agent_type.value
        print(f"  {i}. {agent_name} ({agent_type}) - {role}")

if __name__ == "__main__":
    main()
