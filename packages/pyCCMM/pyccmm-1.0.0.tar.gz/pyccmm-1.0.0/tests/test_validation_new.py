#!/usr/bin/env python3
"""
Input validation test for the new CCMM Handler
"""

from pyccmm.ccmm_handler import CCMMHandler
from pyccmm.ccmm_models import *

def test_validation():
    print("=== Input validation test ===")
    
    handler = CCMMHandler()
    
    # Test empty title
    try:
        handler.set_title("")
        print("❌ Empty title should not be accepted")
    except ValueError as e:
        print(f"✅ Empty title correctly rejected: {e}")
    
    # Test invalid year
    try:
        handler.set_publication_year(3000)
        print("❌ Year 3000 should not be accepted")
    except ValueError as e:
        print(f"✅ Invalid year correctly rejected: {e}")
    
    # Test invalid URI
    try:
        handler.add_distribution("invalid-uri")
        print("❌ Invalid URI should not be accepted")
    except ValueError as e:
        print(f"✅ Invalid URI correctly rejected: {e}")
    
    # Test empty identifier
    try:
        handler.add_identifier("", IdentifierScheme.DOI)
        print("❌ Empty identifier should not be accepted")
    except ValueError as e:
        print(f"✅ Empty identifier correctly rejected: {e}")
    
    # Test invalid email
    try:
        handler.add_agent_relationship("Test", AgentRole.CREATOR, agent_email="invalid-email")
        print("❌ Invalid email should not be accepted")
    except ValueError as e:
        print(f"✅ Invalid email correctly rejected: {e}")
    
    print("\n=== Test of valid data ===")
    
    # Set valid data
    handler.set_title("Test dataset")
    handler.set_publication_year(2024)
    handler.add_identifier("10.1234/test", IdentifierScheme.DOI)
    handler.add_description("Test description")
    handler.add_subject("test", Language.CS, subject_scheme=SubjectScheme.KEYWORD)
    handler.add_agent_relationship("Roman Dvořák", AgentRole.CREATOR, agent_email="roman@example.com")
    handler.add_time_reference("2024-01-01", TimeReferenceType.CREATED)
    
    # Metadata record
    metadata_agent = Agent(name="Cataloguer", agent_type=AgentType.PERSON)
    metadata_relationship = ResourceToAgentRelationship(agent=metadata_agent, role=AgentRole.CURATOR)
    handler.add_metadata_record([metadata_relationship])
    
    print("✅ Valid data was successfully added")
    
    # Show summary
    summary = handler.get_summary()
    print(f"Dataset contains:")
    print(f"  - {summary['identifiers_count']} identifiers")
    print(f"  - {summary['descriptions_count']} descriptions")
    print(f"  - {summary['subjects_count']} subjects")
    print(f"  - {summary['agents_count']} agents")
    
    print("\n=== Enum test ===")
    
    # Test that we can use all enums
    print("✅ Testing all available enums:")
    for lang in Language:
        print(f"  Language: {lang.value}")
        break  # Only the first one for brevity
    
    for scheme in IdentifierScheme:
        print(f"  Scheme: {scheme.value}")
        break
    
    for role in AgentRole:
        print(f"  Role: {role.value}")
        break
    
    print("\n=== Test of multiple identifiers ===")
    
    # Test multiple identifiers
    handler.add_identifier("handle123", IdentifierScheme.HANDLE)
    handler.add_identifier("ark:/12345/test", IdentifierScheme.ARK)
    handler.add_identifier("https://orcid.org/0000-0001-2345-6789", IdentifierScheme.ORCID)
    
    print(f"✅ The dataset now has {len(handler.get_identifiers())} identifiers")
    
    # Print all identifiers
    for i, identifier in enumerate(handler.get_identifiers(), 1):
        print(f"  {i}. {identifier.scheme.value}: {identifier.value}")

if __name__ == "__main__":
    test_validation()
