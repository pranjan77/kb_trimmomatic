
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
 * <p>Original spec-file type: TrimmomaticInput</p>
 * <pre>
 * using KBaseFile.PairedEndLibrary
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "input_ws",
    "output_ws",
    "read_type",
    "input_read_library",
    "adapterFa",
    "seed_mismatches",
    "palindrom_clip_threshold",
    "simple_clip_threshold",
    "quality_encoding",
    "slinding_window_size",
    "sliding_window_min_quality",
    "leading_min_quality",
    "trailing_min_quality",
    "crop_length",
    "head_crop_length",
    "min_length",
    "output_read_library"
})
public class TrimmomaticInput {

    @JsonProperty("input_ws")
    private String inputWs;
    @JsonProperty("output_ws")
    private String outputWs;
    @JsonProperty("read_type")
    private String readType;
    @JsonProperty("input_read_library")
    private String inputReadLibrary;
    @JsonProperty("adapterFa")
    private String adapterFa;
    @JsonProperty("seed_mismatches")
    private Long seedMismatches;
    @JsonProperty("palindrom_clip_threshold")
    private Long palindromClipThreshold;
    @JsonProperty("simple_clip_threshold")
    private Long simpleClipThreshold;
    @JsonProperty("quality_encoding")
    private String qualityEncoding;
    @JsonProperty("slinding_window_size")
    private Long slindingWindowSize;
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
    @JsonProperty("output_read_library")
    private String outputReadLibrary;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("input_ws")
    public String getInputWs() {
        return inputWs;
    }

    @JsonProperty("input_ws")
    public void setInputWs(String inputWs) {
        this.inputWs = inputWs;
    }

    public TrimmomaticInput withInputWs(String inputWs) {
        this.inputWs = inputWs;
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

    public TrimmomaticInput withOutputWs(String outputWs) {
        this.outputWs = outputWs;
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

    public TrimmomaticInput withReadType(String readType) {
        this.readType = readType;
        return this;
    }

    @JsonProperty("input_read_library")
    public String getInputReadLibrary() {
        return inputReadLibrary;
    }

    @JsonProperty("input_read_library")
    public void setInputReadLibrary(String inputReadLibrary) {
        this.inputReadLibrary = inputReadLibrary;
    }

    public TrimmomaticInput withInputReadLibrary(String inputReadLibrary) {
        this.inputReadLibrary = inputReadLibrary;
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

    public TrimmomaticInput withAdapterFa(String adapterFa) {
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

    public TrimmomaticInput withSeedMismatches(Long seedMismatches) {
        this.seedMismatches = seedMismatches;
        return this;
    }

    @JsonProperty("palindrom_clip_threshold")
    public Long getPalindromClipThreshold() {
        return palindromClipThreshold;
    }

    @JsonProperty("palindrom_clip_threshold")
    public void setPalindromClipThreshold(Long palindromClipThreshold) {
        this.palindromClipThreshold = palindromClipThreshold;
    }

    public TrimmomaticInput withPalindromClipThreshold(Long palindromClipThreshold) {
        this.palindromClipThreshold = palindromClipThreshold;
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

    public TrimmomaticInput withSimpleClipThreshold(Long simpleClipThreshold) {
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

    public TrimmomaticInput withQualityEncoding(String qualityEncoding) {
        this.qualityEncoding = qualityEncoding;
        return this;
    }

    @JsonProperty("slinding_window_size")
    public Long getSlindingWindowSize() {
        return slindingWindowSize;
    }

    @JsonProperty("slinding_window_size")
    public void setSlindingWindowSize(Long slindingWindowSize) {
        this.slindingWindowSize = slindingWindowSize;
    }

    public TrimmomaticInput withSlindingWindowSize(Long slindingWindowSize) {
        this.slindingWindowSize = slindingWindowSize;
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

    public TrimmomaticInput withSlidingWindowMinQuality(Long slidingWindowMinQuality) {
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

    public TrimmomaticInput withLeadingMinQuality(Long leadingMinQuality) {
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

    public TrimmomaticInput withTrailingMinQuality(Long trailingMinQuality) {
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

    public TrimmomaticInput withCropLength(Long cropLength) {
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

    public TrimmomaticInput withHeadCropLength(Long headCropLength) {
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

    public TrimmomaticInput withMinLength(Long minLength) {
        this.minLength = minLength;
        return this;
    }

    @JsonProperty("output_read_library")
    public String getOutputReadLibrary() {
        return outputReadLibrary;
    }

    @JsonProperty("output_read_library")
    public void setOutputReadLibrary(String outputReadLibrary) {
        this.outputReadLibrary = outputReadLibrary;
    }

    public TrimmomaticInput withOutputReadLibrary(String outputReadLibrary) {
        this.outputReadLibrary = outputReadLibrary;
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
        return ((((((((((((((((((((((((((((((((((((("TrimmomaticInput"+" [inputWs=")+ inputWs)+", outputWs=")+ outputWs)+", readType=")+ readType)+", inputReadLibrary=")+ inputReadLibrary)+", adapterFa=")+ adapterFa)+", seedMismatches=")+ seedMismatches)+", palindromClipThreshold=")+ palindromClipThreshold)+", simpleClipThreshold=")+ simpleClipThreshold)+", qualityEncoding=")+ qualityEncoding)+", slindingWindowSize=")+ slindingWindowSize)+", slidingWindowMinQuality=")+ slidingWindowMinQuality)+", leadingMinQuality=")+ leadingMinQuality)+", trailingMinQuality=")+ trailingMinQuality)+", cropLength=")+ cropLength)+", headCropLength=")+ headCropLength)+", minLength=")+ minLength)+", outputReadLibrary=")+ outputReadLibrary)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
