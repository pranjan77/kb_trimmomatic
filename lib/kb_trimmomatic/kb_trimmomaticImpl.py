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
from ReadsUtils.ReadsUtilsClient import ReadsUtils
from SetAPI.SetAPIClient import SetAPI
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
    GIT_URL = "https://github.com/kbaseapps/kb_trimmomatic"
    GIT_COMMIT_HASH = "a0822ba2b3b598a4f610cea20204a242dd72ff60"
    
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
        self.serviceWizardURL = config['service-wizard-url']

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
        self.log(console, 'Running runTrimmomatic with parameters: ')
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
                                  'seed_mismatches': input_params['seed_mismatches'],
                                  'palindrome_clip_threshold': input_params['palindrome_clip_threshold'],
                                  'simple_clip_threshold': input_params['simple_clip_threshold'],
                                  'quality_encoding': input_params['quality_encoding'],
                                  'sliding_window_size': input_params['sliding_window_size'],
                                  'sliding_window_min_quality': input_params['sliding_window_min_quality'],
                                  'leading_min_quality': input_params['leading_min_quality'],
                                  'trailing_min_quality': input_params['trailing_min_quality'],
                                  'crop_length': input_params['crop_length'],
                                  'head_crop_length': input_params['head_crop_length'],
                                  'min_length': input_params['min_length']
                                  }

        trimmomatic_retVal = self.execTrimmomatic (ctx, execTrimmomaticParams)[0]


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
        reportName = 'trimmomatic_report_' + str(uuid.uuid4())
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
        self.log(console, 'Running execTrimmomatic with parameters: ')
        self.log(console, "\n"+pformat(input_params))
        report = ''
        trimmomatic_retVal = dict()
        trimmomatic_retVal['output_filtered_ref'] = None
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

            input_reads_obj_info = wsClient.get_object_info_new ({'objects':[{'ref':input_params['input_reads_ref']}]})[0]
            input_reads_obj_type = input_reads_obj_info[TYPE_I]
            #input_reads_obj_version = input_reads_obj_info[VERSION_I]  # this is object version, not type version

        except Exception as e:
            raise ValueError('Unable to get read library object from workspace: (' + str(input_params['input_reads_ref']) +')' + str(e))

        #self.log (console, "B4 TYPE: '"+str(input_reads_obj_type)+"' VERSION: '"+str(input_reads_obj_version)+"'")
        input_reads_obj_type = re.sub ('-[0-9]+\.[0-9]+$', "", input_reads_obj_type)  # remove trailing version
        #self.log (console, "AF TYPE: '"+str(input_reads_obj_type)+"' VERSION: '"+str(input_reads_obj_version)+"'")

        acceptable_types = ["KBaseSets.ReadsSet", "KBaseFile.PairedEndLibrary", "KBaseAssembly.PairedEndLibrary", "KBaseAssembly.SingleEndLibrary", "KBaseFile.SingleEndLibrary"]
        if input_reads_obj_type not in acceptable_types:
            raise ValueError ("Input reads of type: '"+input_reads_obj_type+"'.  Must be one of "+", ".join(acceptable_types))


        # get set
        #
        readsSet_ref_list = []
        readsSet_names_list = []
        if input_reads_obj_type != "KBaseSets.ReadsSet":
            readsSet_ref_list = [input_params['input_reads_ref']]
        else:
            try:
                #self.log (console, "INPUT_READS_REF: '"+input_params['input_reads_ref']+"'")  # DEBUG
                #setAPI_Client = SetAPI (url=self.callbackURL, token=ctx['token'])  # for SDK local.  doesn't work for SetAPI
                setAPI_Client = SetAPI (url=self.serviceWizardURL, token=ctx['token'])  # for dynamic service
                input_readsSet_obj = setAPI_Client.get_reads_set_v1 ({'ref':input_params['input_reads_ref'],'include_item_info':1})

            except Exception as e:
                raise ValueError('SetAPI FAILURE: Unable to get read library set object from workspace: (' + str(input_params['input_reads_ref'])+")\n" + str(e))
            for readsLibrary_obj in input_readsSet_obj['data']['items']:
                readsSet_ref_list.append(readsLibrary_obj['ref'])
                NAME_I = 1
                readsSet_names_list.append(readsLibrary_obj['info'][NAME_I])


        # Iterate through readLibrary memebers of set
        #
        report = ''
        trimmed_readsSet_refs      = []
        unpaired_fwd_readsSet_refs = []
        unpaired_rev_readsSet_refs = []

        for reads_item_i,input_reads_library_ref in enumerate(readsSet_ref_list):
            execTrimmomaticParams = { 'input_reads_ref': input_reads_library_ref,
                                      'output_ws': input_params['output_ws'],
                                      'read_type': input_params['read_type'],
                                      'adapterFa': input_params['adapterFa'],
                                      'seed_mismatches': input_params['seed_mismatches'],
                                      'palindrome_clip_threshold': input_params['palindrome_clip_threshold'],
                                      'simple_clip_threshold': input_params['simple_clip_threshold'],
                                      'quality_encoding': input_params['quality_encoding'],
                                      'sliding_window_size': input_params['sliding_window_size'],
                                      'sliding_window_min_quality': input_params['sliding_window_min_quality'],
                                      'leading_min_quality': input_params['leading_min_quality'],
                                      'trailing_min_quality': input_params['trailing_min_quality'],
                                      'crop_length': input_params['crop_length'],
                                      'head_crop_length': input_params['head_crop_length'],
                                      'min_length': input_params['min_length']
                                    }
            
            if input_reads_obj_type != "KBaseSets.ReadsSet":
                execTrimmomaticParams['output_reads_name'] = input_params['output_reads_name']
            else:
                execTrimmomaticParams['output_reads_name'] = readsSet_names_list[reads_item_i]

            report += "RUNNING TRIMMOMATIC ON LIBRARY: "+str(input_reads_library_ref)+"\n"
            report += "----------------------------------------------------------------------------\n\n"
            trimmomatic_retVal = self.execTrimmomaticSingleLibrary (ctx, execTrimmomaticParams)[0]
            report += trimmomatic_retVal['report']+"\n\n"
            trimmed_readsSet_refs.append (trimmomatic_retVal['output_filtered_ref'])
            unpaired_fwd_readsSet_refs.append (trimmomatic_retVal['output_unpaired_fwd_ref'])
            unpaired_rev_readsSet_refs.append (trimmomatic_retVal['output_unpaired_rev_ref'])

        
        # Just one Library
        if input_reads_obj_type != "KBaseSets.ReadsSet":

            # create return output object
            output = { 'report': report,
                       'output_filtered_ref': trimmomatic_retVal['output_filtered_ref'],
                       'output_unpaired_fwd_ref': trimmomatic_retVal['output_unpaired_fwd_ref'],
                       'output_unpaired_rev_ref': trimmomatic_retVal['output_unpaired_rev_ref']
                     }
        # ReadsSet
        else:
            # save trimmed readsSet
            items = []
            for i,lib_ref in enumerate(trimmed_readsSet_refs):
                if lib_ref == None:
                    items.append(None)
                else:
                    try:
                        label = input_readsSet_obj['data']['items'][i]['label']
                    except:
                        NAME_I = 1
                        label = wsClient.get_object_info_new ({'objects':[{'ref':lib_ref}]})[0][NAME_I]
                    label = label + "_Trimm_paired"

                    items.append({'ref': lib_ref,
                                  'label': label
                                  #'data_attachment': ,
                                  #'info':
                                      })
            output_readsSet_obj = { 'description': input_readsSet_obj['data']['description']+" Trimmomatic paired reads",
                                    'items': items
                                    }
            trimmed_readsSet_ref = setAPI_Client.save_reads_set_v1 ({'workspace_name': input_params['output_ws'],
                                                                     'output_object_name': str(input_params['output_reads_name'])+'_trimm_paired',
                                                                     'data': output_readsSet_obj
                                                                     })['set_ref']
                              
            # save unpaired forward readsSet
            if len(unpaired_fwd_readsSet_refs) > 0:
                items = []
                if lib_ref == None:
                    items.append(None)
                else:
                    for i,lib_ref in enumerate(unpaired_fwd_readsSet_refs):
                        try:
                            label = input_readsSet_obj['data']['items'][i]['label']
                        except:
                            NAME_I = 1
                            label = wsClient.get_object_info_new ({'objects':[{'ref':lib_ref}]})[0][NAME_I]
                        label = label + "_Trimm_unpaired_fwd"

                        items.append({'ref': lib_ref,
                                      'label': label
                                      #'data_attachment': ,
                                      #'info':
                                          })
                output_readsSet_obj = { 'description': input_readsSet_obj['data']['description']+" Trimmomatic unpaired fwd reads",
                                        'items': items
                                        }
                unpaired_fwd_readsSet_ref = setAPI_Client.save_reads_set_v1 ({'workspace_name': input_params['output_ws'],
                                                                              'output_object_name': str(input_params['output_reads_name'])+'_trimm_unpaired_fwd',
                                                                              'data': output_readsSet_obj
                                                                              })['set_ref']
                              
            # save unpaired reverse readsSet
            if len(unpaired_rev_readsSet_refs) > 0:
                items = []
                if lib_ref == None:
                    items.append(None)
                else:
                    for i,lib_ref in enumerate(unpaired_rev_readsSet_refs):
                        try:
                            label = input_readsSet_obj['data']['items'][i]['label']
                        except:
                            NAME_I = 1
                            label = wsClient.get_object_info_new ({'objects':[{'ref':lib_ref}]})[0][NAME_I]
                        label = label + "_Trimm_unpaired_rev"

                        items.append({'ref': lib_ref,
                                      'label': label
                                      #'data_attachment': ,
                                      #'info':
                                          })
                output_readsSet_obj = { 'description': input_readsSet_obj['data']['description']+" Trimmomatic unpaired rev reads",
                                        'items': items
                                        }
                unpaired_rev_readsSet_ref = setAPI_Client.save_reads_set_v1 ({'workspace_name': input_params['output_ws'],
                                                                              'output_object_name': str(input_params['output_reads_name'])+'_trimm_unpaired_rev',
                                                                              'data': output_readsSet_obj
                                                                              })['set_ref']


            # create return output object
            output = { 'report': report,
                       'output_filtered_ref': trimmed_readsSet_ref,
                       'output_unpaired_fwd_ref': unpaired_fwd_readsSet_ref,
                       'output_unpaired_rev_ref': unpaired_rev_readsSet_ref
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
        retVal['output_filtered_ref'] = None
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
        for arg in defaults.keys():
            if arg not in input_params or input_params[arg] == None or input_params[arg] == '':
                input_params[arg] = defaults[arg]
            
        # conditional arg behavior
        arg = 'adapterFa'
        if arg not in input_params or input_params[arg] == None or input_params[arg] == '':
            input_params['adapterFa'] = None
            input_params['seed_mismatches'] = None
            input_params['palindrome_clip_threshold'] = None
            input_params['simple_clip_threshold'] = None
            

        #load provenance
        provenance = [{}]
        if 'provenance' in ctx:
            provenance = ctx['provenance']
        # add additional info to provenance here, in this case the input data object reference
        provenance[0]['input_ws_objects']=[str(input_params['input_reads_ref'])]

        # Determine whether read library is of correct type
        #
        try:
            # object_info tuple
            [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)

            input_reads_obj_info = wsClient.get_object_info_new ({'objects':[{'ref':input_params['input_reads_ref']}]})[0]
            input_reads_obj_type = input_reads_obj_info[TYPE_I]
            #input_reads_obj_version = input_reads_obj_info[VERSION_I]  # this is object version, not type version

        except Exception as e:
            raise ValueError('Unable to get read library object from workspace: (' + str(input_params['input_reads_ref']) +')' + str(e))

        #self.log (console, "B4 TYPE: '"+str(input_reads_obj_type)+"' VERSION: '"+str(input_reads_obj_version)+"'")
        input_reads_obj_type = re.sub ('-[0-9]+\.[0-9]+$', "", input_reads_obj_type)  # remove trailing version
        #self.log (console, "AF TYPE: '"+str(input_reads_obj_type)+"' VERSION: '"+str(input_reads_obj_version)+"'")

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


        # Instatiate ReadsUtils
        #
        try:
            readsUtils_Client = ReadsUtils (url=self.callbackURL, token=ctx['token'])  # SDK local
            
            readLibrary = readsUtils_Client.download_reads ({'read_libraries': [input_params['input_reads_ref']]
#                                                             'interleaved': 'false'
                                                             })
        except Exception as e:
            raise ValueError('Unable to get read library object from workspace: (' + str(input_params['input_reads_ref']) +")\n" + str(e))


        if input_params['read_type'] == 'PE':

            # Download reads Libs to FASTQ files
            input_fwd_file_path = readLibrary['files'][input_params['input_reads_ref']]['files']['fwd']
            input_rev_file_path = readLibrary['files'][input_params['input_reads_ref']]['files']['rev']


            # Run Trimmomatic
            #
            self.log(console, 'Starting Trimmomatic')
            input_fwd_file_path = re.sub ("\.fastq$", "", input_fwd_file_path)
            input_fwd_file_path = re.sub ("\.FASTQ$", "", input_fwd_file_path)
            input_rev_file_path = re.sub ("\.fastq$", "", input_rev_file_path)
            input_rev_file_path = re.sub ("\.FASTQ$", "", input_rev_file_path)
            output_fwd_paired_file_path   = input_fwd_file_path+"_trimm_fwd_paired.fastq"
            output_fwd_unpaired_file_path = input_fwd_file_path+"_trimm_fwd_unpaired.fastq"
            output_rev_paired_file_path   = input_rev_file_path+"_trimm_rev_paired.fastq"
            output_rev_unpaired_file_path = input_rev_file_path+"_trimm_rev_unpaired.fastq"
            input_fwd_file_path           = input_fwd_file_path+".fastq"
            input_rev_file_path           = input_rev_file_path+".fastq"
            
            cmdstring = " ".join( (self.TRIMMOMATIC, trimmomatic_options, 
                            input_fwd_file_path, 
                            input_rev_file_path,
                            output_fwd_paired_file_path,
                            output_fwd_unpaired_file_path,
                            output_rev_paired_file_path,
                            output_rev_unpaired_file_path,
                            trimmomatic_params) )

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

            # upload paired reads
            output_obj_name = input_params['output_reads_name']+'_trimm_paired'
            self.log(console, 'Uploading trimmed paired reads: '+output_obj_name)
            retVal['output_filtered_ref'] = readsUtils_Client.upload_reads ({ 'wsname': str(input_params['output_ws']),
                                                                              'name': output_obj_name,
                                                                              'fwd_file': output_fwd_paired_file_path,
                                                                              'rev_file': output_rev_paired_file_path
                                                                              })


            # upload reads forward unpaired
            output_obj_name = input_params['output_reads_name']+'_trimm_unpaired_fwd'
            self.log(console, '\nUploading trimmed unpaired forward reads: '+output_obj_name)
            retVal['output_unpaired_fwd_ref'] = readsUtils_Client.upload_reads ({ 'wsname': str(input_params['output_ws']),
                                                                                  'name': output_obj_name,
                                                                                  'fwd_file': output_fwd_unpaired_file_path
                                                                                  })



            # upload reads reverse unpaired
            output_obj_name = input_params['output_reads_name']+'_trimm_unpaired_rev'
            self.log(console, '\nUploading trimmed unpaired reverse reads: '+output_obj_name)
            retVal['output_unpaired_rev_ref'] = readsUtils_Client.upload_reads ({ 'wsname': str(input_params['output_ws']),
                                                                                  'name': output_obj_name,
                                                                                  'fwd_file': output_rev_unpaired_file_path
                                                                                  })


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
            output_obj_name = input_params['output_reads_name']
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'trimmed_' + fr_file_name, 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', str(input_params['output_ws']),
                                   '--outobj', output_obj_name, '--readcount', readcount ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            stdout, stderr = cmdProcess.communicate()
            #report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
            #reportObj['objects_created'].append({'ref':str(input_params['input_ws'])+'/'+input_params['output_reads_name'], 
            #            'description':'Trimmed Reads'})
            #retVal['output_filtered_ref'] = str(input_params['output_ws'])+'/'+str(input_params['output_reads_name'])
            retVal['output_filtered_ref'] = str(input_params['output_ws']+'/'+output_obj_name)


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
