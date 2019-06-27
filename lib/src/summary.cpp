#include <ecl3/summary.h>

const char** ecl3_smspec_keywords(void) {
    static const char* kws[] = {
        "INTEHEAD",
        "RESTART ",
        "DIMENS  ",
        "KEYWORDS",
        "WGNAMES ",
        "NAMES   ",
        "NUMS    ",
        "LGRS    ",
        "NUMLX   ",
        "NUMLY   ",
        "NUMLZ   ",
        "LENGTHS ",
        "LENUNITS",
        "MEASRMNT",
        "UNITS   ",
        "STARTDAT",
        "LGRNAMES",
        "LGRVEC  ",
        "LGRTIMES",
        "RUNTIMEI",
        "RUNTIMED",
        "STEPRESN",
        "XCOORD  ",
        "YCOORD  ",
        "TIMESTMP",
        nullptr,
    };

    return kws;
}

const char* ecl3_unit_system_name(int sys) {
    switch (sys) {
        case ECL3_METRIC:   return "METRIC";
        case ECL3_FIELD:    return "FIELD";
        case ECL3_LAB:      return "LAB";
        case ECL3_PVTM:     return "PVT-M";

        default:            return nullptr;
    }
}

const char* ecl3_simulatorid_name(int id) {
    switch (id) {
        case ECL3_ECLIPSE100:           return "ECLIPSE 100";
        case ECL3_ECLIPSE300:           return "ECLIPSE 300";
        case ECL3_ECLIPSE300_THERMAL:   return "ECLIPSE 300 (thermal option)";
        case ECL3_INTERSECT:            return "INTERSECT";
        case ECL3_FRONTSIM:             return "FrontSim";

        default:                        return nullptr;
    }
}
