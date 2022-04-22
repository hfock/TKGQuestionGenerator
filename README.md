# Temporal Knowledge Graph Expansion with Natural Language Processing

The aim is to automatically expand resource description framework (RDF) triples (subject, predicate, object) to a temporal quadruple (subject, predicate, object, time-object). The time-object can be a date, DateTime, (left open] and [right open) time interval.

The automatisation has to be achieved by consulting a text2text-generation [Hugging Face](https://huggingface.co/) model with closed book questions, such as {'Question':'When was the Viennese St. Stephen's Cathedral built', 'Answer':'13th century'}

The data within the KGData folder was taken from the repository https://github.com/mniepert/mmkb/tree/master/TemporalKGs/wikidata.
