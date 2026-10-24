

#include "base_predictor.h"

#include "tage/tage.h"
#include "tage/tage_scl.h"
#include "llbp/llbp.h"
#include "llbpx/llbpx.h"


BasePredictor* CreateBP(std::string bp_name, int access_delay)
{
    if (bp_name == "tage64k") {
        return new LLBP::Tage64k();
    } else if (bp_name == "tage64kscl") {
        return new LLBP::TageSCL64k();
    } else if (bp_name == "tage512kscl") {
        return new LLBP::TageSCL512k();
    } else if (bp_name == "tage-logg8scl") {
        return new LLBP::TageSCL(LLBP::TSCLConfig{
            .tageConfig = LLBP::TageConfig{.LogG = 8, .LogB = 13},
            .useSC = true,
            .useLoop = true
        });
    } else if (bp_name == "tage64kscl-reduced-tagged") {
        return new LLBP::TageSCL(LLBP::TSCLConfig{
            .tageConfig = LLBP::TageConfig{.LogG = 9, .LogB = 13},
            .useSC = true,
            .useLoop = true
        });
    } else if (bp_name == "tage64kscl-reduced-bimodal") {
        return new LLBP::TageSCL(LLBP::TSCLConfig{
            .tageConfig = LLBP::TageConfig{.LogG = 10, .LogB = 12},
            .useSC = true,
            .useLoop = true
        });
    } else if (bp_name == "tage64kscl-reduced-tage") {
        return new LLBP::TageSCL(LLBP::TSCLConfig{
            .tageConfig = LLBP::TageConfig{.LogG = 9, .LogB = 12},
            .useSC = true,
            .useLoop = true
        });
    } else if (bp_name == "llbp") {
        return new LLBP::LLBPTageSCL64k();
    } else if (bp_name == "llbp-timing") {
        return new LLBP::LLBPTageSCL64kTiming();
    } else if (bp_name == "llbpx") {
        return new LLBP::LLBPXTSCL64k();
    } else if (bp_name == "llbpx-logg8") {
        return new LLBP::LLBPXTSCLLogG8();
    } else if (bp_name == "llbpx-logg8-timing") {
        return new LLBP::LLBPXTSCLLogG8Timing(access_delay);
    } else if (bp_name == "llbpx-optw") {
        return new LLBP::LLBPXTSCL64kTimingOptW(access_delay);
    } else if (bp_name == "llbpx-timing") {
        return new LLBP::LLBPXTSCL64kTiming(access_delay);
    } else if (bp_name == "llbpx-reduced-tage") {
        return new LLBP::LLBPXTSCLReducedTage();
    } else if (bp_name == "llbpx-reduced-tagged") {
        return new LLBP::LLBPXTSCLReducedTagged();
    } else if (bp_name == "llbpx-reduced-bimodal") {
        return new LLBP::LLBPXTSCLReducedBimodal();
    } else if (bp_name == "llbpx-reduced-tagged-timing") {
        return new LLBP::LLBPXTSCLReducedTaggedTiming(access_delay);
    } else if (bp_name == "llbpx-reduced-bimodal-timing") {
        return new LLBP::LLBPXTSCLReducedBimodalTiming(access_delay);
    } else if (bp_name == "llbpx-reduced-tage-timing") {
        return new LLBP::LLBPXTSCLReducedTageTiming(access_delay);
    } else {
        std::cout << "Wrong BP name: " << bp_name << std::endl;
        exit(EXIT_FAILURE);
    }
}


