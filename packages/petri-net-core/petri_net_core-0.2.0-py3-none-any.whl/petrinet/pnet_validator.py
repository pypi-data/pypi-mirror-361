from jsonschema import validate as jsonschemavalidate
import json
import os.path as path

class PNetValidator():
    def __init__(self):
        pass
    
    @classmethod
    def validate_schema(cls, json_object_to_validate:dict):
        pnet_json_schema_path=path.join('.','petrinet','pnet_schema.json')
        with open(pnet_json_schema_path,'r') as pnet_json_schema_path:
            pnet_json_schema=json.load(pnet_json_schema_path)
            jsonschemavalidate(json_object_to_validate,schema=pnet_json_schema)

    '''
    Validate that the transitions do not reference unknown places
    '''
    @classmethod
    def validate_integrity(cls, pnet_def:dict):
        pnet_places=pnet_def['places']
        helpful_error_strings=[]
        for transition_key in pnet_def['transitions']:
            transition=pnet_def['transitions'][transition_key]
            for consumed_place in transition['consume']:
                if consumed_place not in pnet_places:
                    helpful_error_strings.append(f'Unknown consumed place {consumed_place} in transition {transition_key}')            
            for produced_place in transition['produce']:
                if produced_place not in pnet_places:
                    helpful_error_strings.append(f'Unknown produced place {produced_place} in transition {transition_key}')            
        if len(helpful_error_strings)>0:
            raise UnknownPlaceException('\n'+'\n'.join(helpful_error_strings))

class UnknownPlaceException(Exception):
    pass