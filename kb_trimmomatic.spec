/*
A KBase module: kb_trimmomatic
This sample module contains one small method - filter_contigs.
*/

module kb_trimmomatic {
    /*
        A string representing a ContigSet id.
    */
    typedef string contigset_id;

    /*
        A string representing a workspace name.
    */
    typedef string workspace_name;

    typedef structure {
        workspace_name workspace;
        contigset_id contigset_id;
        int min_length;
    } FilterContigsParams;

    /* 
        The workspace ID for a ContigSet data object.
        @id ws KBaseGenomes.ContigSet
    */
    typedef string ws_contigset_id;

    typedef structure {
        ws_contigset_id new_contigset_ref;
        int n_initial_contigs;
        int n_contigs_removed;
        int n_contigs_remaining;
    } FilterContigsResults;
	
    /*
        Filter contigs in a ContigSet by DNA length
    */
    funcdef filter_contigs(FilterContigsParams params) returns (FilterContigsResults) authentication required;



    /* using KBaseFile.PairedEndLibrary */

    typedef structure {
        workspace_name input_ws;
        workspace_name output_ws;
        string read_type;
        string input_read_library;
        string adapterFa;
        int seed_mismatches;
        int palindrom_clip_threshold;
        int simple_clip_threshold;
        string quality_encoding;
        int slinding_window_size;
        int sliding_window_min_quality;
        int leading_min_quality;
        int trailing_min_quality;
        int crop_length;
        int head_crop_length;
        int min_length;
        string output_read_library;
    } TrimmomaticInput;

    funcdef runTrimmomatic(TrimmomaticInput input_params) 
        returns (string report) 
        authentication required;
};