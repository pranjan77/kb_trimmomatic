import unittest
import os
import json
import time

from os import environ
from ConfigParser import ConfigParser
from pprint import pprint

from biokbase.workspace.client import Workspace as workspaceService
from kb_trimmomatic.kb_trimmomaticImpl import kb_trimmomatic


class kb_trimmomaticTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        cls.ctx = {'token': token, 'provenance': [{'service': 'kb_trimmomatic',
            'method': 'please_never_use_it_in_production', 'method_params': []}],
            'authenticated': 1}
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_trimmomatic'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = kb_trimmomatic(cls.cfg)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_kb_trimmomatic_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_trimmomatic_ok(self):
        print "run trim"
        #ctx={'token':self.token}
        input_params={}
        input_params['input_ws']='psdehal:1455758523413'
        input_params['input_read_library']='g460'
        input_params['read_type']='PE'
        input_params['quality_encoding']='phred33'
        input_params['adapterFa']='TruSeq3-PE.fa'
        input_params['seed_mismatches']='2'
        input_params['palindrome_clip_threshold']='30'
        input_params['simple_clip_threshold']='10'
        input_params['crop_length']='200'
        input_params['head_crop_length']='1'
        input_params['leading_min_quality']='1'
        input_params['trailing_min_quality']='1'
        input_params['sliding_window_size']='4'
        input_params['sliding_window_min_quality']='5'
        input_params['min_length']='80'
        input_params['output_read_library']='testing'
        input_params['output_ws'] = input_params['input_ws']
        result=self.getImpl().runTrimmomatic(self.getContext(), input_params)
        print result

        