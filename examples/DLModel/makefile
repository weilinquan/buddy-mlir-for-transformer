#!/bin/bash
BUDDY_OPT := ../../build/bin/buddy-opt
MLIR_OPT := ../../llvm/build/bin/mlir-opt
MLIR_TRANSLATE := ../../llvm/build/bin/mlir-translate
MLIR_CPU_RUNNER := ../../llvm/build/bin/mlir-cpu-runner
LLC := ../../llvm/build/bin/llc
OPT_FLAG := -O0
MLIR_RUNNER_UTILS := ../../llvm/build/lib/libmlir_runner_utils.dylib
MLIR_C_RUNNER_UTILS := ../../llvm/build/lib/libmlir_c_runner_utils.dylib
LLVM_AS := ../../llvm/build/bin/llvm-as

resnet-18-lower:
	@${MLIR_OPT} ./ResNet-18.mlir \
		-pass-pipeline="builtin.module(func.func(tosa-to-linalg-named),func.func(tosa-to-linalg),func.func(tosa-to-tensor),func.func(tosa-to-arith))" | \
	${MLIR_OPT} \
		--test-linalg-transform-patterns="test-generalize-pad-tensor" \
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
		--llvm-request-c-wrappers \
		--convert-func-to-llvm \
		--reconcile-unrealized-casts \
		-convert-scf-to-cf \
		-convert-cf-to-llvm | \
	${MLIR_TRANSLATE} \
		-mlir-to-llvmir | \
	llc -mtriple=x86_64 --filetype=obj -o resnet18-c.o
#		${MLIR_CPU_RUNNER} ${OPT_FLAG} -e main -entry-point-result=f32 \
#		-shared-libs=${MLIR_RUNNER_UTILS} -shared-libs=${MLIR_C_RUNNER_UTILS}
