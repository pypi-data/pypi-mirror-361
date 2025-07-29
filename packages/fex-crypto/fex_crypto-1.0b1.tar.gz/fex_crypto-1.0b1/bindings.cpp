#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "fex.h"
#include <vector>

namespace py = pybind11;

// Helper: Encrypt data (with padding) using FEX
std::vector<uint8_t> py_encrypt(const std::vector<uint8_t>& data, const std::vector<uint8_t>& key) {
    FEX fex(key.data(), key.size());
    std::vector<uint8_t> padded = FEX::pad(data);
    for (size_t i = 0; i < padded.size(); i += FEX::BLOCK_SIZE) {
        fex.encrypt_block(&padded[i]);
    }
    return padded;
}

// Helper: Decrypt data (with unpadding) using FEX
std::vector<uint8_t> py_decrypt(const std::vector<uint8_t>& enc, const std::vector<uint8_t>& key) {
    if (enc.size() % FEX::BLOCK_SIZE != 0) throw std::runtime_error("Encrypted data not a multiple of block size");
    FEX fex(key.data(), key.size());
    std::vector<uint8_t> out = enc;
    for (size_t i = 0; i < out.size(); i += FEX::BLOCK_SIZE) {
        fex.decrypt_block(&out[i]);
    }
    return FEX::unpad(out);
}

PYBIND11_MODULE(fex, m) {
    m.doc() = "FEX v1.0-beta: Fast Encryption eXchange (novel symmetric cipher)";
    m.def("encrypt", &py_encrypt, py::arg("data"), py::arg("key"), "Encrypt data with FEX (returns bytes)");
    m.def("decrypt", &py_decrypt, py::arg("encrypted_data"), py::arg("key"), "Decrypt data with FEX (returns bytes)");
} 