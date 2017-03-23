
package us.kbase.kbtrimmomatic;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: execTrimmomaticInput</p>
 * <pre>
 * execTrimmomatic()
 * **
 * ** the local method that runs Trimmomatic on each read library
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "input_reads_ref",
    "output_ws",
    "output_reads_name",
    "read_type",
    "adapterFa",
    "seed_mismatches",
    "palindrome_clip_threshold",
    "simple_clip_threshold",
    "quality_encoding",
    "sliding_window_size",
    "sliding_window_min_quality",
    "leading_min_quality",
    "trailing_min_quality",
    "crop_length",
    "head_crop_length",
    "min_length"
})
public class ExecTrimmomaticInput {

    @JsonProperty("input_reads_ref")
    private String inputReadsRef;
    @JsonProperty("output_ws")
    private String outputWs;
    @JsonProperty("output_reads_name")
    private String outputReadsName;
    @JsonProperty("read_type")
    private String readType;
    @JsonProperty("adapterFa")
    private String adapterFa;
    @JsonProperty("seed_mismatches")
    private Long seedMismatches;
    @JsonProperty("palindrome_clip_threshold")
    private Long palindromeClipThreshold;
    @JsonProperty("simple_clip_threshold")
    private Long simpleClipThreshold;
    @JsonProperty("quality_encoding")
    private String qualityEncoding;
    @JsonProperty("sliding_window_size")
    private Long slidingWindowSize;
    @JsonProperty("sliding_window_min_quality")
    private Long slidingWindowMinQuality;
    @JsonProperty("leading_min_quality")
    private Long leadingMinQuality;
    @JsonProperty("trailing_min_quality")
    private Long trailingMinQuality;
    @JsonProperty("crop_length")
    private Long cropLength;
    @JsonProperty("head_crop_length")
    private Long headCropLength;
    @JsonProperty("min_length")
    private Long minLength;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("input_reads_ref")
    public String getInputReadsRef() {
        return inputReadsRef;
    }

    @JsonProperty("input_reads_ref")
    public void setInputReadsRef(String inputReadsRef) {
        this.inputReadsRef = inputReadsRef;
    }

    public ExecTrimmomaticInput withInputReadsRef(String inputReadsRef) {
        this.inputReadsRef = inputReadsRef;
        return this;
    }

    @JsonProperty("output_ws")
    public String getOutputWs() {
        return outputWs;
    }

    @JsonProperty("output_ws")
    public void setOutputWs(String outputWs) {
        this.outputWs = outputWs;
    }

    public ExecTrimmomaticInput withOutputWs(String outputWs) {
        this.outputWs = outputWs;
        return this;
    }

    @JsonProperty("output_reads_name")
    public String getOutputReadsName() {
        return outputReadsName;
    }

    @JsonProperty("output_reads_name")
    public void setOutputReadsName(String outputReadsName) {
        this.outputReadsName = outputReadsName;
    }

    public ExecTrimmomaticInput withOutputReadsName(String outputReadsName) {
        this.outputReadsName = outputReadsName;
        return this;
    }

    @JsonProperty("read_type")
    public String getReadType() {
        return readType;
    }

    @JsonProperty("read_type")
    public void setReadType(String readType) {
        this.readType = readType;
    }

    public ExecTrimmomaticInput withReadType(String readType) {
        this.readType = readType;
        return this;
    }

    @JsonProperty("adapterFa")
    public String getAdapterFa() {
        return adapterFa;
    }

    @JsonProperty("adapterFa")
    public void setAdapterFa(String adapterFa) {
        this.adapterFa = adapterFa;
    }

    public ExecTrimmomaticInput withAdapterFa(String adapterFa) {
        this.adapterFa = adapterFa;
        return this;
    }

    @JsonProperty("seed_mismatches")
    public Long getSeedMismatches() {
        return seedMismatches;
    }

    @JsonProperty("seed_mismatches")
    public void setSeedMismatches(Long seedMismatches) {
        this.seedMismatches = seedMismatches;
    }

    public ExecTrimmomaticInput withSeedMismatches(Long seedMismatches) {
        this.seedMismatches = seedMismatches;
        return this;
    }

    @JsonProperty("palindrome_clip_threshold")
    public Long getPalindromeClipThreshold() {
        return palindromeClipThreshold;
    }

    @JsonProperty("palindrome_clip_threshold")
    public void setPalindromeClipThreshold(Long palindromeClipThreshold) {
        this.palindromeClipThreshold = palindromeClipThreshold;
    }

    public ExecTrimmomaticInput withPalindromeClipThreshold(Long palindromeClipThreshold) {
        this.palindromeClipThreshold = palindromeClipThreshold;
        return this;
    }

    @JsonProperty("simple_clip_threshold")
    public Long getSimpleClipThreshold() {
        return simpleClipThreshold;
    }

