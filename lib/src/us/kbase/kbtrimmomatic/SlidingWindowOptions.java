
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
 * <p>Original spec-file type: SlidingWindow_Options</p>
 * <pre>
 * parameter groups
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "sliding_window_size",
    "sliding_window_min_quality"
})
public class SlidingWindowOptions {

    @JsonProperty("sliding_window_size")
    private Long slidingWindowSize;
    @JsonProperty("sliding_window_min_quality")
    private Long slidingWindowMinQuality;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("sliding_window_size")
    public Long getSlidingWindowSize() {
        return slidingWindowSize;
    }

    @JsonProperty("sliding_window_size")
    public void setSlidingWindowSize(Long slidingWindowSize) {
        this.slidingWindowSize = slidingWindowSize;
    }

    public SlidingWindowOptions withSlidingWindowSize(Long slidingWindowSize) {
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

    public SlidingWindowOptions withSlidingWindowMinQuality(Long slidingWindowMinQuality) {
        this.slidingWindowMinQuality = slidingWindowMinQuality;
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
        return ((((((("SlidingWindowOptions"+" [slidingWindowSize=")+ slidingWindowSize)+", slidingWindowMinQuality=")+ slidingWindowMinQuality)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
