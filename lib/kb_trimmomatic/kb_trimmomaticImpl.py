#BEGIN_HEADER
import sys
import traceback
from biokbase.workspace.client import Workspace as workspaceService
import requests
import subprocess
import os
import re
#END_HEADER


class kb_trimmomatic:
    '''
    Module Name:
    kb_trimmomatic

    Module Description:
    A KBase module: kb_trimmomatic
This sample module contains one small method - filter_contigs.
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    #BEGIN_CLASS_HEADER
    workspaceURL = None
    TRIMMOMATIC = 'java -jar /kb/module/Trimmomatic-0.33/trimmomatic-0.33.jar'
    ADAPTER_DIR = '/kb/module/Trimmomatic-0.33/adapters/'


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
                                    ":".join( (input_params['adapterFa'],
                                       input_params['seed_mismatches'], 
                                       input_params['palindrome_clip_threshold'],
                                       input_params['simple_clip_threshold']) ) + " " )
        elif ( ('adapterFa' in input_params and input_params['adapterFa'] is not None) or
               ('seed_mismatches' in input_params and input_params['seed_mismatches'] is not None) or
               ('palindrome_clip_threshold' in input_params and input_params['palindrome_clip_threshold'] is not None) or
               ('simple_clip_threshold' in input_params and input_params['simple_clip_threshold'] is not None) ):
            raise ValueError('Adapter Cliping requires Adapter, Seed Mismatches, Palindrome Clip Threshold and Simple Clip Threshold')


        # set Crop
        if 'crop_length' in input_params and input_params['crop_length'] is not None:
            parameter_string += 'CROP:' + input_params['crop_length'] + ' '

        # set Headcrop
        if 'head_crop_length' in input_params and input_params['head_crop_length'] is not None:
            parameter_string += 'HEADCROP:' + input_params['head_crop_length'] + ' '


        # set Leading
        if 'leading_min_quality' in input_params and input_params['leading_min_quality'] is not None:
            parameter_string += 'LEADING:' + input_params['leading_min_quality'] + ' '


        # set Trailing
        if 'trailing_min_quality' in input_params and input_params['trailing_min_quality'] is not None:
            parameter_string += 'TRAILING:' + input_params['trailing_min_quality'] + ' '


        # set sliding window
        if ('sliding_window_size' in input_params and input_params['sliding_window_size'] is not None and 
            'sliding_window_min_quality' in input_params and input_params['sliding_window_min_quality'] is not None):
            parameter_string += 'SLIDINGWINDOW:' + input_params['sliding_window_size'] + ":" + input_params['sliding_window_min_quality'] + ' '
        elif ( ('sliding_window_size' in input_params and input_params['sliding_window_size'] is not None) or 
               ('sliding_window_min_quality' in input_params and input_params['sliding_window_min_quality'] is not None) ):
            raise ValueError('Sliding Window filtering requires both Window Size and Window Minimum Quality to be set')
            

        # set min length
        if 'min_length' in input_params and input_params['min_length'] is not None:
            parameter_string += 'MINLEN:' + input_params['min_length'] + ' '

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
        #END_CONSTRUCTOR
        pass

    def filter_contigs(self, ctx, params):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN filter_contigs
        
        print('Starting filter contigs method.')
        
        if 'workspace' not in params:
            raise ValueError('Parameter workspace is not set in input arguments')
        workspace_name = params['workspace']
        if 'contigset_id' not in params:
            raise ValueError('Parameter contigset_id is not set in input arguments')
        contigset_id = params['contigset_id']
        if 'min_length' not in params:
            raise ValueError('Parameter min_length is not set in input arguments')
        min_length_orig = params['min_length']
        min_length = None
        try:
            min_length = int(min_length_orig)
        except ValueError:
            raise ValueError('Cannot parse integer from min_length parameter (' + str(min_length_orig) + ')')
        if min_length < 0:
            raise ValueError('min_length parameter shouldn\'t be negative (' + str(min_length) + ')')
        
        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token) 
        try: 
            contigSet = wsClient.get_objects([{'ref': workspace_name+'/'+contigset_id}])[0]['data']
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error loading original ContigSet object from workspace:\n' + orig_error)
        provenance = ctx['provenance']
        
        print('Got ContigSet data.')
        
        # save the contigs to a new list
        good_contigs = []
        n_total = 0;
        n_remaining = 0;
        for contig in contigSet['contigs']:
            n_total += 1
            if len(contig['sequence']) >= min_length:
                good_contigs.append(contig)
                n_remaining += 1

        # replace the contigs in the contigSet object in local memory
        contigSet['contigs'] = good_contigs
        
        print('Filtered ContigSet to '+str(n_remaining)+' contigs out of '+str(n_total))
        
        # save the new object to the workspace
        obj_info_list = None
        try:
	        obj_info_list = wsClient.save_objects({
	                            'workspace':workspace_name,
	                            'objects': [
	                                {
	                                    'type':'KBaseGenomes.ContigSet',
	                                    'data':contigSet,
	                                    'name':contigset_id,
	                                    'provenance':provenance
	                                }
	                            ]
	                        })
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error saving filtered ContigSet object to workspace:\n' + orig_error)
        
        info = obj_info_list[0]

        print('saved:'+str(info))

        returnVal = {
                'new_contigset_ref': str(info[6]) + '/'+str(info[0])+'/'+str(info[4]),
                'n_initial_contigs':n_total,
                'n_contigs_removed':n_total-n_remaining,
                'n_contigs_remaining':n_remaining
            }
        
        print('returning:'+str(returnVal))
                
        #END filter_contigs

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method filter_contigs return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def runTrimmomatic(self, ctx, input_params):
        # ctx is the context object
        # return variables are: report
        #BEGIN runTrimmomatic
        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token)
        headers = {'Authorization': 'OAuth '+token}

        if ('output_ws' not in input_params or input_params['output_ws'] is None):
            input_params['output_ws'] = input_params['input_ws']

        trimmomatic_params  = self.parse_trimmomatic_steps(input_params)
        trimmomatic_options = input_params['read_type'] + ' -' + input_params['quality_encoding']

        report = ''


        try:
            readLibrary = wsClient.get_objects([{'name': input_params['input_read_library'], 
                                                            'workspace' : input_params['input_ws']}])[0]
        except Exception as e:
            raise ValueError('Unable to get read library object from workspace: (' + input_params['input_ws']+ '/' + input_params['input_read_library'] +')' + str(e))


        if input_params['read_type'] == 'PE':
            if 'lib1' in readLibrary['data']:
                forward_reads = readLibrary['data']['lib1']['file']
            elif 'handle_1' in readLibrary['data']:
                forward_reads = readLibrary['data']['handle_1']
            if 'lib2' in readLibrary['data']:
                reverse_reads = readLibrary['data']['lib2']['file']
            elif 'handle_2' in readLibrary['data']:
                reverse_reads = readLibrary['data']['handle_2']
            else:
                reverse_reads={}

            forward_reads_file = open(forward_reads['file_name'], 'w', 0)
            r = requests.get(forward_reads['url']+'/node/'+forward_reads['id']+'?download', stream=True, headers=headers)
            for chunk in r.iter_content(1024):
                forward_reads_file.write(chunk)

            if 'interleaved' in readLibrary['data'] and readLibrary['data']['interleaved']:
                if re.search('gz', forward_reads['file_name'], re.I):
                    bcmdstring = 'gunzip -c ' + forward_reads['file_name']
                else:    
                    bcmdstring = 'cat ' + forward_reads['file_name'] 

                
                cmdstring = bcmdstring + '| (paste - - - - - - - -  | tee >(cut -f 1-4 | tr "\t" "\n" > forward.fastq) | cut -f 5-8 | tr "\t" "\n" > reverse.fastq )'
                cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash')
                stdout, stderr = cmdProcess.communicate()

                # Check return status
                report = "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
                
                forward_reads['file_name']='forward.fastq'
                reverse_reads['file_name']='reverse.fastq'
            else:
                reverse_reads_file = open(reverse_reads['file_name'], 'w', 0)
                r = requests.get(reverse_reads['url']+'/node/'+reverse_reads['id']+'?download', stream=True, headers=headers)
                for chunk in r.iter_content(1024):
                    reverse_reads_file.write(chunk)

            cmdstring = " ".join( (self.TRIMMOMATIC, trimmomatic_options, 
                            forward_reads['file_name'], 
                            reverse_reads['file_name'],
                            'forward_paired_'   +forward_reads['file_name'],
                            'forward_unpaired_' +forward_reads['file_name'],
                            'reverse_paired_'   +reverse_reads['file_name'],
                            'reverse_unpaired_' +reverse_reads['file_name'],
                            trimmomatic_params) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            stdout, stderr = cmdProcess.communicate()
            report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr " + stderr


            #get read counts
            match = re.search(r'Both Surviving: (\d+).*?Forward Only Surviving: (\d+).*?Reverse Only Surviving: (\d+)', report)
            read_count_paired = match.group(1)
            read_count_forward_only = match.group(2)
            read_count_reverse_only = match.group(3)

            #upload reads forward paired
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'forward_paired_' + forward_reads['file_name'], 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', input_params['output_ws'],
                                   '--outobj', input_params['output_read_library'] + '_forward_paired', '--readcount', read_count_paired, '--token', token ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = cmdProcess.communicate()
            report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr

            #upload reads reverse paired
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'reverse_paired_' + reverse_reads['file_name'], 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', input_params['output_ws'],
                                   '--outobj', input_params['output_read_library'] + '_reverse_paired', '--readcount', read_count_paired, '--token', token ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = cmdProcess.communicate()
            report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr

            #upload reads forward unpaired
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'forward_unpaired_' + forward_reads['file_name'], 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', input_params['output_ws'],
                                   '--outobj', input_params['output_read_library'] + '_forward_unpaired', '--readcount', read_count_forward_only, '--token', token ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = cmdProcess.communicate()
            report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr

            #upload reads reverse unpaired
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'reverse_unpaired_' + reverse_reads['file_name'], 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', input_params['output_ws'],
                                   '--outobj', input_params['output_read_library'] + '_reverse_unpaired', '--readcount', read_count_reverse_only, '--token', token ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = cmdProcess.communicate()
            report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr

        else:
            if 'handle' in readLibrary['data']:
                reads_file = open(readLibrary['data']['handle']['file_name'], 'w', 0)
                r = requests.get(readLibrary['data']['handle']['url']+'/node/'+readLibrary['data']['handle']['id']+'?download', stream=True, headers=headers)
                for chunk in r.iter_content(1024):
                    reads_file.write(chunk)

            cmdstring = " ".join( (self.TRIMMOMATIC, trimmomatic_options,
                            readLibrary['data']['handle']['file_name'],
                            'trimmed_' + readLibrary['data']['handle']['file_name'],
                            trimmomatic_params) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = cmdProcess.communicate()
            report = "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr

            #get read count
            match = re.search(r'Surviving: (\d+)', report)
            readcount = match.group(1)

            #upload reads
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'trimmed_' + readLibrary['data']['handle']['file_name'], 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', input_params['output_ws'],
                                   '--outobj', input_params['output_read_library'], '--readcount', readcount, '--token', token ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = cmdProcess.communicate()
            report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
        #END runTrimmomatic

        # At some point might do deeper type checking...
        if not isinstance(report, basestring):
            raise ValueError('Method runTrimmomatic return value ' +
                             'report is not type basestring as required.')
        # return the results
        return [report]
