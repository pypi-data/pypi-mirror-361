import unittest
from petri_net_core.petrinet.pnet import PNet
from petri_net_core.petrinet.pnet import InvalidTransitionFiredException
import copy
from jsonschema.exceptions import ValidationError
from petri_net_core.petrinet.pnet_validator import UnknownPlaceException

##  python -m unittest tests/pnet_tests.py  -v

## TODO adicionar teste de que tudo continua funcionando mesmo com transições que não possuem places consumidos ou places produzidos

pnet_dict={
  "places": {
    "p_A": 10,
    "p_B": 30,
    "p_C": 0,
    "p_D": 0
  },
  "transitions":{
      "t_1":{
        "consume": {
          "p_A": 1,
          "p_B": 2
        },
        "produce": {
          "p_C": 1
        }
      },
      "t_2":{
        "consume": {
          "p_B": 1,
          "p_C": 1
        },
        "produce": {
          "p_D": 2
        }
      }
  }
}

class PNetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.simple_ok_pnet=pnet_dict
        return super().setUp()

    def test_correct_build_given_valid_input(self):
        OkPnet=PNet(self.simple_ok_pnet)
        self.assertEqual(OkPnet.dict_places['p_A'],10)
        self.assertEqual(OkPnet.dict_places['p_B'],30)
        self.assertEqual(OkPnet.dict_places['p_C'],0)
        self.assertEqual(OkPnet.dict_places['p_D'],0)
        self.assertEqual(OkPnet.transitions_dict['t_1']['consume']["p_A"],1)
        self.assertEqual(OkPnet.transitions_dict['t_1']['consume']["p_B"],2)
        self.assertEqual(OkPnet.transitions_dict['t_1']['produce']["p_C"],1)
        self.assertEqual(OkPnet.transitions_dict['t_2']['consume']["p_B"],1)
        self.assertEqual(OkPnet.transitions_dict['t_2']['consume']["p_C"],1)
        self.assertEqual(OkPnet.transitions_dict['t_2']['produce']["p_D"],2)
    
    def test_rejects_invalid_schema_1(self):
        invalid_pnet=copy.deepcopy(self.simple_ok_pnet)
        del invalid_pnet['places']
        with self.assertRaises(ValidationError):
            PNet(invalid_pnet)
    
    def test_rejects_invalid_schema_2(self):
        invalid_pnet=copy.deepcopy(self.simple_ok_pnet)
        del invalid_pnet['transitions']
        with self.assertRaises(ValidationError):
            PNet(invalid_pnet)
    
    def test_rejects_invalid_schema_3(self):
        invalid_pnet=copy.deepcopy(self.simple_ok_pnet)
        del invalid_pnet['places']['p_B']
        invalid_pnet['places']['p_B+']=30
        with self.assertRaises(ValidationError):
            PNet(invalid_pnet)
    
    def test_rejects_invalid_schema_negative_tokens(self):
        invalid_pnet=copy.deepcopy(self.simple_ok_pnet)
        invalid_pnet['places']['p_B']=-3
        with self.assertRaises(ValidationError):
            PNet(invalid_pnet)

    def test_rejects_invalid_schema_fractional_tokens(self):
        invalid_pnet=copy.deepcopy(self.simple_ok_pnet)
        invalid_pnet['places']['p_B']=3.5
        with self.assertRaises(ValidationError):
            PNet(invalid_pnet)

    def test_rejects_inconsistent_transitions(self):
        invalid_pnet=copy.deepcopy(self.simple_ok_pnet)
        del invalid_pnet['transitions']['t_1'] ['consume']['p_A']
        invalid_pnet['transitions']['t_1'] ['consume']['p_X']=1
        with self.assertRaises(UnknownPlaceException):
            PNet(invalid_pnet)

    def test_runs_steps_correctly(self):
        OkPnet=PNet(self.simple_ok_pnet)
        OkPnet.custom_valid_step(step_transition_t1)
        self.assertEqual(OkPnet.dict_places['p_A'],9)
        self.assertEqual(OkPnet.dict_places['p_B'],28)
        self.assertEqual(OkPnet.dict_places['p_C'],1)

    def test_rejects_invalid_step(self):
        OkPnet=PNet(self.simple_ok_pnet)
        for i in range(10):
          OkPnet.custom_valid_step(step_transition_t1)
        self.assertEqual(OkPnet.dict_places['p_A'],0)
        with self.assertRaises(InvalidTransitionFiredException):
          OkPnet.custom_valid_step(step_transition_t1)  
        
            

def step_transition_t1(dict_places, valid_transitions):
    return 't_1'

def step_transition_t2(dict_places, valid_transitions):
    return 't_2'

def insecure_step_function(dict_places, valid_transitions):
    dict_places['p_A']=1
    return 't_1'


if __name__ == '__main__':
    unittest.main()