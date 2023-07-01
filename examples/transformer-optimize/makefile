#!/bin/bash
BUDDY_OPT := ../../build/bin/buddy-opt
MLIR_OPT := ../../llvm/build/bin/mlir-opt
MLIR_TRANSLATE := ../../llvm/build/bin/mlir-translate
MLIR_CPU_RUNNER := ../../llvm/build/bin/mlir-cpu-runner
LLC := ../../llvm/build/bin/llc
LLVM_AS := ../../llvm/build/bin/llvm-as
OPT_FLAG := -O0

ifeq ($(shell uname),Linux)
MLIR_RUNNER_UTILS := ../../llvm/build/lib/libmlir_runner_utils.so
MLIR_C_RUNNER_UTILS := ../../llvm/build/lib/libmlir_c_runner_utils.so
MLIR_ASYNC_RUNTIME := ../../llvm/build/lib/libmlir_async_runtime.so
MTRIPLE := x86_64-unknown-linux-gnu
else ifeq ($(shell uname),Darwin)
MLIR_RUNNER_UTILS := ../../llvm/build/lib/libmlir_runner_utils.dylib
MLIR_C_RUNNER_UTILS := ../../llvm/build/lib/libmlir_c_runner_utils.dylib
MLIR_ASYNC_RUNTIME := ../../llvm/build/lib/libmlir_async_runtime.dylib
MTRIPLE := x86_64-apple-darwin
endif

#transformer-lower:
#	@${MLIR_OPT} ./bert_tiny_mhlo.mlir \
#		-convert-vector-to-llvm \
#		-convert-memref-to-llvm -convert-arith-to-llvm  \
#		-convert-func-to-llvm -reconcile-unrealized-casts \
#		-o ./log.mlir
#
#transformer-translate:
#	@${MLIR_OPT} ./bert_tiny_mhlo.mlir \
#		-convert-vector-to-llvm \
#		-convert-memref-to-llvm -convert-arith-to-llvm  \
#		-convert-func-to-llvm -reconcile-unrealized-casts | \
#	${MLIR_TRANSLATE} --mlir-to-llvmir -o log.ll

#transformer-run:
#	@${MLIR_OPT} ./bert_tiny_mhlo.mlir --lower-affine  \
#		-convert-vector-to-llvm \
#		-convert-memref-to-llvm -convert-arith-to-llvm  \
#		-convert-func-to-llvm -reconcile-unrealized-casts | \
#	${MLIR_CPU_RUNNER} ${OPT_FLAG} -e main -entry-point-result=void \
#		-shared-libs=${MLIR_RUNNER_UTILS} -shared-libs=${MLIR_C_RUNNER_UTILS}
transformer-lower:
	@${MLIR_OPT} ./bert_tiny_mhlo.mlir \
		-pass-pipeline="builtin.module(func.func(tosa-to-linalg-named),func.func(tosa-to-tensor),func.func(tosa-to-linalg),func.func(tosa-to-arith))" | \
	${MLIR_OPT} --test-linalg-transform-patterns="test-generalize-pad-tensor" \
		--linalg-bufferize \
		--convert-linalg-to-loops \
		--func-bufferize \
		--arith-bufferize \
		--tensor-bufferize \
		--finalizing-bufferize \
		--convert-vector-to-scf \
		--convert-scf-to-cf \
		--expand-strided-metadata \
		--lower-affine \
		--convert-vector-to-llvm \
		--memref-expand \
		--arith-expand \
		--convert-arith-to-llvm \
		--finalize-memref-to-llvm \
		--convert-math-to-llvm \
		--convert-math-to-libm \
		--convert-func-to-llvm \
		--llvm-request-c-wrappers \
		--reconcile-unrealized-casts | \
	${MLIR_TRANSLATE} \
		-mlir-to-llvmir | \
	${LLVM_AS} | \
	${LLC} -filetype=obj ${OPT_FLAG} -o transformer.o
transformer-compile:
	g++ main.cc transformer.o /home/wlq/buddy-mlir/llvm/build/lib/libmlir_c_runner_utils.so -o main
#	${MLIR_CPU_RUNNER} ${OPT_FLAG} -e main -entry-point-result=void \
#		-shared-libs=${MLIR_RUNNER_UTILS} -shared-libs=${MLIR_C_RUNNER_UTILS}
transformer-jit:
	@${MLIR_OPT} ./bert_tiny_mhlo_run_JIT.mlir \
		-pass-pipeline="builtin.module(func.func(tosa-to-linalg-named),func.func(tosa-to-tensor),func.func(tosa-to-linalg),func.func(tosa-to-arith))" | \
	${MLIR_OPT} --test-linalg-transform-patterns="test-generalize-pad-tensor" \
		--empty-tensor-to-alloc-tensor \
		--linalg-bufferize \
		--convert-linalg-to-loops \
		--func-bufferize \
		--arith-bufferize \
		--tensor-bufferize \
		--finalizing-bufferize \
		--convert-vector-to-scf \
		--convert-scf-to-cf \
		--expand-strided-metadata \
		--lower-affine \
		--convert-vector-to-llvm \
		--memref-expand \
		--arith-expand \
		--convert-arith-to-llvm \
		--finalize-memref-to-llvm \
		--convert-math-to-llvm \
		--convert-math-to-libm \
		--llvm-request-c-wrappers \
		--convert-func-to-llvm \
		--reconcile-unrealized-casts | \
	${MLIR_CPU_RUNNER} ${OPT_FLAG} -e forward -entry-point-result=void \
		-shared-libs=${MLIR_RUNNER_UTILS} -shared-libs=${MLIR_C_RUNNER_UTILS}