#!/usr/bin/env python3
"""
Ukázkový soubor pro použití CCMMHandler třídy
"""

from pyccmm.ccmm_handler import CCMMHandler
from pyccmm.ccmm_models import IdentifierScheme, AgentRole, AgentType, TimeReferenceType, LocationType, Language, DistributionFormat

def main():
    # Inicializace handleru metadat
    handler = CCMMHandler()
    
    # Nastavení základních povinných polí
    handler.set_title("Ukázkový dataset pro pyCCMM")
    handler.set_publication_year(2024)
    
    # Přidání identifikátoru
    handler.add_identifier("12345", IdentifierScheme.DOI, "https://doi.org/10.1234/example")
    
    # Přidání popisu
    handler.add_description("Tento dataset obsahuje ukázková data pro testování CCMM parseru.")
    
    # Přidání alternativního titulu
    handler.add_alternate_title("CCMM Example Dataset", Language.EN)
    
    # Přidání subjektů/klíčových slov
    handler.add_subject("metadata", Language.CS)
    handler.add_subject("dataset", Language.CS)
    handler.add_subject("parser", Language.CS)
    
    # Přidání vztahu k agentovi (autor)
    handler.add_agent_relationship("Roman Dvořák", AgentRole.CREATOR, AgentType.PERSON)
    
    # Přidání druhého vztahu k agentovi (XSD vyžaduje minOccurs=2)
    handler.add_agent_relationship("Jan Novák", AgentRole.CONTRIBUTOR, AgentType.PERSON)
    
    # Přidání distribuce
    handler.add_distribution("https://example.com/dataset", DistributionFormat.JSON)
    
    # Přidání lokace
    handler.add_location("Praha, Česká republika", LocationType.PLACE)
    
    # Přidání časové reference
    handler.add_time_reference("2024-01-01", TimeReferenceType.CREATED)
    
    # Přidání metadata record (povinné pole)
    handler.add_metadata_record(handler.get_agent_relationships())
    
    # Kontrola validity datasetu
    if handler.is_valid():
        print("\nDataset je validní!")
    else:
        print("\nDataset není validní - chybí povinná pole nebo neprošel XSD validací.")
    
    # Uložení do souboru
    handler.save_to_file("example_dataset.xml")
    print("\nDataset uložen do souboru 'example_dataset.xml'")
    
    # Zobrazení XML
    print("\nXML reprezentace:")
    print(handler.to_xml_string())
    
    # Zobrazení shrnutí datasetu
    print("\nShrnutí datasetu:")
    summary = handler.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
