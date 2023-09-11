"""The buddy compiler backend for torch dynamo.
"""
import operator
from typing import List, Union, Callable
from torch import _inductor
import torch
from torch._functorch.aot_autograd import aot_module_simplified
import mlir.ir as ir
import mlir.dialects.func as func
from mlir.passmanager import PassManager
from .OperatorsGen import operation_func, ParamToConstantOp
import torch.utils._pytree as pytree
import os
from torch._subclasses import FakeTensorMode
from .global_var import *

def DynamoCompiler(gm: torch.fx.GraphModule,
                   inputs: List[torch.Tensor]) -> Callable:
  """The main entry point of buddy compiler for torch dynamo. It takes a FX
  graph module and a list of inputs as parameters. The compiler will first use
  PyTorch's AOT autograd to lower FX graph in Torch IR to Aten/Prims IR. Then
  it will map the operators in Aten/Prims IR to MLIR operations and generate an
  MLIR module. Finally, It will lower the MLIR module to LLVM dialect.

  Args:
    gm (torch.fx.GraphModule): The FX graph module to be compiled.
    inputs (List[torch.Tensor]): The inputs of the FX graph module.

  Returns:
    Callable: A compiled function that equivalent to the FX graph.

  """
  def _compiler(gm: torch.fx.GraphModule, inputs: List[torch.Tensor]):
    """Compile a FX graph in Aten/Prims IR to MLIR."""
    ctx = ir.Context()
    with ir.Location.unknown(ctx):
      fx_importer = FXGraphImporter(gm, inputs)
      module = fx_importer.import_graph(ctx)
      module = Lowering(module)
    return gm.forward
  # params = {
  #     **dict(gm.named_parameters(remove_duplicate=False)),
  #     **dict(gm.named_buffers(remove_duplicate=False)),
  # }
  # params_flat, params_spec = pytree.tree_flatten(params)
  # params_flat = list(params_flat)
  # with open(global_var_get_value('params-write-path')+"params_shape.txt", 'w') as file:
  #   for i, param in enumerate(params_flat):
  #     file.write("arg{} ".format(i))
  #     param_size = []
  #     for i in param.shape:
  #       param_size.append(str(i))
  #     file.write(",".join(param_size)+"\n")
  #     if not os.path.exists(global_var_get_value('params-write-path')+"params_data"):
  #       os.mkdir("params_data")
  #     param_data = param.detach().numpy().reshape([-1])
  #     param_data.tofile(global_var_get_value('params-write-path')+"params_data/arg{}.data".format(i))
  return aot_module_simplified(gm, inputs, fw_compiler=_compiler)

class FXGraphImporter:
  """The FX graph importer class."""

  def __init__(
      self,
      gm: torch.fx.GraphModule,
      inputs: List[torch.Tensor],
      func_name: str = "forward",
  ):
    """
    Args:
      gm (torch.fx.GraphModule): The FX graph module that will be imported.
      inputs (List[torch.Tensor]): Input tensor(s) of the FX graph.
      func_name (str): Name of the generated MLIR func.

    """
    self._symbol_table = {}
    self._gm = gm
    self._func_name = func_name

    # decide wether or not write params to mlir func
    if global_var_get_value('param-to-mlir'):
      #print('write params to mlir func file')
      # for llama2 the final input in inputs is input sentence
      self._inputs = [inputs[-1]]
      self._params = inputs[:-1]
    else:
      self._inputs = inputs
      self._params = []
    self._num_input_visited = 0
    self._module = ir.Module.create()
  def import_graph(self,
                   ctx: ir.Context) -> ir.Module:
    """Import the FX graph, generate an MLIR module in high-level dialects.

    Returns:
      mlir.ir.Module: An MLIR moduel in high-level dialects.

    """
    with ir.InsertionPoint(self._module.body):
      arguments = []
      for arg in self._inputs:
        shape_list = list(arg.shape)
        if str(arg.dtype) == "torch.bool":
          dtype = ir.IntegerType.get_signless(1)
        elif str(arg.dtype) == "torch.float32":
          dtype = ir.F32Type.get()
        elif str(arg.dtype) == "torch.int64":
          dtype = ir.IntegerType.get_signless(64)
        tensor_arg = ir.RankedTensorType.get(shape_list, dtype)
        arguments.append(tensor_arg)

      @func.FuncOp.from_py_func(*arguments, name=self._func_name)
      def generated_func(*args):
        args_list = list(args)
        for node in self._gm.graph.nodes:
          if node.op == "output":
            output_node_args = node.args[0]
            returns = []
            for output_arg in output_node_args:
              op = self._symbol_table.get((str(output_arg), 0))
              returns.append(op)

            # for model llama2, we only need output[0] to get next token
            returns = [returns[0]]
            self._symbol_table[("output", 0)] = returns
          elif node.op == "placeholder":
            self._import_placeholder(node, args_list)
          else:
            if node.target is operator.getitem:
              self._symbol_table[(str(node.name),
                                  0)] = self._symbol_table[(node.args[0],
                                                            node.args[1])]
            else:
              self._import_op(node, ctx)

        return self._symbol_table.get(("output", 0))

    print(self._module)
    return self._module

  def _import_placeholder(self, node: torch.fx.Node, args_list):
    if self._num_input_visited < len(self._params):
      self._symbol_table[(str(node.name), 0)] = ParamToConstantOp(node, self._num_input_visited).result
    else:
      placeholder_name = args_list[self._num_input_visited-len(self._params)]
      self._symbol_table[(str(node.name), 0)] = placeholder_name
    self._num_input_visited += 1

  def _import_op(self, node: torch.fx.Node,
                 ctx: ir.Context):
    op_name = node.target.__name__
    if op_name not in operation_func.keys():
      return
    op_ret: Union[ir.Operation,
                  tuple] = operation_func[op_name](node, self._symbol_table, ctx)
    assert op_ret is not None
    if isinstance(op_ret, tuple):
      for i, operation in op_ret:
        self._symbol_table[(str(node.name), i)] = operation.result
    else:
      self._symbol_table[(str(node.name), 0)] = op_ret.result


def Lowering(module: ir.Module):
  """Lower an MLIR module to LLVM dialect.

  Args:
    module (mlir.ir.Module): An MLIR module that need to be lowered.

  Returns:
    mlir.ir.Module: An MLIR module in LLVM dialect.

  """
  pm = PassManager("builtin.module")
  pm.add("func.func(tosa-to-linalg)")
  pm.add("func.func(tosa-to-tensor)")
  pm.add("func.func(tosa-to-arith)")
  pm.add("func.func(tosa-to-arith)")
  pm.add("empty-tensor-to-alloc-tensor")
  pm.add("convert-elementwise-to-linalg")
  pm.add("arith-bufferize")
  pm.add("func.func(linalg-bufferize)")
  pm.add("func.func(tensor-bufferize)")
  pm.add("func-bufferize")
  pm.run(module.operation)
  #print(module)
  pm.add("func.func(buffer-deallocation)")
  pm.add("func.func(convert-linalg-to-loops)")
  pm.add("convert-scf-to-cf")
  pm.add("convert-linalg-to-llvm")
  pm.add("convert-arith-to-llvm")
  pm.add("expand-strided-metadata")
  pm.add("finalize-memref-to-llvm")
  pm.add("convert-func-to-llvm")
  pm.add("reconcile-unrealized-casts")
  pm.run(module.operation)
  #print(module)
  return module
