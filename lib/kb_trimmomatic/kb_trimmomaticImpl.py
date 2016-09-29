# -*- coding: utf-8 -*-
#BEGIN_HEADER
import sys
import traceback
from biokbase.workspace.client import Workspace as workspaceService
import requests
requests.packages.urllib3.disable_warnings()
import subprocess
import os
import re
from pprint import pprint, pformat
import uuid

# SDK Utils
#from ReadsUtils.ReadsUtilsClient import ReadsUtilsClient  # FIX
#from SetAPI.SetAPIClient import SetAPI
from SetAPI import SetAPIClient
#END_HEADER


class kb_trimmomatic:
    '''
    Module Name:
    kb_trimmomatic

    Module Description:
    A KBase module: kb_trimmomatic
This module contains two methods

runTrimmomatic() to backend a KBase App, potentially operating on ReadSets
execTrimmomatic() the local method that handles overloading Trimmomatic to run on a set or a single library
execTrimmomaticSingleLibrary() runs Trimmomatic on a single library
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    VERSION = "0.0.3"
    workspaceURL = None
    shockURL     = None
    handleURL    = None
    callbackURL  = None
    scratch      = None

    GIT_URL = "https://github.com/kbaseapps/kb_trimmomatic"
    GIT_COMMIT_HASH = "3194e03ae1604f39ad65fd3f61af4ea3bbf25a3a"
    
    #BEGIN_CLASS_HEADER
    workspaceURL = None
    TRIMMOMATIC = 'java -jar /kb/module/Trimmomatic-0.33/trimmomatic-0.33.jar'
    ADAPTER_DIR = '/kb/module/Trimmomatic-0.33/adapters/'

    def log(self, target, message):
        if target is not None:
            target.append(message)
        print(message)
        sys.stdout.flush()


    def parse_trimmomatic_steps(self, input_params):
        # validate input parameters and return string defining trimmomatic steps

        parameter_string = ''

        if 'read_type' not in input_params and input_params['read_type'] is not None:
            raise ValueError('read_type not defined')
        elif input_params['read_type'] not in ('PE', 'SE'):
            raise ValueError('read_type must be PE or SE')

        if 'quality_encoding' not in input_params and input_params['quality_encoding'] is not None:
            raise ValueError('quality_encoding not defined')
        elif input_params['quality_encoding'] not in ('phred33', 'phred64'):
            raise ValueError('quality_encoding must be phred33 or phred64')
            

        # set adapter trimming
        if ('adapterFa' in input_params and input_params['adapterFa'] is not None and
            'seed_mismatches' in input_params and input_params['seed_mismatches'] is not None and
            'palindrome_clip_threshold' in input_params and input_params['quality_encoding'] is not None and
            'simple_clip_threshold' in input_params and input_params['simple_clip_threshold'] is not None):
            parameter_string = ("ILLUMINACLIP:" + self.ADAPTER_DIR +
                                    ":".join( (str(input_params['adapterFa']),
                                       str(input_params['seed_mismatches']), 
                                       str(input_params['palindrome_clip_threshold']),
                                       str(input_params['simple_clip_threshold'])) ) + " " )
        elif ( ('adapterFa' in input_params and input_params['adapterFa'] is not None) or
               ('seed_mismatches' in input_params and input_params['seed_mismatches'] is not None) or
               ('palindrome_clip_threshold' in input_params and input_params['palindrome_clip_threshold'] is not None) or
               ('simple_clip_threshold' in input_params and input_params['simple_clip_threshold'] is not None) ):
            raise ValueError('Adapter Cliping requires Adapter, Seed Mismatches, Palindrome Clip Threshold and Simple Clip Threshold')

        # set Crop
        if 'crop_length' in input_params and input_params['crop_length'] is not None:
            parameter_string += 'CROP:' + str(input_params['crop_length']) + ' '

        # set Headcrop
        if 'head_crop_length' in input_params and input_params['head_crop_length'] is not None:
            parameter_string += 'HEADCROP:' + str(input_params['head_crop_length']) + ' '


        # set Leading
        if 'leading_min_quality' in input_params and input_params['leading_min_quality'] is not None:
            parameter_string += 'LEADING:' + str(input_params['leading_min_quality']) + ' '


        # set Trailing
        if 'trailing_min_quality' in input_params and input_params['trailing_min_quality'] is not None:
            parameter_string += 'TRAILING:' + str(input_params['trailing_min_quality']) + ' '


        # set sliding window
        if ('sliding_window_size' in input_params and input_params['sliding_window_size'] is not None and 
            'sliding_window_min_quality' in input_params and input_params['sliding_window_min_quality'] is not None):
            parameter_string += 'SLIDINGWINDOW:' + str(input_params['sliding_window_size']) + ":" + str(input_params['sliding_window_min_quality']) + ' '
        elif ( ('sliding_window_size' in input_params and input_params['sliding_window_size'] is not None) or 
               ('sliding_window_min_quality' in input_params and input_params['sliding_window_min_quality'] is not None) ):
            raise ValueError('Sliding Window filtering requires both Window Size and Window Minimum Quality to be set')
            

        # set min length
        if 'min_length' in input_params and input_params['min_length'] is not None:
            parameter_string += 'MINLEN:' + str(input_params['min_length']) + ' '

        if parameter_string == '':
            raise ValueError('No filtering/trimming steps specified!')

        return parameter_string

    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.workspaceURL = config['workspace-url']
        self.shockURL = config['shock-url']
        self.scratch = os.path.abspath(config['scratch'])
        self.handleURL = config['handle-service-url']

        #self.callbackURL = os.environ['SDK_CALLBACK_URL'] if os.environ['SDK_CALLBACK_URL'] != None else 'https://kbase.us/services/njs_wrapper'  # DEBUG
        self.callbackURL = os.environ.get('SDK_CALLBACK_URL')
        if self.callbackURL == None:
            raise ValueError ("SDK_CALLBACK_URL not set in environment")

        if not os.path.exists(self.scratch):
            os.makedirs(self.scratch)
        os.chdir(self.scratch)
        #END_CONSTRUCTOR
        pass
    

    def runTrimmomatic(self, ctx, input_params):
        """
        :param input_params: instance of type "runTrimmomaticInput"
           (runTrimmomatic() ** ** to backend a KBase App, potentially
           operating on ReadSets) -> structure: parameter "input_ws" of type
           "workspace_name" (** Common types), parameter "input_reads_name"
           of type "data_obj_name", parameter "output_ws" of type
           "workspace_name" (** Common types), parameter "output_reads_name"
           of type "data_obj_name", parameter "read_type" of String,
           parameter "adapterFa" of String, parameter "seed_mismatches" of
           Long, parameter "palindrome_clip_threshold" of Long, parameter
           "simple_clip_threshold" of Long, parameter "quality_encoding" of
           String, parameter "sliding_window_size" of Long, parameter
           "sliding_window_min_quality" of Long, parameter
           "leading_min_quality" of Long, parameter "trailing_min_quality" of
           Long, parameter "crop_length" of Long, parameter
           "head_crop_length" of Long, parameter "min_length" of Long
        :returns: instance of type "runTrimmomaticOutput" -> structure:
           parameter "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN runTrimmomatic
        console = []
        self.log(console, 'Running Trimmomatic with parameters: ')
        self.log(console, "\n"+pformat(input_params))

        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token)
        headers = {'Authorization': 'OAuth '+token}
        env = os.environ.copy()
        env['KB_AUTH_TOKEN'] = token

        # load provenance
        provenance = [{}]
        if 'provenance' in ctx:
            provenance = ctx['provenance']
        provenance[0]['input_ws_objects']=[str(input_params['input_ws'])+'/'+str(input_params['input_reads_name'])]

        # set up and run execTrimmomatic()
        #
        if ('output_ws' not in input_params or input_params['output_ws'] is None):
            input_params['output_ws'] = input_params['input_ws']


        execTrimmomaticParams = { 'input_reads_ref': str(input_params['input_ws']) + '/' + str(input_params['input_reads_name']),
                                  'output_ws': input_params['output_ws'],
                                  'output_reads_name': input_params['output_reads_name'],
                                  'read_type': input_params['read_type'],
                                  'adapterFa': input_params['adapterFa'],
                                  'seed_mismatches': input_params['seed_mismatces'],
                                  'palindrome_clip_threshold': input_params['palindrome_clip_threshold'],
                                  'simple_clip_threshold': input_params['simple_clip_threshold'],
                                  'quality_encoding': input_params['quality_encoding'],
                                  'sliding_window_size': input_params['sliding_window_size'],
                                  'sliding_window_min_quality': input_params['sliding_window_quality'],
                                  'leading_min_quality': input_params['leading_min_quality'],
                                  'trailing_min_quality': input_params['trailing_min_quality'],
                                  'crop_length': input_params['crop_length'],
                                  'head_crop_length': input_params['head_crop_olength'],
                                  'min_length': input_params['min_length']
                                  }

        trimmomatic_retVal = self.execTrimmomatic (execTrimmomaticParams)


        # build report
        #
        reportObj = {'objects_created':[], 
                     'text_message':''}

        # text report
        try:
            reportObj['text_message'] = trimmomatic_retVal['report']
        except:
            raise ValueError ("no report generated by execTrimmomatic()")

        # trimmed object
        try:
            reportObj['objects_created'].append({'ref':trimmomatic_retVal['output_filtered_ref'],
                                                 'description':'Trimmed Reads'})
        except:
            raise ValueError ("no trimmed output generated by execTrimmomatic()")

        # unpaired fwd
        try:
            reportObj['objects_created'].append({'ref':trimmomatic_retVal['output_unpaired_fwd_ref'],
                                                 'description':'Trimmed Unpaired Forward Reads'})
        except:
            pass

        # unpaired rev
        try:
            reportObj['objects_created'].append({'ref':trimmomatic_retVal['output_unpaired_rev_ref'],
                                                 'description':'Trimmed Unpaired Reverse Reads'})
        except:
            pass


        # save report object
        #
        reportName = 'trimmomatic_report_' + str(hex(uuid.getnode()))
        report_obj_info = wsClient.save_objects({
                'workspace': input_params['input_ws'],
                'objects':[
                    {
                        'type':'KBaseReport.Report',
                        'data':reportObj,
                        'name':reportName,
                        'meta':{},
                        'hidden':1,
                        'provenance':provenance
                    }
                ]
            })[0]

        output = { 'report_name': reportName, 'report_ref': str(report_obj_info[6]) + '/' + str(report_obj_info[0]) + '/' + str(report_obj_info[4]) }
        #END runTrimmomatic

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method runTrimmomatic return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def execTrimmomatic(self, ctx, input_params):
        """
        :param input_params: instance of type "execTrimmomaticInput"
           (execTrimmomatic() ** ** the local method that runs Trimmomatic on
           each read library) -> structure: parameter "input_reads_ref" of
           type "data_obj_ref", parameter "output_ws" of type
           "workspace_name" (** Common types), parameter "output_reads_name"
           of type "data_obj_name", parameter "read_type" of String,
           parameter "adapterFa" of String, parameter "seed_mismatches" of
           Long, parameter "palindrome_clip_threshold" of Long, parameter
           "simple_clip_threshold" of Long, parameter "quality_encoding" of
           String, parameter "sliding_window_size" of Long, parameter
           "sliding_window_min_quality" of Long, parameter
           "leading_min_quality" of Long, parameter "trailing_min_quality" of
           Long, parameter "crop_length" of Long, parameter
           "head_crop_length" of Long, parameter "min_length" of Long
        :returns: instance of type "execTrimmomaticOutput" -> structure:
           parameter "output_filtered_ref" of type "data_obj_ref", parameter
           "output_unpaired_fwd_ref" of type "data_obj_ref", parameter
           "output_unpaired_rev_ref" of type "data_obj_ref", parameter
           "report" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN execTrimmomatic
        console = []
        self.log(console, 'Running Trimmomatic with parameters: ')
        self.log(console, "\n"+pformat(input_params))
        report = ''
        trimmomatic_retVal = dict()
        trimmomatic_retVal['output_trimmed_ref'] = None
        trimmomatic_retVal['output_unpaired_fwd_ref'] = None
        trimmomatic_retVal['output_unpaired_rev_ref'] = None

        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token)
        headers = {'Authorization': 'OAuth '+token}
        env = os.environ.copy()
        env['KB_AUTH_TOKEN'] = token

        # param checks
        required_params = ['input_reads_ref', 
                           'output_ws', 
                           'output_reads_name', 
                           'read_type'
                          ]
        for required_param in required_params:
            if required_param not in input_params or input_params[required_param] == None:
                raise ValueError ("Must define required param: '"+required_param+"'")

        # load provenance
        provenance = [{}]
        if 'provenance' in ctx:
            provenance = ctx['provenance']
        # add additional info to provenance here, in this case the input data object reference
        provenance[0]['input_ws_objects']=[str(input_params['input_reads_ref'])]

        # Determine whether read library or read set is input object
        #
        try:
            # object_info tuple
            [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)

            input_reads_obj_type = wsClient.get_object_info_new ({'objects':[{'ref':input_params['input_reads_ref']}]})[0][TYPE_I]

        except Exception as e:
            raise ValueError('Unable to get read library object from workspace: (' + str(input_params['input_reads_ref']) +')' + str(e))

        acceptable_types = ["KBaseSets.ReadsSet", "KBaseFile.PairedEndLibrary", "KBaseAssembly.PairedEndLibrary", "KBaseAssembly.SingleEndLibrary", "KBaseFile.SingleEndLibrary"]
        if input_reads_obj_type not in acceptable_types:
            raise ValueError ("Input reads of type: '"+input_reads_obj_type+"'.  Must be one of "+", ".join(acceptable_types))


        # get set
        #
        readsSet_ref_list = []
        if input_reads_obj_type != "KBaseSets.ReadsSet":
            readsSet_ref_list = [input_params['input_reads_ref']]
        else:
            try:
                setAPI_Client = SetAPIClient (url=self.callbackURL, token=ctx['token'])
                readSet_obj = setAPI_Client.get_reads_set_v1 ({'ref':input_reads_ref})
                for readLibrary_obj in readSet_obj['items']:
                    readSet_ref_list.append(readLibrary_obj['ref'])
            except Exception as e:
                raise ValueError('SetAPI FAILURE: Unable to get read library set object from workspace: (' + str(input_params['input_reads_ref'])+')' + str(e))

        # Iterate through readLibrary memebers of set
        #
        report = ''
        trimmed_readSet = []
        unpaired_fwd_readSet = []
        unpaired_rev_readSet = []

        for input_reads_library_ref in readsSet_ref_list:
            execTrimmomaticParams = { 'input_reads_ref': input_reads_library_ref,
                                      'output_ws': input_params['output_ws'],
                                      'output_reads_name': input_params['output_reads_name'],
                                      'read_type': input_params['read_type'],
                                      'adapterFa': input_params['adapterFa'],
                                      'seed_mismatches': input_params['seed_mismatces'],
                                      'palindrome_clip_threshold': input_params['palindrome_clip_threshold'],
                                      'simple_clip_threshold': input_params['simple_clip_threshold'],
                                      'quality_encoding': input_params['quality_encoding'],
                                      'sliding_window_size': input_params['sliding_window_size'],
                                      'sliding_window_min_quality': input_params['sliding_window_quality'],
                                      'leading_min_quality': input_params['leading_min_quality'],
                                      'trailing_min_quality': input_params['trailing_min_quality'],
                                      'crop_length': input_params['crop_length'],
                                      'head_crop_length': input_params['head_crop_olength'],
                                      'min_length': input_params['min_length']
                                    }

            report += "RUNNING TRIMMOMATIC ON LIBRARY: "+str(input_reads_library_ref)+"\n"
            report += "--------------------------------\n\n"
            trimmomatic_retVal = self.execTrimmomaticSingleLibrary (execTrimmomaticParams)
            report += trimmomatic_retVal['report']+"\n\n"
            trimmed_readSet.append (trimmomatic_retVal['output_trimmed_ref'])
            unpaired_fwd_readSet.append (trimmomatic_retVal['output_unpaired_fwd_ref'])
            unpaired_rev_readSet.append (trimmomatic_retVal['output_unpaired_rev_ref'])

        
        # Single Library
        if input_reads_obj_type != "KBaseSets.ReadsSet":
            output = { 'report': report,
                       'output_filtered_ref': trimmomatic_retVal['output_filtered_ref'],
                       'output_unpaired_fwd_ref': trimmomatic_retVal['output_unpaired_fwd_ref'],
                       'output_unpaired_rev_ref': trimmomatic_retVal['output_unpaired_rev_ref']
                     }
        # ReadSet
        else:
            # save trimmed readSet
            items = []
            for lib_ref in trimmed_readSet:
                items.append({'ref': lib_ref,
                              'label': 'foo'   # FIX
                              #'data_attachment': ,
                              #'info':
                             })
                readSet_obj = { 'description': 'foo',  # FIX
                                'items': items
                              }
                trimmed_readSet_ref = setAPI_Client.save_reads_set_v1 ({'workspace_name': input_params['output_ws'],
                                                                        'output_object_name': str(input_params['output_reads_name'])+'_paired',
                                                                        'data': readSet_obj
                                                                       })['set_ref']
                              
            # save unpaired forward readSet
            if len(unpaired_fwd_readSet) > 0:
                items = []
                for lib_ref in trimmed_readSet:
                    items.append({'ref': lib_ref,
                                  'label': 'foo'   # FIX
                                  #'data_attachment': ,
                                  #'info':
                                 })
                    readSet_obj = { 'description': 'foo',  # FIX 
                                    'items': items
                                  }
                    unpaired_fwd_readSet_ref = setAPI_Client.save_reads_set_v1 ({'workspace_name': input_params['output_ws'],
                                                                                 'output_object_name': str(input_params['output_reads_name'])+'_unpaired_fwd',
                                                                                 'data': readSet_obj
                                                                               })['set_ref']
                              
            # save unpaired reverse readSet
            if len(unpaired_rev_readSet) > 0:
                items = []
                for lib_ref in trimmed_readSet:
                    items.append({'ref': lib_ref,
                                  'label': 'foo'   # FIX
                                  #'data_attachment': ,
                                  #'info':
                                 })
                    readSet_obj = { 'description': 'foo',  # FIX 
                                    'items': items
                                  }
                    unpaired_rev_readSet_ref = setAPI_Client.save_reads_set_v1 ({'workspace_name': input_params['output_ws'],
                                                                                 'output_object_name': str(input_params['output_reads_name'])+'_unpaired_rev',
                                                                                 'data': readSet_obj
                                                                               })['set_ref']
                              


            output = { 'report': report,
                       'output_filtered_ref': trimmed_readSet_ref,
                       'output_unpaired_fwd_ref': unpaired_fwd_readSet_ref,
                       'output_unpaired_rev_ref': unpaired_fwd_readSet_ref
                     }

        #END execTrimmomatic

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method execTrimmomatic return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def execTrimmomaticSingleLibrary(self, ctx, input_params):
        """
        :param input_params: instance of type "execTrimmomaticInput"
           (execTrimmomatic() ** ** the local method that runs Trimmomatic on
           each read library) -> structure: parameter "input_reads_ref" of
           type "data_obj_ref", parameter "output_ws" of type
           "workspace_name" (** Common types), parameter "output_reads_name"
           of type "data_obj_name", parameter "read_type" of String,
           parameter "adapterFa" of String, parameter "seed_mismatches" of
           Long, parameter "palindrome_clip_threshold" of Long, parameter
           "simple_clip_threshold" of Long, parameter "quality_encoding" of
           String, parameter "sliding_window_size" of Long, parameter
           "sliding_window_min_quality" of Long, parameter
           "leading_min_quality" of Long, parameter "trailing_min_quality" of
           Long, parameter "crop_length" of Long, parameter
           "head_crop_length" of Long, parameter "min_length" of Long
        :returns: instance of type "execTrimmomaticOutput" -> structure:
           parameter "output_filtered_ref" of type "data_obj_ref", parameter
           "output_unpaired_fwd_ref" of type "data_obj_ref", parameter
           "output_unpaired_rev_ref" of type "data_obj_ref", parameter
           "report" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN execTrimmomaticSingleLibrary
        console = []
        self.log(console, 'Running Trimmomatic with parameters: ')
        self.log(console, "\n"+pformat(input_params))
        report = ''
        retVal = dict()
        retVal['output_trimmed_ref'] = None
        retVal['output_unpaired_fwd_ref'] = None
        retVal['output_unpaired_rev_ref'] = None

        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token)
        headers = {'Authorization': 'OAuth '+token}
        env = os.environ.copy()
        env['KB_AUTH_TOKEN'] = token

        # param checks
        required_params = ['input_reads_ref', 
                           'output_ws', 
                           'output_reads_name', 
                           'read_type'
                          ]
        for required_param in required_params:
            if required_param not in input_params or input_params[required_param] == None:
                raise ValueError ("Must define required param: '"+required_param+"'")

        # and param defaults
        defaults = { 'quality_encoding':           'phred64',
                     'seed_mismatches':            '2',
                     'palindrom_clip_threshold':   '3',
                     'simple_clip_threshold':      '10',
                     'crop_length':                '0',
                     'head_crop_length':           '0',
                     'leading_min_quality':        '3',
                     'trailing_min_quality':       '3',
                     'sliding_window_size':        '4',
                     'sliding_window_min_quality': '15',
                     'min_length':                 '36'
                   }
        def default_params (params, arg, val):
            if arg not in params or params[arg] == None or params[arg] == '':
                return val
            else:
                return params[arg]

        for arg in defaults.keys():
            input_params[arg] = default_params (input_params, arg, defaults[arg])
            
        # conditional arg behavior
        arg = 'adapterFa'
        if arg not in params or params[arg] == None or params[arg] == '':
            input_params['seed_mismatches'] = None
            input_params['palindrom_clip_threshold'] = None
            input_params['simple_clip_threshold'] = None
            

        #load provenance
        provenance = [{}]
        if 'provenance' in ctx:
            provenance = ctx['provenance']
        # add additional info to provenance here, in this case the input data object reference
        provenance[0]['input_ws_objects']=[str(input_params['input_ws'])+'/'+str(input_params['input_reads_name'])]


        # Determine whether read library is of correct type
        #
        try:
            # object_info tuple
            [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)

            input_reads_obj_type = wsClient.get_object_info_new ({'objects':[{'ref':input_params['input_reads_ref']}]})[0][TYPE_I]

        except Exception as e:
            raise ValueError('Unable to get read library object from workspace: (' + str(input_params['input_reads_ref']) +')' + str(e))

        acceptable_types = ["KBaseFile.PairedEndLibrary", "KBaseAssembly.PairedEndLibrary", "KBaseAssembly.SingleEndLibrary", "KBaseFile.SingleEndLibrary"]
        if input_reads_obj_type not in acceptable_types:
            raise ValueError ("Input reads of type: '"+input_reads_obj_type+"'.  Must be one of "+", ".join(acceptable_types))


        # Confirm user is paying attention (matters because Trimmomatic params are very different for PairedEndLibary and SingleEndLibrary
        #
        if input_params['read_type'] == 'PE' \
                and (input_reads_obj_type == 'KBaseAssembly.SingleEndLibrary' \
                     or input_reads_obj_type == 'KBaseFile.SingleEndLibrary'):
            raise ValueError ("read_type set to 'Paired End' but object is SingleEndLibrary")
        if input_params['read_type'] == 'SE' \
                and (input_reads_obj_type == 'KBaseAssembly.PairedEndLibrary' \
                     or input_reads_obj_type == 'KBaseFile.PairedEndLibrary'):
            raise ValueError ("read_type set to 'Single End' but object is PairedEndLibrary")
            

        # Let's rock!
        #
        trimmomatic_params  = self.parse_trimmomatic_steps(input_params)
        trimmomatic_options = str(input_params['read_type']) + ' -' + str(input_params['quality_encoding'])

        self.log(console, pformat(trimmomatic_params))
        self.log(console, pformat(trimmomatic_options))


        #
        # FIX: USE ReadsUtils HERE INSTEAD
        #
        try:
            readLibrary = wsClient.get_objects([{'name': input_params['input_read_library'], 
                                                 'workspace' : input_params['input_ws']}])[0]
            info = readLibrary['info']

        except Exception as e:
            raise ValueError('Unable to get read library object from workspace: (' + str(input_params['input_ws'])+ '/' + str(input_params['input_read_library']) +')' + str(e))


        # PairedEndLibrary
        #
        if input_params['read_type'] == 'PE':

            fr_type = ''
            rv_type = ''
            if 'lib1' in readLibrary['data']:
                forward_reads = readLibrary['data']['lib1']['file']
                # type is required if lib1 is present
                fr_type = '.' + readLibrary['data']['lib1']['type']
            elif 'handle_1' in readLibrary['data']:
                forward_reads = readLibrary['data']['handle_1']
            if 'lib2' in readLibrary['data']:
                reverse_reads = readLibrary['data']['lib2']['file']
                # type is required if lib2 is present
                rv_type = '.' + readLibrary['data']['lib2']['type']
            elif 'handle_2' in readLibrary['data']:
                reverse_reads = readLibrary['data']['handle_2']
            else:
                reverse_reads={}

            fr_file_name = str(forward_reads['id']) + fr_type
            if 'file_name' in forward_reads:
                fr_file_name = forward_reads['file_name']

            self.log(console, "\nDownloading Paired End reads file...")
            forward_reads_file = open(fr_file_name, 'w', 0)
            print("cwd: " + str(os.getcwd()) )
            
            r = requests.get(forward_reads['url']+'/node/'+str(forward_reads['id'])+'?download', stream=True, headers=headers)
            for chunk in r.iter_content(1024):
                forward_reads_file.write(chunk)
            forward_reads_file.close()
            self.log(console, 'done\n')

            if 'interleaved' in readLibrary['data'] and readLibrary['data']['interleaved']:
                if re.search('gz', fr_file_name, re.I):
                    bcmdstring = 'gunzip -c ' + fr_file_name
                    self.log(console, "Reads are gzip'd and interleaved, uncompressing and deinterleaving.")
                else:    
                    bcmdstring = 'cat ' + fr_file_name 
                    self.log(console, "Reads are interleaved, deinterleaving.")

                
                cmdstring = bcmdstring + '| (paste - - - - - - - -  | tee >(cut -f 1-4 | tr "\t" "\n" > forward.fastq) | cut -f 5-8 | tr "\t" "\n" > reverse.fastq )'
                cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash')
                stdout, stderr = cmdProcess.communicate()

                # Check return status
                report = "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
                self.log(console, 'done\n')
                fr_file_name='forward.fastq'
                rev_file_name='reverse.fastq'
            else:
                self.log(console, 'Downloading reverse reads.')
                rev_file_name = str(reverse_reads['id']) + rv_type
                if 'file_name' in reverse_reads:
                    rev_file_name = reverse_reads['file_name']
                reverse_reads_file = open(rev_file_name, 'w', 0)

                r = requests.get(reverse_reads['url']+'/node/'+str(reverse_reads['id'])+'?download', stream=True, headers=headers)
                for chunk in r.iter_content(1024):
                    reverse_reads_file.write(chunk)
                reverse_reads_file.close()
                self.log(console, 'done\n')

                if re.search('gz', rev_file_name, re.I):
                    bcmdstring = 'gunzip ' + rev_file_name + ' ' + fr_file_name
                    self.log(console, "Reads are compressed, uncompressing.")
                    cmdProcess = subprocess.Popen(bcmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash')
                    stdout, stderr = cmdProcess.communicate()
                    self.log(console, "\n".join(stdout, stderr, "done"))
                    rev_file_name = re.sub(r'\.gz\Z', '', rev_file_name)
                    fr_file_name = re.sub(r'\.gz\Z', '', fr_file_name)

            cmdstring = " ".join( (self.TRIMMOMATIC, trimmomatic_options, 
                            fr_file_name, 
                            rev_file_name,
                            'forward_paired_'   +fr_file_name,
                            'unpaired_fwd_' +fr_file_name,
                            'reverse_paired_'   +rev_file_name,
                            'unpaired_rev_' +rev_file_name,
                            trimmomatic_params) )

            self.log(console, 'Starting Trimmomatic')
            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)


            outputlines = []

            while True:
                line = cmdProcess.stdout.readline()
                outputlines.append(line)
                if not line: break
                self.log(console, line.replace('\n', ''))

            cmdProcess.stdout.close()
            cmdProcess.wait()
            self.log(console, 'return code: ' + str(cmdProcess.returncode) + '\n')

            report += "\n".join(outputlines)
            #report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr " + stderr


            #get read counts
            match = re.search(r'Input Read Pairs: (\d+).*?Both Surviving: (\d+).*?Forward Only Surviving: (\d+).*?Reverse Only Surviving: (\d+).*?Dropped: (\d+)', report)
            input_read_count = match.group(1)
            read_count_paired = match.group(2)
            read_count_forward_only = match.group(3)
            read_count_reverse_only = match.group(4)
            read_count_dropped = match.group(5)

            report = "\n".join( ('Input Read Pairs: '+ input_read_count, 
                'Both Surviving: '+ read_count_paired, 
                'Forward Only Surviving: '+ read_count_forward_only,
                'Reverse Only Surviving: '+ read_count_reverse_only,
                'Dropped: '+ read_count_dropped) )

            #upload paired reads
            self.log(console, 'Uploading trimmed paired reads.')
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'forward_paired_' + fr_file_name, 
                                   '--inputfile2', 'reverse_paired_' + rev_file_name,
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', str(input_params['output_ws']),
                                   '--outobj', input_params['output_read_library'] + '_paired', '--readcount', read_count_paired ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            stdout, stderr = cmdProcess.communicate()
            print("cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr)
            #report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
            #reportObj['objects_created'].append({'ref':str(input_params['input_ws'])+'/'+input_params['output_read_library']+'_paired', 
            #            'description':'Trimmed Paired-End Reads'})
            retVal['output_filtered_ref'] = str(input_params['output_ws'])+'/'+str(input_params['output_reads_name']+'_paired')


            #upload reads forward unpaired
            self.log(console, '\nUploading trimmed unpaired forward reads.')
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'unpaired_fwd_' + fr_file_name, 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', str(input_params['output_ws']),
                                   '--outobj', input_params['output_read_library'] + '_unpaired_fwd', '--readcount', read_count_forward_only ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            stdout, stderr = cmdProcess.communicate()
            print("cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr)
            #report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
            #reportObj['objects_created'].append({'ref':str(input_params['input_ws'])+'/'+input_params['output_read_library']+'_unpaired_fwd', 
            #            'description':'Trimmed Unpaired Forward Reads'})
            retVal['output_unpaired_fwd_ref'] = str(input_params['output_ws'])+'/'+str(input_params['output_reads_name']+'_unpaired_fwd')


            #upload reads reverse unpaired
            self.log(console, '\nUploading trimmed unpaired reverse reads.')
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'unpaired_rev_' + rev_file_name, 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', str(input_params['output_ws']),
                                   '--outobj', input_params['output_read_library'] + '_unpaired_rev', '--readcount', read_count_reverse_only ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            stdout, stderr = cmdProcess.communicate()
            print("cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr)
            #report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
            #reportObj['objects_created'].append({'ref':str(input_params['input_ws'])+'/'+input_params['output_read_library']+'_unpaired_rev', 
            #            'description':'Trimmed Unpaired Reverse Reads'})
            retVal['output_unpaired_rev_ref'] = str(input_params['output_ws'])+'/'+str(input_params['output_reads_name']+'_unpaired_rev')


        # SingleEndLibrary
        #
        else:
            self.log(console, "Downloading Single End reads file...")
            fr_file_name = ''
            if 'handle' in readLibrary['data']:
                forward_reads = readLibrary['data']['handle']
            elif 'lib' in readLibrary['data']:
                forward_reads = readLibrary['data']['lib']['file']


            fr_file_name = str(forward_reads['id'])
            if 'file_name' in forward_reads:
                    fr_file_name = forward_reads['file_name']

            reads_file = open(fr_file_name, 'w', 0)
            r = requests.get(forward_reads['url']+'/node/'+forward_reads['id']+'?download', stream=True, headers=headers)
            for chunk in r.iter_content(1024):
                reads_file.write(chunk)
            self.log(console, "done.\n")

            cmdstring = " ".join( (self.TRIMMOMATIC, trimmomatic_options,
                            fr_file_name,
                            'trimmed_' + fr_file_name,
                            trimmomatic_params) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

            #report += "cmdstring: " + cmdstring

            outputlines = []

            while True:
                line = cmdProcess.stdout.readline()
                outputlines.append(line)
                if not line: break
                self.log(console, line.replace('\n', ''))

            report += "\n".join(outputlines)

            #get read count
            match = re.search(r'Surviving: (\d+)', report)
            readcount = match.group(1)

            #upload reads
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'trimmed_' + fr_file_name, 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', str(input_params['output_ws']),
                                   '--outobj', input_params['output_read_library'], '--readcount', readcount ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            stdout, stderr = cmdProcess.communicate()
            #report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
            #reportObj['objects_created'].append({'ref':str(input_params['input_ws'])+'/'+input_params['output_read_library'], 
            #            'description':'Trimmed Reads'})
            retVal['output_filtered_ref'] = str(input_params['output_ws'])+'/'+str(input_params['output_reads_name'])


        # return created objects
        #
        output = { 'report': report,
                   'output_filtered_ref': retVal['output_filtered_ref'],
                   'output_unpaired_fwd_ref': retVal['output_unpaired_fwd_ref'],
                   'output_unpaired_rev_ref': retVal['output_unpaired_rev_ref']
                 }
        #END execTrimmomaticSingleLibrary

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method execTrimmomaticSingleLibrary return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "", 'version': self.VERSION, 
                     'git_url': self.GIT_URL, 'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
