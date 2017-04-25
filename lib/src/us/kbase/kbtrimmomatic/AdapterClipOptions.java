
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
 * <p>Original spec-file type: AdapterClip_Options</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "adapterFa",
    "seed_mismatches",
    "palindrome_clip_threshold",
    "simple_clip_threshold"
})
public class AdapterClipOptions {

    @JsonProperty("adapterFa")
    private String adapterFa;
    @JsonProperty("seed_mismatches")
    private Long seedMismatches;
    @JsonProperty("palindrome_clip_threshold")
    private Long palindromeClipThreshold;
    @JsonProperty("simple_clip_threshold")
    private Long simpleClipThreshold;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("adapterFa")
    public String getAdapterFa() {
        return adapterFa;
    }

    @JsonProperty("adapterFa")
    public void setAdapterFa(String adapterFa) {
        this.adapterFa = adapterFa;
    }

    public AdapterClipOptions withAdapterFa(String adapterFa) {
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

    public AdapterClipOptions withSeedMismatches(Long seedMismatches) {
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

    public AdapterClipOptions withPalindromeClipThreshold(Long palindromeClipThreshold) {
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

    public AdapterClipOptions withSimpleClipThreshold(Long simpleClipThreshold) {
        this.simpleClipThreshold = simpleClipThreshold;
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
        return ((((((((((("AdapterClipOptions"+" [adapterFa=")+ adapterFa)+", seedMismatches=")+ seedMismatches)+", palindromeClipThreshold=")+ palindromeClipThreshold)+", simpleClipThreshold=")+ simpleClipThreshold)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
