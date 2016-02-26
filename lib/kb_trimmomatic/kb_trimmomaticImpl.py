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

    def runTrimmomatic(self, ctx, input_params):
        # ctx is the context object
        # return variables are: output
        #BEGIN runTrimmomatic

        console = []
        self.log(console, 'Running Trimmomatic with paramseters: ')

        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token)
        headers = {'Authorization': 'OAuth '+token}
        env = os.environ.copy()
        env['KB_AUTH_TOKEN'] = token

        #load provenance
        provenance = [{}]
        if 'provenance' in ctx:
            provenance = ctx['provenance']
        # add additional info to provenance here, in this case the input data object reference
        provenance[0]['input_ws_objects']=[input_params['input_ws']+'/'+input_params['input_read_library']]

        if ('output_ws' not in input_params or input_params['output_ws'] is None):
            input_params['output_ws'] = input_params['input_ws']

        trimmomatic_params  = self.parse_trimmomatic_steps(input_params)
        trimmomatic_options = input_params['read_type'] + ' -' + input_params['quality_encoding']

        self.log(console, pformat(trimmomatic_params))
        self.log(console, pformat(trimmomatic_options))

        report = ''
        reportObj = {'objects_created':[], 
                     'text_message':''}


        try:
            readLibrary = wsClient.get_objects([{'name': input_params['input_read_library'], 
                                                            'workspace' : input_params['input_ws']}])[0]
            info = readLibrary['info']

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

            self.log(console, "\nDownloading Paired End reads file...")
            forward_reads_file = open(forward_reads['file_name'], 'w', 0)
            
            r = requests.get(forward_reads['url']+'/node/'+forward_reads['id']+'?download', stream=True, headers=headers)
            for chunk in r.iter_content(1024):
                forward_reads_file.write(chunk)
            forward_reads_file.close()
            self.log(console, 'done\n')

            if 'interleaved' in readLibrary['data'] and readLibrary['data']['interleaved']:
                if re.search('gz', forward_reads['file_name'], re.I):
                    bcmdstring = 'gunzip -c ' + forward_reads['file_name']
                    self.log(console, "Reads are gzip'd and interleaved, uncompressing and deinterleaving.")
                else:    
                    bcmdstring = 'cat ' + forward_reads['file_name'] 
                    self.log(console, "Reads are interleaved, deinterleaving.")

                
                cmdstring = bcmdstring + '| (paste - - - - - - - -  | tee >(cut -f 1-4 | tr "\t" "\n" > forward.fastq) | cut -f 5-8 | tr "\t" "\n" > reverse.fastq )'
                cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash')
                stdout, stderr = cmdProcess.communicate()

                # Check return status
                report = "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
                self.log(console, 'done\n')
                forward_reads['file_name']='forward.fastq'
                reverse_reads['file_name']='reverse.fastq'
            else:
                self.log(console, 'Downloading reverse reads.')
                reverse_reads_file = open(reverse_reads['file_name'], 'w', 0)

                r = requests.get(reverse_reads['url']+'/node/'+reverse_reads['id']+'?download', stream=True, headers=headers)
                for chunk in r.iter_content(1024):
                    reverse_reads_file.write(chunk)
                reverse_reads_file.close()
                self.log(console, 'done\n')

            cmdstring = " ".join( (self.TRIMMOMATIC, trimmomatic_options, 
                            forward_reads['file_name'], 
                            reverse_reads['file_name'],
                            'forward_paired_'   +forward_reads['file_name'],
                            'forward_unpaired_' +forward_reads['file_name'],
                            'reverse_paired_'   +reverse_reads['file_name'],
                            'reverse_unpaired_' +reverse_reads['file_name'],
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
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'forward_paired_' + forward_reads['file_name'], 
                                   '--inputfile2', 'reverse_paired_' + reverse_reads['file_name'],
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', input_params['output_ws'],
                                   '--outobj', input_params['output_read_library'] + '_paired', '--readcount', read_count_paired ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            stdout, stderr = cmdProcess.communicate()
            print("cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr)
            #report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
            reportObj['objects_created'].append({'ref':input_params['input_ws']+'/'+input_params['output_read_library']+'_paired', 
                        'description':'Trimmed Paired-End Reads'})

            #upload reads forward unpaired
            self.log(console, '\nUploading trimmed unpaired forward reads.')
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'forward_unpaired_' + forward_reads['file_name'], 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', input_params['output_ws'],
                                   '--outobj', input_params['output_read_library'] + '_forward_unpaired', '--readcount', read_count_forward_only ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            stdout, stderr = cmdProcess.communicate()
            print("cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr)
            #report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
            reportObj['objects_created'].append({'ref':input_params['input_ws']+'/'+input_params['output_read_library']+'_forward_unpaired', 
                        'description':'Trimmed Unpaired Forward Reads'})

            #upload reads reverse unpaired
            self.log(console, '\nUploading trimmed unpaired reverse reads.')
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'reverse_unpaired_' + reverse_reads['file_name'], 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', input_params['output_ws'],
                                   '--outobj', input_params['output_read_library'] + '_reverse_unpaired', '--readcount', read_count_reverse_only ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            stdout, stderr = cmdProcess.communicate()
            print("cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr)
            #report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
            reportObj['objects_created'].append({'ref':input_params['input_ws']+'/'+input_params['output_read_library']+'_reverse_unpaired', 
                        'description':'Trimmed Unpaired Reverse Reads'})

        else:
            self.log(console, "Downloading Single End reads file...")
            if 'handle' in readLibrary['data']:
                reads_file = open(readLibrary['data']['handle']['file_name'], 'w', 0)
                r = requests.get(readLibrary['data']['handle']['url']+'/node/'+readLibrary['data']['handle']['file_name']+'?download', stream=True, headers=headers)
                for chunk in r.iter_content(1024):
                    reads_file.write(chunk)
            self.log(console, "done.\n")

            cmdstring = " ".join( (self.TRIMMOMATIC, trimmomatic_options,
                            readLibrary['data']['handle']['file_name'],
                            'trimmed_' + readLibrary['data']['handle']['file_name'],
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
            cmdstring = " ".join( ('ws-tools fastX2reads --inputfile', 'trimmed_' + readLibrary['data']['handle']['file_name'], 
                                   '--wsurl', self.workspaceURL, '--shockurl', self.shockURL, '--outws', input_params['output_ws'],
                                   '--outobj', input_params['output_read_library'], '--readcount', readcount ) )

            cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            stdout, stderr = cmdProcess.communicate()
            report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr
            reportObj['objects_created'].append({'ref':input_params['input_ws']+'/'+input_params['output_read_library'], 
                        'description':'Trimmed Reads'})

        # save report object
        reportObj['text_message'] = report
        reportName = 'trimmomatic_report_' + str(hex(uuid.getnode()))
        report_obj_info = wsClient.save_objects({
                'id':info[6],
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
