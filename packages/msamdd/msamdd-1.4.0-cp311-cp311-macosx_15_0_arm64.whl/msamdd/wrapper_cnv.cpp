#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>  // <- add this

extern "C" int main_convex(int argc, char** argv);

namespace py = pybind11;

PYBIND11_MODULE(_optmsa_cnv, m) {
    m.doc() = "MSAMDD convex-gap alignment";

    m.def("run_convex",
        [](const std::vector<std::string>& flags) {
            std::vector<const char*> argv;
            argv.reserve(flags.size() + 1);
            argv.push_back("optmsa_cnv");
            for (auto& s : flags)
                argv.push_back(s.c_str());

            int code = main_convex((int)argv.size(), const_cast<char**>(argv.data()));

            std::cout << std::flush;  // <-- flush C++ stdout
            std::cerr << std::flush;  // <-- flush C++ stderr
            fflush(stdout);           // <-- flush C stdio
            fflush(stderr);           // <-- flush C stdio

            return code;
        },
        py::arg("flags") = std::vector<std::string>{}
    );
}
