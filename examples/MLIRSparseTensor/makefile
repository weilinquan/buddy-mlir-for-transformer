MLIR_OPT := ../../llvm/build/bin/mlir-opt
MLIR_CPU_RUNNER := ../../llvm/build/bin/mlir-cpu-runner
MLIR_TRANSLATE := ../../llvm/build/bin/mlir-translate
ifeq ($(shell uname),Linux)
MLIR_RUNNER_UTILS := ../../llvm/build/lib/libmlir_runner_utils.so
MLIR_C_RUNNER_UTILS := ../../llvm/build/lib/libmlir_c_runner_utils.so
MTRIPLE := x86_64-unknown-linux-gnu
else ifeq ($(shell uname),Darwin)
MLIR_RUNNER_UTILS := ../../llvm/build/lib/libmlir_runner_utils.dylib
MLIR_C_RUNNER_UTILS := ../../llvm/build/lib/libmlir_c_runner_utils.dylib
MTRIPLE := x86_64-apple-darwin
endif

SPARSE_MATRIX_A := ./data/sa.mtx
SPARSE_MATRIX_B := ./data/sb.mtx

sparse-tensor-fuse-tensor-cast-lower:
	@${MLIR_OPT} ./sparse-tensor-fuse-tensor-cast.mlir\
		--pre-sparsification-rewrite -o ./log.mlir

sparse-tensor-new-lower:
	@${MLIR_OPT} ./sparse-tensor-new.mlir \
		--sparse-compiler="enable-runtime-library=true" -o log.mlir
sparse-tensor-new-translate:
	@${MLIR_OPT} ./sparse-tensor-new.mlir \
		--sparse-compiler="enable-runtime-library=true" | \
	${MLIR_TRANSLATE} --mlir-to-llvmir -o log.ll
sparse-tensor-new-run:
	@${MLIR_OPT} ./sparse-tensor-new.mlir \
		--sparse-compiler="enable-runtime-library=true" | \
	TENSOR0=${SPARSE_MATRIX_A} TENSOR1=${SPARSE_MATRIX_B} \
	${MLIR_CPU_RUNNER} -e main -O0 --entry-point-result=void \
		--shared-libs=${MLIR_RUNNER_UTILS},${MLIR_C_RUNNER_UTILS}
