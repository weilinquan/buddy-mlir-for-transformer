get_property(dialect_libs GLOBAL PROPERTY MLIR_DIALECT_LIBS)
get_property(conversion_libs GLOBAL PROPERTY MLIR_CONVERSION_LIBS)
set(LLVM_LINK_COMPONENTS
  Core
  Support
  AsmParser
  )

if(MLIR_INCLUDE_TESTS)
  set(test_libs
    MLIRTestFuncToLLVM
    MLIRAffineTransformsTestPasses
    MLIRArithTestPasses
    MLIRBufferizationTestPasses
    MLIRControlFlowTestPasses
    MLIRDLTITestPasses
    MLIRFuncTestPasses
    MLIRGPUTestPasses
    MLIRLinalgTestPasses
    MLIRLoopLikeInterfaceTestPasses
    MLIRMathTestPasses
    MLIRMemRefTestPasses
    MLIRNVGPUTestPasses
    MLIRSCFTestPasses
    MLIRShapeTestPasses
    MLIRSPIRVTestPasses
    MLIRTensorTestPasses
    MLIRTestAnalysis
    MLIRTestDialect
    MLIRTestDynDialect
    MLIRTestIR
    MLIRTestOneToNTypeConversionPass
    MLIRTestPass
    MLIRTestPDLL
    MLIRTestReducer
    MLIRTestRewrite
    MLIRTestTransformDialect
    MLIRTestTransforms
    MLIRTilingInterfaceTestPasses
    MLIRVectorTestPasses
    MLIRTestVectorToSPIRV
    MLIRLLVMTestPasses
    )
endif()

set(LIBS
  ${dialect_libs}
  ${conversion_libs}
  ${test_libs}
  MLIRAffineAnalysis
  MLIRAnalysis
  MLIRDialect
  MLIROptLib
  MLIRParser
  MLIRPass
  MLIRTransforms
  MLIRTransformUtils
  MLIRSupport
  MLIRIR
  )

# Exclude from libMLIR.so because this has static options intended for
# opt-like tools only.

add_llvm_tool(transformer-opt
transformer-opt.cpp

  DEPENDS
  ${LIBS}
  SUPPORT_PLUGINS
  )
target_link_libraries(transformer-opt PRIVATE ${LIBS})
