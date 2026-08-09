import Lake
open Lake DSL

package «qiskit_equiv» where
  -- add package configuration options here

@[default_target]
lean_lib «QiskitEquiv» where
  -- add library configuration options here

require Quantumlib from git
  "https://github.com/inQWIRE/LeanQuantum" @ "main"
