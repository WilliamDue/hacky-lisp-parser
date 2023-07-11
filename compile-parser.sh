parallel-parser parser.cg -q 1 -k 1
futhark pkg add github.com/diku-dk/sorts
futhark pkg sync
futhark c --library parser.fut
build_futhark_ffi parser
