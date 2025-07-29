import unittest
import object_petrinet.opnet as opnet
import petrinet.pnet_validator as pnet_validator
from object_petrinet.opnet_validator import UnknownPlaceException
from jsonschema.exceptions import ValidationError
import copy

##  python -m unittest tests/opnet_tests.py -v

json_input={
    "pnet1":{
      "places": {
        "m": {
            "pnet":"pnet2",
            "tokens":1
        },
        "p": 0
      },
      "transitions": 
        {
          "translation":{
              "consume": {
                "m": 1
              },
              "produce": {
                "p": 1
              }
          }
         }
      
    },
    "pnet2":{
      "places": {
        "m0": 1,
        "m1": 0,
        "m2": 0,
        "a":2
      },
      "transitions": 
        {
            "elongation_step1":{
              "consume": {
                "m0": 1,
                "a":1
              },
              "produce": {
                "m1": 1
              }
              },
            "elongation_step2":{
              "consume": {
                "m1": 1,
                "a":1
              },
              "produce": {
                "m2": 1
              }
              },
              "translation":{
              "consume": {
                "m2": 1
              },
              "produce":{}
            }
        }
    }
}

class OPNetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.opnet=opnet.ObjectPNet(json_input)
        return super().setUp()
    
    
    def test_rejects_invalid_schema_for_subpnet(self):
        invalid_opnet=copy.deepcopy(json_input)
        invalid_opnet['invalid_subpnet']=[]
        with self.assertRaises(ValidationError):
            opnet.ObjectPNet(invalid_opnet)
        del invalid_opnet['invalid_subpnet']
        invalid_opnet['invalid_subpnet']={
            'places':''
        }
        with self.assertRaises(ValidationError):
            opnet.ObjectPNet(invalid_opnet)
            
    def test_rejects_inconsistent_transitions(self):
        invalid_opnet=copy.deepcopy(json_input)
        invalid_opnet['pnet2']['transitions']['translation']['produce']['p']=1
        with self.assertRaises(ValidationError):
            opnet.ObjectPNet(UnknownPlaceException)
        
    def test_generates_valid_petrinet(self):
        pnet_json_dict=self.opnet.get_vanilla_pnet_def()
        pnet_validator.PNetValidator.validate_schema(pnet_json_dict)
        pnet_validator.PNetValidator.validate_integrity(pnet_json_dict)
        
    def test_access_opnet(self):
        self.opnet.reset()
        self.assertEqual(self.opnet.get_place_tokens('pnet1','m'),1)
        self.assertEqual(self.opnet.get_place_tokens('pnet1','p'),0)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','m0'),1)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','m1'),0)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','m2'),0)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','a'),2)

    def test_batch_access_opnet(self):
        self.opnet.reset()
        place_dict={
            'pnet1':['m','p'],
            'pnet2':['m2']
        }
        returned_dict=self.opnet.get_multiple_place_tokens(place_dict)
        self.assertDictEqual(returned_dict,{
            'pnet1':{'m':1,'p':0},
            'pnet2':{'m2':0},
        })
    
    def test_reset_opnet(self):
        self.opnet.simulate(1)
        self.opnet.reset()
        self.assertEqual(self.opnet.get_place_tokens('pnet1','m'),1)
        self.assertEqual(self.opnet.get_place_tokens('pnet1','p'),0)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','m0'),1)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','m1'),0)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','m2'),0)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','a'),2)

    def test_dynamic_opnet(self):        
        self.opnet.simulate(1)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','m0'),0)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','m1'),1)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','a'),1)
        self.opnet.simulate(2)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','m1'),0)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','m2'),1)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','a'),0)
        self.opnet.simulate(3)
        self.assertEqual(self.opnet.get_place_tokens('pnet2','m2'),0)
        self.assertEqual(self.opnet.get_place_tokens('pnet1','m'),0)
        self.assertEqual(self.opnet.get_place_tokens('pnet1','p'),1)
        self.assertListEqual(self.opnet.get_firing_sequence(),['t_elongation_step1', 't_elongation_step2', 't_translation'])
                
    



if __name__ == '__main__':
    unittest.main()