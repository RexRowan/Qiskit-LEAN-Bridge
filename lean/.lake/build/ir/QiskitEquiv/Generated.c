// Lean compiler output
// Module: QiskitEquiv.Generated
// Imports: public import Init public meta import Init public import Quantumlib.Data.Gate.Basic public import Quantumlib.Data.Gate.Rotate public import Quantumlib.Data.Gate.PhaseShift public import Quantumlib.Data.Gate.Pauli.Defs public import Quantumlib.Data.Gate.Equivs
#include <lean/lean.h>
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-label"
#elif defined(__GNUC__) && !defined(__CLANG__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-label"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#endif
#ifdef __cplusplus
extern "C" {
#endif
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_quantumlib_Quantumlib_Data_Gate_Basic(uint8_t builtin);
lean_object* initialize_quantumlib_Quantumlib_Data_Gate_Rotate(uint8_t builtin);
lean_object* initialize_quantumlib_Quantumlib_Data_Gate_PhaseShift(uint8_t builtin);
lean_object* initialize_quantumlib_Quantumlib_Data_Gate_Pauli_Defs(uint8_t builtin);
lean_object* initialize_quantumlib_Quantumlib_Data_Gate_Equivs(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_qiskit__equiv_QiskitEquiv_Generated(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_quantumlib_Quantumlib_Data_Gate_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_quantumlib_Quantumlib_Data_Gate_Rotate(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_quantumlib_Quantumlib_Data_Gate_PhaseShift(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_quantumlib_Quantumlib_Data_Gate_Pauli_Defs(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_quantumlib_Quantumlib_Data_Gate_Equivs(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
