/*
A KBase module: kb_trimmomatic
This module contains two methods

runTrimmomatic() to backend a KBase App, potentially operating on ReadSets
execTrimmomatic() the local method that runs Trimmomatic on each read library
*/

module kb_trimmomatic {
    
    /*
    ** Common types
    */
    typedef string workspace_name;
    typedef string data_obj_ref;
    typedef string data_obj_name;

    
    /* runTrimmomatic()
    **
    ** to backend a KBase App, potentially operating on ReadSets
    */
    typedef structure {
        workspace_name input_ws;
        workspace_name output_ws;
        string read_type;
        /*string input_read_library;*/
        data_obj_name input_reads_name;  /* may be either ReadSet, PairedEndLibrary, or SingleEndLibrary */
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
        /*string output_read_library;*/
        data_obj_name output_reads_name;
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
        data_obj_name output_reads_name;
    } execTrimmomaticInput;

    typedef structure {
        string report_name;
        string report_ref;
    } execTrimmomaticOutput;

    funcdef execTrimmomatic(execTrimmomaticInput input_params) 
        returns (execTrimmomaticOutput output) 
        authentication required;
};