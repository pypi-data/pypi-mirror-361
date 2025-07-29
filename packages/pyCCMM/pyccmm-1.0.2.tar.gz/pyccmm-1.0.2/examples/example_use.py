#!/usr/bin/env python3
"""
Příklad použití CCMM datových modelů
"""

from pyccmm.ccmm_models import *
import xml.etree.ElementTree as ET
from datetime import date


def main():
    # Vytvoření identifikátorů
    identifiers = [
        Identifier(value="10.1234/example", scheme=IdentifierScheme.DOI),
        Identifier(value="https://orcid.org/0000-0001-2345-6789", scheme=IdentifierScheme.ORCID)
    ]
    
    # Vytvoření alternatních titulů
    alternate_titles = [
        AlternateTitle(
            titles=[MultiLanguageText(text="Alternativní titul", language=Language.CS)],
            alternate_title_type="ExampleType"
        )
    ]

    # Vytvoření popisů
    descriptions = [
        Description(
            description_text="Toto je popis datasetu.",
            description_type="GeneralDescription"
        )
    ]

    # Vytvoření subjektů
    subjects = [
        Subject(
            titles=[
                MultiLanguageText(text="Matematika", language=Language.CS),
                MultiLanguageText(text="Mathematics", language=Language.EN)
            ],
            classification_code="01",
            subject_scheme=SubjectScheme.CLASSIFICATION
        )
    ]

    # Vytvoření vztahů agent-resource
    agents = [
        Agent(name="Jan Novák", agent_type=AgentType.PERSON)
    ]
    relationships = [
        ResourceToAgentRelationship(agent=agents[0], role=AgentRole.CREATOR)
    ]

    # Vytvoření časových referencí
    time_references = [
        TimeReference(time_value="2023-01-01", time_type=TimeReferenceType.CREATED)
    ]

    # Vytvoření metadatového záznamu
    metadata_records = [
        MetadataRecord(
            qualified_relations=relationships,
            date_created=date(2023, 1, 1)
        )
    ]

    # Sestavení datasetu
    dataset = Dataset(
        title="Příklad datasetu",
        publication_year=2023,
        identifiers=identifiers,
        alternate_titles=alternate_titles,
        descriptions=descriptions,
        subjects=subjects,
        metadata_records=metadata_records,
        qualified_relations=relationships,
        time_references=time_references
    )

    # Export do XML
    xml_elem = dataset.to_xml_element()
    xml_str = ET.tostring(xml_elem, encoding='unicode')
    print(xml_str)


if __name__ == "__main__":
    main()

