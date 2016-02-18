/*
A KBase module: kb_trimmomatic
This sample module contains one small method - filter_contigs.
*/

module kb_trimmomatic {
    
    /*
        A string representing a workspace name.
    */
    typedef string workspace_name;

    
    /* using KBaseFile.PairedEndLibrary */

    typedef structure {
        workspace_name input_ws;
        workspace_name output_ws;
        string read_type;
        string input_read_library;
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
        string output_read_library;
    } TrimmomaticInput;

    typedef structure {
        string report_name;
        string report_ref;
    } TrimmomaticOutput;

    funcdef runTrimmomatic(TrimmomaticInput input_params) 
        returns (TrimmomaticOutput output) 
        authentication required;
};