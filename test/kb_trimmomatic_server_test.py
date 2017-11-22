# -*- coding: utf-8 -*-
import unittest
import os
import json
import time
import requests
requests.packages.urllib3.disable_warnings()

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint

from requests_toolbelt import MultipartEncoder
from biokbase.workspace.client import Workspace as workspaceService
from biokbase.AbstractHandle.Client import AbstractHandle as HandleService

from kb_trimmomatic.kb_trimmomaticImpl import kb_trimmomatic
from kb_trimmomatic.kb_trimmomaticServer import MethodContext
from kb_trimmomatic.authclient import KBaseAuth as _KBaseAuth


class kb_trimmomaticTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        cls.token = token
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_trimmomatic'):
            cls.cfg[nameval[0]] = nameval[1]
        authServiceUrl = cls.cfg.get('auth-service-url',
                "https://kbase.us/services/authorization/Sessions/Login")
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(cls.token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_trimmomatic',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.shockURL = cls.cfg['shock-url']
        cls.handleURL = cls.cfg['handle-service-url']
        cls.serviceWizardURL = cls.cfg['service-wizard-url']

        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = kb_trimmomatic(cls.cfg)


    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')
        if hasattr(cls, 'shock_ids'):
            for shock_id in cls.shock_ids:
                print('Deleting SHOCK node: '+str(shock_id))
                cls.delete_shock_node(shock_id)

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


    @classmethod
    def upload_file_to_shock(cls, file_path):
        """
        Use HTTP multi-part POST to save a file to a SHOCK instance.
        """

        header = dict()
        header["Authorization"] = "Oauth {0}".format(cls.token)

        if file_path is None:
            raise Exception("No file given for upload to SHOCK!")
        if not file_path.startswith(os.sep):
            file_path = os.path.join(os.sep, 'kb','module','test',file_path)

        with open(os.path.abspath(file_path), 'rb') as dataFile:
            files = {'upload': dataFile}
            response = requests.post(
                cls.shockURL + '/node', headers=header, files=files,
                stream=True, allow_redirects=True, timeout=30)

        if not response.ok:
            response.raise_for_status()

        result = response.json()

        if result['error']:
            raise Exception(result['error'][0])
        else:
            shock_id = result['data']['id']
            if not hasattr(cls, 'shock_ids'):
                cls.shock_ids = []
            cls.shock_ids.append(shock_id)

            return result["data"]

    @classmethod
    def delete_shock_node(cls, node_id):
        header = {'Authorization': 'Oauth {0}'.format(cls.token)}
        requests.delete(cls.shockURL + '/node/' + node_id, headers=header,
                        allow_redirects=True)
        print('Deleted shock node ' + node_id)


    def getSingleEndLibInfo(self, read_lib_basename, lib_i=0):
        if hasattr(self.__class__, 'singleEndLibInfo_list'):
            try:
                info = self.__class__.singleEndLibInfo_list[lib_i]
                name = self.__class__.singleEndLibName_list[lib_i]
                if info != None:
                    if name != read_lib_basename:
                        self.__class__.singleEndLib_SetInfo[lib_i] = None
                        self.__class__.singleEndLib_SetName[lib_i] = None
                    else:
                        return info
            except:
                pass

        # 1) upload files to shock
        token = self.ctx['token']
        forward_shock_file = self.upload_file_to_shock('data/'+read_lib_basename+'.fwd.fq')
        #pprint(forward_shock_file)

        # 2) create handle
        hs = HandleService(url=self.handleURL, token=token)
        forward_handle = hs.persist_handle({
                                        'id' : forward_shock_file['id'],
                                        'type' : 'shock',
                                        'url' : self.shockURL,
                                        'file_name': forward_shock_file['file']['name'],
                                        'remote_md5': forward_shock_file['file']['checksum']['md5']})

        # 3) save to WS
        single_end_library = {
            'lib': {
                'file': {
                    'hid':forward_handle,
                    'file_name': forward_shock_file['file']['name'],
                    'id': forward_shock_file['id'],
                    'url': self.shockURL,
                    'type':'shock',
                    'remote_md5':forward_shock_file['file']['checksum']['md5']
                },
                'encoding':'UTF8',
                'type':'fastq',
                'size':forward_shock_file['file']['size']
            },
            'sequencing_tech':'artificial reads'
        }

        new_obj_info = self.wsClient.save_objects({
                        'workspace':self.getWsName(),
                        'objects':[
                            {
                                'type':'KBaseFile.SingleEndLibrary',
                                'data':single_end_library,
                                'name':'test-'+str(lib_i)+'.se.reads',
                                'meta':{},
                                'provenance':[
                                    {
                                        'service':'kb_trimmomatic',
                                        'method':'test_runTrimmomatic'
                                    }
                                ]
                            }]
                        })[0]

        # store it
        if not hasattr(self.__class__, 'singleEndLibInfo_list'):
            self.__class__.singleEndLibInfo_list = []
            self.__class__.singleEndLibName_list = []
        for i in range(lib_i+1):
            try:
                assigned = self.__class__.singleEndLibInfo_list[i]
            except:
                self.__class__.singleEndLibInfo_list.append(None)
                self.__class__.singleEndLibName_list.append(None)

        self.__class__.singleEndLibInfo_list[lib_i] = new_obj_info
        self.__class__.singleEndLibName_list[lib_i] = read_lib_basename
        return new_obj_info


    def getPairedEndLibInfo(self, read_lib_basename, lib_i=0):
        if hasattr(self.__class__, 'pairedEndLibInfo_list'):
            try:
                info = self.__class__.pairedEndLibInfo_list[lib_i]
                name = self.__class__.pairedEndLibName_list[lib_i]
                if info != None:
                    if name != read_lib_basename:
                        self.__class__.singleEndLibInfo_list[lib_i] = None
                        self.__class__.singleEndLibName_list[lib_i] = None
                    else:
                        return info
            except:
                pass

        # 1) upload files to shock
        token = self.ctx['token']
        forward_shock_file = self.upload_file_to_shock('data/'+read_lib_basename+'.fwd.fq')
        reverse_shock_file = self.upload_file_to_shock('data/'+read_lib_basename+'.rev.fq')
        #pprint(forward_shock_file)
        #pprint(reverse_shock_file)

        # 2) create handle
        hs = HandleService(url=self.handleURL, token=token)
        forward_handle = hs.persist_handle({
                                        'id' : forward_shock_file['id'],
                                        'type' : 'shock',
                                        'url' : self.shockURL,
                                        'file_name': forward_shock_file['file']['name'],
                                        'remote_md5': forward_shock_file['file']['checksum']['md5']})

        reverse_handle = hs.persist_handle({
                                        'id' : reverse_shock_file['id'],
                                        'type' : 'shock',
                                        'url' : self.shockURL,
                                        'file_name': reverse_shock_file['file']['name'],
                                        'remote_md5': reverse_shock_file['file']['checksum']['md5']})

        # 3) save to WS
        paired_end_library = {
            'lib1': {
                'file': {
                    'hid':forward_handle,
                    'file_name': forward_shock_file['file']['name'],
                    'id': forward_shock_file['id'],
                    'url': self.shockURL,
                    'type':'shock',
                    'remote_md5':forward_shock_file['file']['checksum']['md5']
                },
                'encoding':'UTF8',
                'type':'fastq',
                'size':forward_shock_file['file']['size']
            },
            'lib2': {
                'file': {
                    'hid':reverse_handle,
                    'file_name': reverse_shock_file['file']['name'],
                    'id': reverse_shock_file['id'],
                    'url': self.shockURL,
                    'type':'shock',
                    'remote_md5':reverse_shock_file['file']['checksum']['md5']
                },
                'encoding':'UTF8',
                'type':'fastq',
                'size':reverse_shock_file['file']['size']

            },
            'interleaved':0,
            'sequencing_tech':'artificial reads'
        }

        new_obj_info = self.wsClient.save_objects({
                        'workspace':self.getWsName(),
                        'objects':[
                            {
                                'type':'KBaseFile.PairedEndLibrary',
                                'data':paired_end_library,
                                'name':'test-'+str(lib_i)+'.pe.reads',
                                'meta':{},
                                'provenance':[
                                    {
                                        'service':'kb_trimmomatic',
                                        'method':'test_runTrimmomatic'
                                    }
                                ]
                            }]
                        })[0]

        # store it
        if not hasattr(self.__class__, 'pairedEndLibInfo_list'):
            self.__class__.pairedEndLibInfo_list = []
            self.__class__.pairedEndLibName_list = []
        for i in range(lib_i+1):
            try:
                assigned = self.__class__.pairedEndLibInfo_list[i]
            except:
                self.__class__.pairedEndLibInfo_list.append(None)
                self.__class__.pairedEndLibName_list.append(None)

        self.__class__.pairedEndLibInfo_list[lib_i] = new_obj_info
        self.__class__.pairedEndLibName_list[lib_i] = read_lib_basename
        return new_obj_info

    def getSingleEndLib_SampleSetInfo(self, read_libs_basename_list, refresh=False):
        if hasattr(self.__class__, 'singleEndLib_SampleSetInfo'):
            try:
                info = self.__class__.singleEndLib_SampleSetInfo
                if info != None:
                    if refresh:
                        self.__class__.singleEndLib_SampleSetInfo = None
                    else:
                        return info
            except:
                pass

        sample_ids = list()
        conditions = list()
        for lib_i, read_lib_basename in enumerate(read_libs_basename_list):
            label = read_lib_basename
            lib_info = self.getSingleEndLibInfo(read_lib_basename, lib_i)
            lib_ref = str(lib_info[6])+'/'+str(lib_info[0])
            print ("LIB_REF["+str(lib_i)+"]: "+lib_ref+" "+read_lib_basename)  # DEBUG
            sample_ids.append(lib_ref)
            conditions.append(label)
        desc = "test sample set"
        name = "TEST_SAMPLE_SET"
        sampleset_obj = {
            "sample_ids": sample_ids,
            "condition": conditions,
            "sampleset_id": "foo",
            "sampleset_desc": desc,
            "domain": "prokaryota",
            "num_samples": len(sample_ids),
            "Library_type": "SingleEnd"
        }
        sample_set_info = self.wsClient.save_objects({
            "workspace": self.getWsName(),
            "objects": [{
                "type": "KBaseRNASeq.RNASeqSampleSet",
                "data": sampleset_obj,
                "name": name,
                "meta": {},
                "provenance": [
                    {
                        "service": "kb_trimmomatic",
                        "method": "test_runTrimmomatic"
                    }
                ]
            }]
        })[0]
        # store it
        self.__class__.singleEndLib_SampleSetInfo = sample_set_info
        return sample_set_info

    # call this method to get the WS object info of a Single End Library Set (will
    # upload the example data if this is the first time the method is called during tests)
    def getSingleEndLib_SetInfo(self, read_libs_basename_list, refresh=False):
        if hasattr(self.__class__, 'singleEndLib_SetInfo'):
            try:
                info = self.__class__.singleEndLib_SetInfo
                if info != None:
                    if refresh:
                        self.__class__.singleEndLib_SetInfo = None
                    else:
                        return info
            except:
                pass

        # build items and save each PairedEndLib
        items = []
        for lib_i,read_lib_basename in enumerate (read_libs_basename_list):
            label    = read_lib_basename
            lib_info = self.getSingleEndLibInfo (read_lib_basename, lib_i)
            lib_ref  = str(lib_info[6])+'/'+str(lib_info[0])
            print ("LIB_REF["+str(lib_i)+"]: "+lib_ref+" "+read_lib_basename)  # DEBUG

            items.append({'ref': lib_ref,
                          'label': label
                          #'data_attachment': ,
                          #'info':
                         })

        # save readsset
        desc = 'test ReadsSet'
        readsSet_obj = { 'description': desc,
                         'items': items
                       }
        name = 'TEST_READSET'

        new_obj_info = self.wsClient.save_objects({
                        'workspace':self.getWsName(),
                        'objects':[
                            {
                                'type':'KBaseSets.ReadsSet',
                                'data':readsSet_obj,
                                'name':name,
                                'meta':{},
                                'provenance':[
                                    {
                                        'service':'kb_trimmomatic',
                                        'method':'test_runTrimmomatic'
                                    }
                                ]
                            }]
                        })[0]

        # store it
        self.__class__.singleEndLib_SetInfo = new_obj_info
        return new_obj_info


    # call this method to get the WS object info of a Paired End Library Set (will
    # upload the example data if this is the first time the method is called during tests)
    def getPairedEndLib_SetInfo(self, read_libs_basename_list, refresh=False):
        if hasattr(self.__class__, 'pairedEndLib_SetInfo'):
            try:
                info = self.__class__.pairedEndLib_SetInfo
                if info != None:
                    if refresh:
                        self.__class__.pairedEndLib_SetInfo[lib_i] = None
                    else:
                        return info
            except:
                pass

        # build items and save each PairedEndLib
        items = []
        for lib_i,read_lib_basename in enumerate (read_libs_basename_list):
            label    = read_lib_basename
            lib_info = self.getPairedEndLibInfo (read_lib_basename, lib_i)
            lib_ref  = str(lib_info[6])+'/'+str(lib_info[0])
            print ("LIB_REF["+str(lib_i)+"]: "+lib_ref+" "+read_lib_basename)  # DEBUG

            items.append({'ref': lib_ref,
                          'label': label
                          #'data_attachment': ,
                          #'info':
                         })

        # save readsset
        desc = 'test ReadsSet'
        readsSet_obj = { 'description': desc,
                         'items': items
                       }
        name = 'TEST_READSET'

        new_obj_info = self.wsClient.save_objects({
                        'workspace':self.getWsName(),
                        'objects':[
                            {
                                'type':'KBaseSets.ReadsSet',
                                'data':readsSet_obj,
                                'name':name,
                                'meta':{},
                                'provenance':[
                                    {
                                        'service':'kb_trimmomatic',
                                        'method':'test_runTrimmomatic'
                                    }
                                ]
                            }]
                        })[0]

        # store it
        self.__class__.pairedEndLib_SetInfo = new_obj_info
        return new_obj_info


    ##############
    # UNIT TESTS #
    ##############


    # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    #
    # Prepare test objects in workspace if needed using
    # self.getWsClient().save_objects({'workspace': self.getWsName(), 'objects': []})
    #
    # Run your method by
    # ret = self.getImpl().your_method(self.getContext(), parameters...)
    #
    # Check returned data with
    # self.assertEqual(ret[...], ...) or other unittest methods

        # Object Info Contents
        # 0 - obj_id objid
        # 1 - obj_name name
        # 2 - type_string type
        # 3 - timestamp save_date
        # 4 - int version
        # 5 - username saved_by
        # 6 - ws_id wsid
        # 7 - ws_name workspace
        # 8 - string chsum
        # 9 - int size
        # 10 - usermeta meta


    ### TEST 1: run Trimmomatic against just one single end library
    #
    # Uncomment to skip this test
    #HIDE @unittest.skip("skipped test_runTrimmomatic_SingleEndLibrary()")
    def test_runTrimmomatic_SingleEndLibrary(self):

        print ("\n\nRUNNING: test_runTrimmomatic_SingleEndLibrary()")
        print ("===============================================\n\n")

        # figure out where the test data lives
        se_lib_info = self.getSingleEndLibInfo('test_quick')
        pprint(se_lib_info)

        # run method
        output_name = 'output_trim.SElib'
        params = {
            'input_ws': se_lib_info[7],
            'output_ws': se_lib_info[7],
            'input_reads_ref': str(se_lib_info[6])+'/'+str(se_lib_info[0]),
            'output_reads_name': output_name,
            #'read_type': 'SE',
            #'quality_encoding': 'phred33',
            'translate_to_phred33': 1,
            'adapter_clip': {
                'adapterFa': None,
                'seed_mismatches': None,
                'palindrom_clip_threshold': None,
                'simple_clip_threshold': None
                },
            'sliding_window': {
                'sliding_window_size': 4,
                'sliding_window_min_size': 15
                },
            'leading_min_quality': 3,
            'trailing_min_quality': 3,
            'crop_length': 0,
            'head_crop_length': 0,
            'min_length': 36
        }

        result = self.getImpl().runTrimmomatic(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        single_output_name = output_name
        info_list = self.wsClient.get_object_info([{'ref':se_lib_info[7] + '/' + single_output_name}], 1)
        self.assertEqual(len(info_list),1)
        trimmed_reads_info = info_list[0]
        self.assertEqual(trimmed_reads_info[1],single_output_name)
        self.assertEqual(trimmed_reads_info[2].split('-')[0],'KBaseFile.SingleEndLibrary')


    ### TEST 2: run Trimmomatic against just one paired end library
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_runTrimmomatic_PairedEndLibrary()")
    def test_runTrimmomatic_PairedEndLibrary(self):

        print ("\n\nRUNNING: test_runTrimmomatic_PairedEndLibrary()")
        print ("\n=============================================\n\n")

        # figure out where the test data lives
        pe_lib_info = self.getPairedEndLibInfo('test_quick')
        pprint(pe_lib_info)

        # run method
        output_name = 'output_trim.PElib'
        params = {
            'input_ws': pe_lib_info[7],
            'output_ws': pe_lib_info[7],
            'input_reads_ref': str(pe_lib_info[6])+'/'+str(pe_lib_info[0]),
            'output_reads_name': output_name,
            #'read_type': 'PE',
            #'quality_encoding': 'phred33',
            'translate_to_phred33': 1,
            'adapter_clip': {
                'adapterFa': None,
                'seed_mismatches': None,
                'palindrom_clip_threshold': None,
                'simple_clip_threshold': None
                },
            'sliding_window': {
                'sliding_window_size': 4,
                'sliding_window_min_size': 15
                },
            'leading_min_quality': 3,
            'trailing_min_quality': 3,
            'crop_length': 0,
            'head_crop_length': 0,
            'min_length': 36
        }

        result = self.getImpl().runTrimmomatic(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        paired_output_name = output_name + '_paired'
        info_list = self.wsClient.get_object_info([{'ref':pe_lib_info[7] + '/' + paired_output_name}], 1)
        self.assertEqual(len(info_list),1)
        trimmed_reads_info = info_list[0]
        self.assertEqual(trimmed_reads_info[1],paired_output_name)
        self.assertEqual(trimmed_reads_info[2].split('-')[0],'KBaseFile.PairedEndLibrary')


    ### TEST 3: run Trimmomatic against a Single End Library reads set
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_runTrimmomatic_SingleEndLibrary_ReadsSet()")
    def test_runTrimmomatic_SingleEndLibrary_ReadsSet(self):

        print ("\n\nRUNNING: test_runTrimmomatic_SingleEndLibrary_ReadsSet()")
        print ("========================================================\n\n")

        # figure out where the test data lives
        se_lib_set_info = self.getSingleEndLib_SetInfo(['test_quick','small_2'])
        pprint(se_lib_set_info)

        # run method
        output_name = 'output_trim.SElib'
        params = {
            'input_ws': se_lib_set_info[7],
            'output_ws': se_lib_set_info[7],
            'input_reads_ref': str(se_lib_set_info[6])+'/'+str(se_lib_set_info[0]),
            'output_reads_name': output_name,
            #'read_type': 'SE',
            #'quality_encoding': 'phred33',
            'translate_to_phred33': 1,
            'adapter_clip': {
                'adapterFa': None,
                'seed_mismatches': None,
                'palindrom_clip_threshold': None,
                'simple_clip_threshold':  None
                },
            'sliding_window': {
                'sliding_window_size': 4,
                'sliding_window_min_size': 15
                },
            'leading_min_quality': 3,
            'trailing_min_quality': 3,
            'crop_length': 0,
            'head_crop_length': 0,
            'min_length': 36
        }

        result = self.getImpl().runTrimmomatic(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        single_output_name = output_name + '_trimm'
        info_list = self.wsClient.get_object_info([{'ref':se_lib_set_info[7] + '/' + single_output_name}], 1)
        self.assertEqual(len(info_list),1)
        trimmed_reads_info = info_list[0]
        self.assertEqual(trimmed_reads_info[1],single_output_name)
        self.assertEqual(trimmed_reads_info[2].split('-')[0],'KBaseSets.ReadsSet')


    ### TEST 4: run Trimmomatic against a Paired End Library reads set
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_runTrimmomatic_PairedEndLibrary_ReadsSet()")
    def test_runTrimmomatic_PairedEndLibrary_ReadsSet(self):

        print ("\n\nRUNNING: test_runTrimmomatic_PairedEndLibrary_ReadsSet()")
        print ("========================================================\n\n")

        # figure out where the test data lives
        pe_lib_set_info = self.getPairedEndLib_SetInfo(['test_quick','small_2'])
        pprint(pe_lib_set_info)

        # run method
        output_name = 'output_trim.PElib'
        params = {
            'input_ws': pe_lib_set_info[7],
            'output_ws': pe_lib_set_info[7],
            'input_reads_ref': str(pe_lib_set_info[6])+'/'+str(pe_lib_set_info[0]),
            'output_reads_name': output_name,
            #'read_type': 'PE',
            #'quality_encoding': 'phred33',
            'translate_to_phred33': 1,
            'adapter_clip': {
                'adapterFa': None,
                'seed_mismatches': None,
                'palindrom_clip_threshold': None,
                'simple_clip_threshold':  None
                },
            'sliding_window': {
                'sliding_window_size': 4,
                'sliding_window_min_size': 15
                },
            'leading_min_quality': 3,
            'trailing_min_quality': 3,
            'crop_length': 0,
            'head_crop_length': 0,
            'min_length': 36
        }

        result = self.getImpl().runTrimmomatic(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        paired_output_name = output_name + '_trimm_paired'
        info_list = self.wsClient.get_object_info([{'ref':pe_lib_set_info[7] + '/' + paired_output_name}], 1)
        self.assertEqual(len(info_list),1)
        trimmed_reads_info = info_list[0]
        self.assertEqual(trimmed_reads_info[1],paired_output_name)
        self.assertEqual(trimmed_reads_info[2].split('-')[0],'KBaseSets.ReadsSet')


    ### TEST 5: run Trimmomatic against a Single End Library sample set
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_runTrimmomatic_SingleEndLibrary_SampleSet()")
    def test_runTrimmomatic_SingleEndLibrary_SampleSet(self):

        print ("\n\nRUNNING: test_runTrimmomatic_SingleEndLibrary_SampleSet()")
        print ("========================================================\n\n")

        # figure out where the test data lives
        se_lib_sampleset_info = self.getSingleEndLib_SampleSetInfo(['test_quick', 'small_2'])
        pprint(se_lib_sampleset_info)

        # run method
        output_name = 'output_trim.SElib'
        params = {
            'input_ws': se_lib_sampleset_info[7],
            'output_ws': se_lib_sampleset_info[7],
            'input_reads_ref': str(se_lib_sampleset_info[6])+'/'+str(se_lib_sampleset_info[0]),
            'output_reads_name': output_name,
            #'read_type': 'SE',
            #'quality_encoding': 'phred33',
            'translate_to_phred33': 1,
            'adapter_clip': {
                'adapterFa': None,
                'seed_mismatches': None,
                'palindrom_clip_threshold': None,
                'simple_clip_threshold':  None
                },
            'sliding_window': {
                'sliding_window_size': 4,
                'sliding_window_min_size': 15
                },
            'leading_min_quality': 3,
            'trailing_min_quality': 3,
            'crop_length': 0,
            'head_crop_length': 0,
            'min_length': 36
        }

        result = self.getImpl().runTrimmomatic(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        single_output_name = output_name + '_trimm'
        info_list = self.wsClient.get_object_info([{'ref':se_lib_sampleset_info[7] + '/' + single_output_name}], 1)
        self.assertEqual(len(info_list),1)
        trimmed_reads_info = info_list[0]
        self.assertEqual(trimmed_reads_info[1],single_output_name)
        self.assertEqual(trimmed_reads_info[2].split('-')[0],'KBaseSets.ReadsSet')


    ### TEST 6: run Trimmomatic with data that doesn't get trimmed, check report output.
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_runTrimmomatic_SingleEndLibrary_no_trimming()")
    def test_runTrimmomatic_SingleEndLibrary_no_trimming(self):
        print("\n\nRUNNING: test_runTrimmomatic_SingleEndLibrary_no_trimming")
        print("---------------------------------------------------------\n\n")

        # figure out where the test data lives
        se_lib_info = self.getSingleEndLibInfo('small_no_trim')
        #se_lib_info = self.getSingleEndLibInfo('test_quick')
        pprint(se_lib_info)

        # run method
        output_name = 'output_no_trim.SElib'
        params = {
            'input_ws': se_lib_info[7],
            'output_ws': se_lib_info[7],
            'input_reads_ref': str(se_lib_info[6])+'/'+str(se_lib_info[0]),
            'output_reads_name': output_name,
            #'read_type': 'SE',
            #'quality_encoding': 'phred33',
            'translate_to_phred33': 1,
            'adapter_clip': {
                'adapterFa': None,
                'seed_mismatches': None,
                'palindrom_clip_threshold': None,
                'simple_clip_threshold': None
                },
            'sliding_window': {
                'sliding_window_size': 4,
                'sliding_window_min_size': 15
                },
            'leading_min_quality': 3,
            'trailing_min_quality': 3,
            'crop_length': 0,
            'head_crop_length': 0,
            'min_length': 36
        }

        result = self.getImpl().runTrimmomatic(self.getContext(),params)
        # check the output
        single_output_name = output_name
        info_list = self.wsClient.get_object_info([{'ref':se_lib_info[7] + '/' + single_output_name}], 1)
        self.assertEqual(len(info_list),1)
        trimmed_reads_info = info_list[0]
        self.assertEqual(trimmed_reads_info[1],single_output_name)
        self.assertEqual(trimmed_reads_info[2].split('-')[0],'KBaseFile.SingleEndLibrary')


    ### TEST 7: run Trimmomatic with data that gets completely trimmed, check report output.
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_runTrimmomatic_SingleEndLibrary_all_trimming()")
    def test_runTrimmomatic_SingleEndLibrary_all_trimming(self):
        print("\n\nRUNNING: test_runTrimmomatic_SingleEndLibrary_all_trimming")
        print("---------------------------------------------------------\n\n")

        # figure out where the test data lives
        se_lib_info = self.getSingleEndLibInfo('small_all_trim')
        #se_lib_info = self.getSingleEndLibInfo('test_quick')
        pprint(se_lib_info)

        # run method
        output_name = 'output_all_trim.SElib'
        params = {
            'input_ws': se_lib_info[7],
            'output_ws': se_lib_info[7],
            'input_reads_ref': str(se_lib_info[6])+'/'+str(se_lib_info[0]),
            'output_reads_name': output_name,
            #'read_type': 'SE',
            #'quality_encoding': 'phred33',
            'translate_to_phred33': 1,
            'adapter_clip': {
                'adapterFa': None,
                'seed_mismatches': None,
                'palindrom_clip_threshold': None,
                'simple_clip_threshold': None
                },
            'sliding_window': {
                'sliding_window_size': 4,
                'sliding_window_min_size': 15
                },
            'leading_min_quality': 3,
            'trailing_min_quality': 30,
            'crop_length': 0,
            'head_crop_length': 0,
            'min_length': 1000
        }

        result = self.getImpl().runTrimmomatic(self.getContext(), params)

        # check the output, ensure it ends as a no-op
        with self.assertRaises(Exception):
            self.wsClient.get_object_info([{'ref': se_lib_info[7] + '/' + output_name}], 1)
        report_obj = self.wsClient.get_objects([{'ref': result[0]['report_ref']}])[0]
        # moved to separate HTML object, so can't just read buf
        #self.assertIn('Input Reads', report_obj['data']['direct_html'])
        #self.assertIn('Surviving', report_obj['data']['direct_html'])
        #self.assertIn('Dropped', report_obj['data']['direct_html'])


    ### TEST 8: run Trimmomatic with q64 data that gets translated to q33
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_runTrimmomatic_SingleEndLibrary_q64_to_q33()")
    def test_runTrimmomatic_SingleEndLibrary_translate_q64_to_q33(self):
        print("\n\nRUNNING: test_runTrimmomatic_SingleEndLibrary_translate_q64_to_q33")
        print("------------------------------------------------------------------\n\n")

        # figure out where the test data lives
        se_lib_info = self.getSingleEndLibInfo('small_all_trim')  # q64
        pprint(se_lib_info)

        # run method
        output_name = 'output_trim_q64_to_q33.SElib'
        params = {
            'input_ws': se_lib_info[7],
            'output_ws': se_lib_info[7],
            'input_reads_ref': str(se_lib_info[6])+'/'+str(se_lib_info[0]),
            'output_reads_name': output_name,
            #'read_type': 'SE',
            #'quality_encoding': 'phred33',
            'translate_to_phred33': 1,
            'adapter_clip': {
                'adapterFa': None,
                'seed_mismatches': None,
                'palindrom_clip_threshold': None,
                'simple_clip_threshold': None
                },
            'sliding_window': {
                'sliding_window_size': 4,
                'sliding_window_min_size': 15
                },
            'leading_min_quality': 3,
            'trailing_min_quality': 3,
            'crop_length': 0,
            'head_crop_length': 0,
            'min_length': 20
        }

        result = self.getImpl().runTrimmomatic(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        single_output_name = output_name
        info_list = self.wsClient.get_object_info([{'ref':se_lib_info[7] + '/' + single_output_name}], 1)
        self.assertEqual(len(info_list),1)
        trimmed_reads_info = info_list[0]
        self.assertEqual(trimmed_reads_info[1],single_output_name)
        self.assertEqual(trimmed_reads_info[2].split('-')[0],'KBaseFile.SingleEndLibrary')
