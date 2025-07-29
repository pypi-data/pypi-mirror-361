#!/usr/bin/env python3
"""
Test file for validating CCMMMetadataHandler
"""

from pyccmm.ccmm_metadata_handler import CCMMMetadataHandler

def test_validation():
    handler = CCMMMetadataHandler()
    
    print("=== Test of input parameter validation ===")
    
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
        handler.add_identifier("", "DOI")
        print("❌ Empty identifier should not be accepted")
    except ValueError as e:
        print(f"✅ Empty identifier correctly rejected: {e}")
    
    print("\n=== Test of valid data ===")
    
    # Setting valid data
    handler.set_title("Test dataset")
    handler.set_publication_year(2024)
    handler.add_identifier("10.1234/test", "DOI", "https://doi.org/10.1234/test")
    handler.add_description("Test dataset description")
    handler.add_distribution("https://example.com/data", "text/csv")
    handler.add_agent_relationship("Test Author", "creator", "person")
    handler.add_subject("test", "keyword")
    handler.add_location("Prague", "city")
    handler.add_time_reference("2024-01-01", "created")
    
    print("✅ Valid data was successfully added")
    
    # Test validation of required fields
    validation_result = handler.validate_required_fields()
    print(f"Validation of required fields: {validation_result}")
    
    # Test overall validity (including XSD validation)
    print("\n=== Test XSD validation ===")
    if handler.is_valid():
        print("✅ Dataset passed overall validation (including XSD)")
    else:
        print("❌ Dataset did not pass overall validation")
    
    # Test multiple identifiers
    print("\n=== Test multiple identifiers ===")
    handler.add_identifier("handle123", "Handle", "https://hdl.handle.net/handle123")
    handler.add_identifier("ark:/12345/test", "ARK")
    
    print("✅ Multiple identifiers were successfully added")
    
    # Display final XML
    print("\n=== Final XML ===")
    print(handler.to_xml_string())

if __name__ == "__main__":
    test_validation()
