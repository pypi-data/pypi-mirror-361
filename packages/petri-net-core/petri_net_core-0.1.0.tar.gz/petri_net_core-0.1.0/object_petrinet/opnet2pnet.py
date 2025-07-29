


class ObjectPNet2PNetAdapter():
    def __init__(self, dict_definition):
        self.opnet_definition=dict_definition
        self.dependency_list={}
        self.__build_pnet_from_opnet()

    def __build_pnet_from_opnet(self):
        self.pnet_dict={}
        self.pnet_dict['places']={}
        self.pnet_dict['transitions']={}
        for pnet_name in self.opnet_definition:
            pnet=self.opnet_definition[pnet_name]
            for place_name in pnet['places']:
                self.__add_place(pnet_name,place_name)
            for transition_name in pnet['transitions']:
                self.__add_transition(pnet_name,transition_name)
    

    def __add_place(self,pnet_name:str,place_name:str):
        place=self.opnet_definition[pnet_name]['places'][place_name]
        place_is_dict=isinstance(place,dict)
        place_is_int=isinstance(place,int)
        if place_is_dict:
            tokens_in_place=place['tokens']
            self.pnet_dict['places'][self.get_adapted_pnet_place_name(pnet_name,place_name)]=tokens_in_place
            self.__add_dependency(pnet_name,place['pnet'])
        elif place_is_int:
            tokens_in_place=place
            self.pnet_dict['places'][self.get_adapted_pnet_place_name(pnet_name,place_name)]=tokens_in_place
        else:
            raise InvalidPlaceDefinition(f'Place {place_name} in pnet {pnet_name} is neither and int nor a dict')

    def __add_dependency(self,input_dependant_pnet:str,input_dependancy_pnet:str):
        if input_dependant_pnet not in self.dependency_list:
            self.dependency_list[input_dependant_pnet]=[]
        self.dependency_list[input_dependant_pnet].append(input_dependancy_pnet)
        dependant_pnet=input_dependancy_pnet
        #while dependant_pnet <> input_dependant_pnet:

    def __add_transition(self,pnet_name:str,transition_name:str):
        opnet_transition=self.opnet_definition[pnet_name]['transitions'][transition_name]
        if 't_' != transition_name[:2]:
           new_transition_name='t_'+transition_name 
        if new_transition_name not in self.pnet_dict['transitions']:
            self.pnet_dict['transitions'][new_transition_name]={
                'consume':{},
                'produce':{}
            }
        new_transition=self.pnet_dict['transitions'][new_transition_name]
        for place_name in opnet_transition['consume']:
            new_pnet_place_name=self.get_adapted_pnet_place_name(pnet_name,place_name)
            tokens_consumed=opnet_transition['consume'][place_name]
            new_transition['consume'][new_pnet_place_name]=tokens_consumed
        for place_name in opnet_transition['produce']:
            new_pnet_place_name=self.get_adapted_pnet_place_name(pnet_name,place_name)
            tokens_consumed=opnet_transition['produce'][place_name]
            new_transition['produce'][new_pnet_place_name]=tokens_consumed

    def get_adapted_pnet_place_name(self,pnet_name,place_name):
        return 'p_'+pnet_name+'__'+place_name

    def get_pnet_json_dict(self):
        return self.pnet_dict

class InvalidPlaceDefinition(Exception):
    pass