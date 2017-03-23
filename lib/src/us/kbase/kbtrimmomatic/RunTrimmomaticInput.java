
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
 * <p>Original spec-file type: runTrimmomaticInput</p>
 * <pre>
 * runTrimmomatic()
 * **
 * ** to backend a KBase App, potentially operating on ReadSets
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "input_ws",
    "input_reads_ref",
    "output_ws",
    "output_reads_name",
    "read_type",
    "quality_encoding",
    "adapter_clip",
    "sliding_window",
    "leading_min_quality",
    "trailing_min_quality",
    "crop_length",
    "head_crop_length",
    "min_length"
})
public class RunTrimmomaticInput {

    @JsonProperty("input_ws")
    private String inputWs;
    @JsonProperty("input_reads_ref")
    private String inputReadsRef;
    @JsonProperty("output_ws")
    private String outputWs;
    @JsonProperty("output_reads_name")
    private String outputReadsName;
    @JsonProperty("read_type")
    private String readType;
    @JsonProperty("quality_encoding")
    private String qualityEncoding;
    /**
     * <p>Original spec-file type: AdapterClip_Options</p>
     * 
     * 
     */
    @JsonProperty("adapter_clip")
    private AdapterClipOptions adapterClip;
    /**
     * <p>Original spec-file type: SlidingWindow_Options</p>
     * <pre>
     * parameter groups
     * </pre>
     * 
     */
    @JsonProperty("sliding_window")
    private SlidingWindowOptions slidingWindow;
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

    @JsonProperty("input_ws")
    public String getInputWs() {
        return inputWs;
    }

    @JsonProperty("input_ws")
    public void setInputWs(String inputWs) {
        this.inputWs = inputWs;
    }

    public RunTrimmomaticInput withInputWs(String inputWs) {
        this.inputWs = inputWs;
        return this;
    }

    @JsonProperty("input_reads_ref")
    public String getInputReadsRef() {
        return inputReadsRef;
    }

    @JsonProperty("input_reads_ref")
    public void setInputReadsRef(String inputReadsRef) {
        this.inputReadsRef = inputReadsRef;
    }

    public RunTrimmomaticInput withInputReadsRef(String inputReadsRef) {
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

    public RunTrimmomaticInput withOutputWs(String outputWs) {
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

    public RunTrimmomaticInput withOutputReadsName(String outputReadsName) {
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

    public RunTrimmomaticInput withReadType(String readType) {
        this.readType = readType;
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

    public RunTrimmomaticInput withQualityEncoding(String qualityEncoding) {
        this.qualityEncoding = qualityEncoding;
        return this;
    }

    /**
     * <p>Original spec-file type: AdapterClip_Options</p>
     * 
     * 
     */
    @JsonProperty("adapter_clip")
    public AdapterClipOptions getAdapterClip() {
        return adapterClip;
    }

    /**
     * <p>Original spec-file type: AdapterClip_Options</p>
     * 
     * 
     */
    @JsonProperty("adapter_clip")
    public void setAdapterClip(AdapterClipOptions adapterClip) {
        this.adapterClip = adapterClip;
    }

    public RunTrimmomaticInput withAdapterClip(AdapterClipOptions adapterClip) {
        this.adapterClip = adapterClip;
        return this;
    }

    /**
     * <p>Original spec-file type: SlidingWindow_Options</p>
     * <pre>
     * parameter groups
     * </pre>
     * 
     */
    @JsonProperty("sliding_window")
    public SlidingWindowOptions getSlidingWindow() {
        return slidingWindow;
    }

    /**
     * <p>Original spec-file type: SlidingWindow_Options</p>
     * <pre>
     * parameter groups
     * </pre>
     * 
     */
    @JsonProperty("sliding_window")
    public void setSlidingWindow(SlidingWindowOptions slidingWindow) {
        this.slidingWindow = slidingWindow;
    }

    public RunTrimmomaticInput withSlidingWindow(SlidingWindowOptions slidingWindow) {
        this.slidingWindow = slidingWindow;
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

    public RunTrimmomaticInput withLeadingMinQuality(Long leadingMinQuality) {
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

    public RunTrimmomaticInput withTrailingMinQuality(Long trailingMinQuality) {
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

    public RunTrimmomaticInput withCropLength(Long cropLength) {
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

    public RunTrimmomaticInput withHeadCropLength(Long headCropLength) {
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

    public RunTrimmomaticInput withMinLength(Long minLength) {
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
        return ((((((((((((((((((((((((((((("RunTrimmomaticInput"+" [inputWs=")+ inputWs)+", inputReadsRef=")+ inputReadsRef)+", outputWs=")+ outputWs)+", outputReadsName=")+ outputReadsName)+", readType=")+ readType)+", qualityEncoding=")+ qualityEncoding)+", adapterClip=")+ adapterClip)+", slidingWindow=")+ slidingWindow)+", leadingMinQuality=")+ leadingMinQuality)+", trailingMinQuality=")+ trailingMinQuality)+", cropLength=")+ cropLength)+", headCropLength=")+ headCropLength)+", minLength=")+ minLength)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
