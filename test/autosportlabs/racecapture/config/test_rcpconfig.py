import unittest
import json
from autosportlabs.racecapture.config.rcpconfig import CANChannels, CANChannel, CANMapping

CAN_CHANNEL_1 = '{"nm":"CHAN1", "ut": "UNITS1", "min":-55, "max":55,"prec":2,"sr":25, "bm": false, "type":0, "bus":0, "id":1234, "idMask":0, "offset":23, "len":19, "mult":1.23, "div":3.45, "add":3, "bigEndian":false, "filtId": 3}'
CAN_CHANNEL_2 = '{"nm":"CHAN2", "ut": "UNITS2", "min":-66, "max":66,"prec":3,"sr":50, "bm": true, "type":0, "bus":1, "id":1235, "idMask":0, "offset":24, "len":20, "mult":1.24, "div":6.78, "add":4, "bigEndian":true, "filtId": 4}'
CAN_CHANNELS = '{"en": 1, "chans":[' + CAN_CHANNEL_1 + ',' + CAN_CHANNEL_2 + ']}'
 
class BaseConfigTest(unittest.TestCase):
    def to_json_string(self, json_dict):
        return json.dumps(json_dict, separators=(',', ':'))
    
    def from_json_string(self, json_string):
        return json.loads(json_string)

    def assert_dicts_equal(self, json_dict1, json_dict2):
        self.assertEqual(self.to_json_string(json_dict1), self.to_json_string(json_dict2))
        
class CANMappingTest(BaseConfigTest):
    def test_can_mapping(self):
        can_mapping_json_dict = self.from_json_string('{"bm": false, "type":0, "bus":0, "id":1234, "idMask":0, "offset":23, "len":19, "mult":1.23, "div":3.45, "add":3, "bigEndian":false, "filtId": 3}')
        can_mapping_json_dict_test = CANMapping().from_json_dict(can_mapping_json_dict).to_json_dict()
        self.assert_dicts_equal(can_mapping_json_dict, can_mapping_json_dict_test)

class CANChannelTest(BaseConfigTest):
    
    def test_CAN_channel(self):
        can_channel_1_json_dict = self.from_json_string(CAN_CHANNEL_1)
        can_channel_1_json_dict_test = CANChannel().from_json_dict(can_channel_1_json_dict).to_json_dict()
        self.assert_dicts_equal(can_channel_1_json_dict, can_channel_1_json_dict_test)
        
        can_channel_2_json_dict = self.from_json_string(CAN_CHANNEL_2)
        json_channel_2_test = CANChannel().from_json_dict(can_channel_2_json_dict).to_json_dict()
        self.assert_dicts_equal(can_channel_2_json_dict, json_channel_2_test)
        
class CANChannelsTest(BaseConfigTest):
    
    def test_CAN_channels(self):
        json_CAN_channels = self.from_json_string(CAN_CHANNELS)
        json_CAN_channels_test = CANChannels().from_json_dict(json_CAN_channels).to_json_dict()
        self.assert_dicts_equal({'canChanCfg': json_CAN_channels}, json_CAN_channels_test)