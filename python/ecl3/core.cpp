#include <array>
#include <fstream>
#include <sstream>
#include <string>
#include <string>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <ecl3/keyword.h>
#include <ecl3/summary.h>

namespace py = pybind11;

namespace {

struct array {
    char keyword[9] = {};
    char type[5] = {};
    int count;
    py::list values;
};

struct stream : std::ifstream {
    stream(const std::string& path) :
        std::ifstream(path, std::ios::binary | std::ios::in)
    {
        if (!this->is_open()) {
            const auto msg = "could not open file '" + path + "'";
            throw std::invalid_argument(msg);
        }

        auto errors = std::ios::failbit | std::ios::badbit | std::ios::eofbit;
        this->exceptions(errors);
    }

    std::vector< array > keywords();

};

array getheader(std::ifstream& fs) {
    array a;
    char buffer[16];
    fs.read(buffer, sizeof(buffer));

    auto err = ecl3_array_header(buffer, a.keyword, a.type, &a.count);

    if (err) {
        auto msg = std::string("invalid argument to ecl3_array_header: ");
        msg.insert(msg.end(), buffer, buffer + sizeof(buffer));
        throw std::invalid_argument(msg);
    }

    return a;
}

template < typename T >
void extend(py::list& l, const char* src, int n, T tmp) {
    for (int i = 0; i < n; ++i) {
        std::memcpy(&tmp, src + (i * sizeof(T)), sizeof(T));
        l.append(tmp);
    }
}

void extend_char(py::list& l, const char* src, int n) {
    char tmp[8];
    for (int i = 0; i < n; ++i) {
        std::memcpy(tmp, src + (i * sizeof(tmp)), sizeof(tmp));
        l.append(py::str(tmp, sizeof(tmp)));
    }
}

void extend(py::list& l, const char* src, ecl3_typeids type, int count) {
    switch (type) {
        case ECL3_INTE:
            extend(l, src, count, std::int32_t(0));
            break;

        case ECL3_REAL:
            extend(l, src, count, float(0));
            break;

        case ECL3_DOUB:
            extend(l, src, count, double(0));
            break;

        case ECL3_CHAR:
            extend_char(l, src, count);
            break;

        default:
            throw std::invalid_argument("unknown type");
    }
}

std::vector< array > stream::keywords() {
    std::vector< array > kws;

    std::array< char, sizeof(std::int32_t) > head;
    std::array< char, sizeof(std::int32_t) > tail;

    auto buffer = std::vector< char >();

    std::int32_t ix;
    float fx;
    double dx;
    char str[9] = "        ";

    while (true) {
        try {
            this->read(head.data(), sizeof(head));
        } catch (std::ios::failure&) {
            if (this->eof()) return kws;
            /* some error is set - propagate exception */
        }
        auto kw = getheader(*this);
        this->read(tail.data(), sizeof(tail));
        if (head != tail) {
            std::int32_t h;
            std::int32_t t;
            ecl3_get_native(&h, head.data(), ECL3_INTE, 1);
            ecl3_get_native(&t, tail.data(), ECL3_INTE, 1);

            std::stringstream ss;
            ss << "array header: "
               << "head (" << h << ")"
               << " != tail (" << t << ")"
            ;

            throw std::runtime_error(ss.str());
        }

        int err;
        int type;
        int size;
        int blocksize;
        err = ecl3_typeid(kw.type, &type);
        if (err) {
            auto msg = std::string("unknown type: '");
            msg += kw.type;
            msg += "'";
            throw std::invalid_argument(msg);
        }
        ecl3_type_size(type, &size);
        ecl3_block_size(type, &blocksize);
        int remaining = kw.count;

        while (remaining > 0) {
            this->read(head.data(), sizeof(head));
            std::int32_t elems;
            ecl3_get_native(&elems, head.data(), ECL3_INTE, 1);

            buffer.resize(elems);
            this->read(buffer.data(), elems);

            this->read(tail.data(), sizeof(tail));
            if (head != tail) {
                std::int32_t h;
                std::int32_t t;
                ecl3_get_native(&h, head.data(), ECL3_INTE, 1);
                ecl3_get_native(&t, tail.data(), ECL3_INTE, 1);

                std::stringstream ss;
                ss << "array body: "
                   << "head (" << h << ")"
                   << " != tail (" << t << ")"
                ;

                throw std::runtime_error(ss.str());
            }

            int count;
            ecl3_array_body(
                buffer.data(),
                buffer.data(),
                type,
                remaining,
                blocksize,
                &count
            );
            remaining -= count;
            extend(kw.values, buffer.data(), ecl3_typeids(type), count);
        }

        kws.push_back(kw);
    }

    return kws;
}

py::list spec_keywords() {
    py::list xs;
    auto kw = ecl3_smspec_keywords();
    while (*kw)
        xs.append(py::str(*kw++));
    return xs;
}

}

PYBIND11_MODULE(core, m) {
    py::class_<stream>(m, "stream")
        .def(py::init<const std::string&>())
        .def("keywords", &stream::keywords)
    ;

    py::class_<array>(m, "array")
        .def("__repr__", [](const array& x) {
            std::stringstream ss;

            auto kw = std::string(x.keyword);
            auto type = std::string(x.type);

            ss << "{ " << kw << ", " << type << ": [ ";

            for (const auto& val : x.values) {
                ss << py::str(val).cast< std::string >() << " ";
            }

            ss << "] }";
            return ss.str();
        })
        .def_readonly("keyword", &array::keyword)
        .def_readonly("values", &array::values)
    ;

    m.def("spec_keywords", spec_keywords);
    m.def("unitsystem",  ecl3_unit_system_name);
    m.def("simulatorid", ecl3_simulatorid_name);
}