    @JsonProperty("simple_clip_threshold")
    public void setSimpleClipThreshold(Long simpleClipThreshold) {
        this.simpleClipThreshold = simpleClipThreshold;
    }

    public ExecTrimmomaticInput withSimpleClipThreshold(Long simpleClipThreshold) {
        this.simpleClipThreshold = simpleClipThreshold;
        return this;
    }

    @JsonProperty("quality_encoding")
    public String getQualityEncoding() {
        return qualityEncoding;
    }

    @JsonProperty("quality_encoding")
    public void setQualityEncoding(String qualityEncoding) {
        this.qualityEncoding = qualityEncoding;
    }

    public ExecTrimmomaticInput withQualityEncoding(String qualityEncoding) {
        this.qualityEncoding = qualityEncoding;
        return this;
    }

    @JsonProperty("sliding_window_size")
    public Long getSlidingWindowSize() {
        return slidingWindowSize;
    }

    @JsonProperty("sliding_window_size")
    public void setSlidingWindowSize(Long slidingWindowSize) {
        this.slidingWindowSize = slidingWindowSize;
    }

    public ExecTrimmomaticInput withSlidingWindowSize(Long slidingWindowSize) {
        this.slidingWindowSize = slidingWindowSize;
        return this;
    }

    @JsonProperty("sliding_window_min_quality")
    public Long getSlidingWindowMinQuality() {
        return slidingWindowMinQuality;
    }

    @JsonProperty("sliding_window_min_quality")
    public void setSlidingWindowMinQuality(Long slidingWindowMinQuality) {
        this.slidingWindowMinQuality = slidingWindowMinQuality;
    }

    public ExecTrimmomaticInput withSlidingWindowMinQuality(Long slidingWindowMinQuality) {
        this.slidingWindowMinQuality = slidingWindowMinQuality;
        return this;
    }

    @JsonProperty("leading_min_quality")
    public Long getLeadingMinQuality() {
        return leadingMinQuality;
    }

    @JsonProperty("leading_min_quality")
    public void setLeadingMinQuality(Long leadingMinQuality) {
        this.leadingMinQuality = leadingMinQuality;
    }

    public ExecTrimmomaticInput withLeadingMinQuality(Long leadingMinQuality) {
        this.leadingMinQuality = leadingMinQuality;
        return this;
    }

    @JsonProperty("trailing_min_quality")
    public Long getTrailingMinQuality() {
        return trailingMinQuality;
    }

    @JsonProperty("trailing_min_quality")
    public void setTrailingMinQuality(Long trailingMinQuality) {
        this.trailingMinQuality = trailingMinQuality;
    }

    public ExecTrimmomaticInput withTrailingMinQuality(Long trailingMinQuality) {
        this.trailingMinQuality = trailingMinQuality;
        return this;
    }

    @JsonProperty("crop_length")
    public Long getCropLength() {
        return cropLength;
    }

    @JsonProperty("crop_length")
    public void setCropLength(Long cropLength) {
        this.cropLength = cropLength;
    }

    public ExecTrimmomaticInput withCropLength(Long cropLength) {
        this.cropLength = cropLength;
        return this;
    }

    @JsonProperty("head_crop_length")
    public Long getHeadCropLength() {
        return headCropLength;
    }

    @JsonProperty("head_crop_length")
    public void setHeadCropLength(Long headCropLength) {
        this.headCropLength = headCropLength;
    }

    public ExecTrimmomaticInput withHeadCropLength(Long headCropLength) {
        this.headCropLength = headCropLength;
        return this;
    }

    @JsonProperty("min_length")
    public Long getMinLength() {
        return minLength;
    }

    @JsonProperty("min_length")
    public void setMinLength(Long minLength) {
        this.minLength = minLength;
    }

    public ExecTrimmomaticInput withMinLength(Long minLength) {
        this.minLength = minLength;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((((((((((((((((((((((((((((("ExecTrimmomaticInput"+" [inputReadsRef=")+ inputReadsRef)+", outputWs=")+ outputWs)+", outputReadsName=")+ outputReadsName)+", readType=")+ readType)+", adapterFa=")+ adapterFa)+", seedMismatches=")+ seedMismatches)+", palindromeClipThreshold=")+ palindromeClipThreshold)+", simpleClipThreshold=")+ simpleClipThreshold)+", qualityEncoding=")+ qualityEncoding)+", slidingWindowSize=")+ slidingWindowSize)+", slidingWindowMinQuality=")+ slidingWindowMinQuality)+", leadingMinQuality=")+ leadingMinQuality)+", trailingMinQuality=")+ trailingMinQuality)+", cropLength=")+ cropLength)+", headCropLength=")+ headCropLength)+", minLength=")+ minLength)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
