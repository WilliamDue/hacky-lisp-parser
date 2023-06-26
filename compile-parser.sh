parallel-parser parser.cg -q 1 -k 1
futhark opencl --library parser.fut
build_futhark_ffi parser