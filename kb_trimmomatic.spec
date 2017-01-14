/*
A KBase module: kb_trimmomatic
This module contains two methods

runTrimmomatic() to backend a KBase App, potentially operating on ReadSets
execTrimmomatic() the local method that handles overloading Trimmomatic to run on a set or a single library
execTrimmomaticSingleLibrary() runs Trimmomatic on a single library
*/

module kb_trimmomatic {
    
    /*
    ** Common types
    */
    typedef string workspace_name;
    typedef string data_obj_ref;
    typedef string data_obj_name;


    /* parameter groups
    */
    typedef structure {
    } SlidingWindow_Options;

    typedef structure {
        string adapterFa;
        int seed_mismatches;
        int palindrome_clip_threshold;
        int simple_clip_threshold;
    } AdapterClip_Options;

    
    /* runTrimmomatic()
    **
    ** to backend a KBase App, potentially operating on ReadSets
    */
    typedef structure {
        workspace_name input_ws;
        /*string input_read_library;*/
        /*data_obj_name input_reads_name;*/  /* may be either ReadSet, PairedEndLibrary, or SingleEndLibrary */
        data_obj_ref input_reads_ref;  /* may be either ReadSet, PairedEndLibrary, or SingleEndLibrary */
        workspace_name output_ws;
        /*string output_read_library;*/
	data_obj_name output_reads_name;

        string                read_type;
        string                quality_encoding;
	AdapterClip_Options   adapter_clip;
        int sliding_window_size;
        int sliding_window_min_quality;
        int leading_min_quality;
        int trailing_min_quality;
        int crop_length;
        int head_crop_length;
        int min_length;
    } runTrimmomaticInput;

    typedef structure {
        string report_name;
        string report_ref;
    } runTrimmomaticOutput;

    funcdef runTrimmomatic(runTrimmomaticInput input_params) 
        returns (runTrimmomaticOutput output) 
        authentication required;


    /* execTrimmomatic()
    **
    ** the local method that runs Trimmomatic on each read library
    */
    typedef structure {
        data_obj_ref input_reads_ref; /* may be either PairedEndLibrary, or SingleEndLibrary */
        workspace_name output_ws;
        data_obj_name output_reads_name;

        string read_type;
        string adapterFa;
        int seed_mismatches;
        int palindrome_clip_threshold;
        int simple_clip_threshold;
        string quality_encoding;
        int sliding_window_size;
        int sliding_window_min_quality;
        int leading_min_quality;
        int trailing_min_quality;
        int crop_length;
        int head_crop_length;
        int min_length;
    } execTrimmomaticInput;

    typedef structure {
        data_obj_ref output_filtered_ref;
	data_obj_ref output_unpaired_fwd_ref;
	data_obj_ref output_unpaired_rev_ref;
	string       report;
    } execTrimmomaticOutput;

    funcdef execTrimmomatic(execTrimmomaticInput input_params) 
        returns (execTrimmomaticOutput output) 
        authentication required;

    funcdef execTrimmomaticSingleLibrary(execTrimmomaticInput input_params) 
        returns (execTrimmomaticOutput output) 
        authentication required;
};