# Copyright (C) 2023 – 2025 Advanced Micro Devices, Inc. All rights reserved.
# Licensed under the MIT License.

import sys
import logging
import time
import json
from typing import Any, Optional
from pathlib import Path
from collections import deque
import onnx
import onnx.utils
from onnx import helper, shape_inference
from onnx.external_data_helper import load_external_data_for_model
import flexml
from importlib import metadata
import copy


def get_vitisai_root_dir() -> str:
    vitisai_root_dir = Path(__file__).parent
    return str(vitisai_root_dir)


def get_vaip_version() -> str:
    return metadata.metadata("voe")["Version"]


# pylint: disable=redefined-builtin
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=protected-access
# pylint: disable=broad-exception-raised
def load_onnx_modelfile(
    model_filename: str = "",
    onnx_external_data_dir: str = "",
) -> Any:
    logger = logging.getLogger("vaiml.compile_onnx2mlopslib")
    model = onnx.load(model_filename, load_external_data=False)

    # per Mathias' request, the onnx_external_data_dir handed to FE stay as it is.
    # if onnx_external_data_dir != "":
    #    # need to load external data
    #    logger.info(f"    Load external data from {onnx_external_data_dir}")
    #    load_external_data_for_model(model, onnx_external_data_dir)

    return model


# pylint: disable=redefined-builtin
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=protected-access
# pylint: disable=broad-exception-raised
def modify_batch_size(model_path, new_batch_size, output_path):
    # Load the ONNX model
    model = load_onnx_modelfile(model_path)

    # Modify the batch size of all input tensors
    for input_tensor in model.graph.input:
        shape = input_tensor.type.tensor_type.shape
        if len(shape.dim) > 0:
            shape.dim[0].dim_value = new_batch_size

    # Modify the batch size of all value_info tensors
    for value_info in model.graph.value_info:
        shape = value_info.type.tensor_type.shape
        if len(shape.dim) > 0:
            shape.dim[0].dim_value = new_batch_size

    # Modify the batch size of all output tensors
    for output_tensor in model.graph.output:
        shape = output_tensor.type.tensor_type.shape
        if len(shape.dim) > 0:
            shape.dim[0].dim_value = new_batch_size

    # Perform shape inference to propagate the new input shape
    model = shape_inference.infer_shapes(model)

    # Save the modified model to a file
    onnx.save(model, output_path)
    print(f"Modified model saved to {output_path}")


# pylint: disable=redefined-builtin
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=protected-access
# pylint: disable=broad-exception-raised
def compile_microkernel(
    model: Any,
    output_dir: str = "",
    hw_device: str = "stx",
    ai_analyzer_profiling: bool = False,
    ai_analyzer_visualization: bool = False,
    config_file: Optional[str] = None,
    visualization: bool = False,
    debug: bool = False,
) -> Any:
    logger = logging.getLogger("vaiml.compile_microkernel")

    try:
        print("    Compiling microkernel ...", flush=True)
        compiled_model = flexml.compile(
            model,
            None,  # input_shapes
            output_dir=output_dir,
            microkernel_option=1,  # microkernel only flow via custom-op
            fe_match_unsupported_kernels=True,
            device=hw_device,
            config=config_file,
            visualization=visualization,
            enable_f32_to_bf16_conversion=True,
        )
    except Exception as flexml_compile_exception:
        logger.error("Exception during flexml.compile. %s", flexml_compile_exception)
        raise flexml_compile_exception
        print("    Compilation of AIE partition completed", flush=True)
    return compiled_model


# pylint: disable=redefined-builtin
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=protected-access
# pylint: disable=broad-exception-raised
def compile_onnx2mlopslib(
    model_filename: str = "",
    output_dir: str = "",
    max_inputs: int = 0,
    max_outputs: int = 0,
    hw_device: str = "auto",
    ai_analyzer_profiling: bool = False,
    ai_analyzer_visualization: bool = False,
    hw_output_type: str = "aie-exe",
    enable_f32_to_bf16_conversion: Optional[bool] = False,
    enable_f16_to_bf16_conversion: Optional[bool] = False,
    config_file: Optional[str] = None,
    debug: bool = False,
    override_batch_size=False,
    fast_partition_swap: bool = True,
    onnx_external_data_dir: str = "",
    microkernel_operator: str = "",
    microkernel_overlay_array: str = "4x4",
    get_capability: bool = True,
    aie_single_core_compiler: str = "peano",
    enable_preemption: bool = False,
    logging_level: str = "error",
) -> Any:
    """
    This method uses the mlopslib compiler to compile the model.
    Inputs:
    hw_device:
        For internal debug only. Set the target device for flexml.compile()
    hw_output_type:
        For internal debug only. Set the output_type for flexml.compile()
    config_file:
        Json file to specify advanced internal options, all settings
        in config file will have higher precedence
    onnx_external_data_dir:
        Path only to the external data file. ONNX gets the relative file name
        from the model and appends to this path to get the final external
        data file name
    microkernel_operator
        Microkernel operator to be compiled
    microkernel_overlay_array
        4x4 or 2x4x4 overlay for microkernel tiling
    """
    logger = logging.getLogger("vaiml.compile_onnx2mlopslib")

    if model_filename.endswith("ukernel.mlir"):
        model = model_filename
        microkernel_option = 2
    else:
        if override_batch_size:
            model_dir = Path(model_filename).parent
            model_basename = Path(model_filename).stem
            new_batch_size = 1
            updated_model_filename = (
                model_dir / f"{model_basename}_batch{new_batch_size}.onnx"
            )
            modify_batch_size(model_filename, new_batch_size, updated_model_filename)
            model_filename = updated_model_filename

        model = load_onnx_modelfile(model_filename, onnx_external_data_dir)
        microkernel_option = 0
        assign_unique_names(model)
        logger.info(f"    Successfully loaded model {model_filename} ...")

    try:
        logger.info(
            f"    Compiling subgraph using vaiml.compile model_file={model_filename} onnx_external_data_dir={onnx_external_data_dir}"
        )
        flexml.set_ai_analyzer_profiling(ai_analyzer_profiling)
        flexml.set_ai_analyzer_visualization(ai_analyzer_visualization)
        compiled_model = flexml.compile(
            model,
            None,
            output_type=hw_output_type,
            max_inputs=max_inputs,
            max_outputs=max_outputs,
            output_dir=output_dir,
            dse_args="dse-hw-overlay=4x4 dse-memtile-rows=1",
            backend_args="memtile-rows=1",
            device=hw_device,
            partitioner="onnxruntime-vaip-vaiml-pass",
            enable_f32_to_bf16_conversion=enable_f32_to_bf16_conversion,
            enable_f16_to_bf16_conversion=enable_f16_to_bf16_conversion,
            fast_partition_swap=fast_partition_swap,
            config=config_file,
            microkernel_option=microkernel_option,
            onnx_external_data_dir=onnx_external_data_dir,
            microkernel_operator=microkernel_operator,
            microkernel_overlay_array=microkernel_overlay_array,
            get_capability=get_capability,
            aie_single_core_compiler=aie_single_core_compiler,
            enable_preemption=enable_preemption,
        )
    except Exception as flexml_compile_exception:
        # Only print error message if debug flag is set
        if debug:
            logger.error(
                "Exception during flexml.compile. %s", flexml_compile_exception
            )
            raise flexml_compile_exception
        else:
            compiled_model = None

    return compiled_model


def assign_unique_names(model):
    # Keep in sync with VaimlSubgraphProcessor::isNodeSupported!

    for node in model.graph.node:
        if len(node.name) == 0 and len(node.output) > 0:
            node.name = "=" + node.op_type + "->" + str(node.output[0])


def dynamic_shape_infer(model_file_name, fixed_seq_lens, batch_size, json_file_path):
    print(f"model_file_name: {model_file_name}")
    seq_len_list = fixed_seq_lens.split(",")
    seq_lens = [int(x.strip()) for x in seq_len_list]

    for seq_len in seq_lens:
        # Load the ONNX model
        model = load_onnx_modelfile(model_file_name)
        json_file_dir = Path(json_file_path + f"_{seq_len}")
        if not json_file_dir.exists():
            json_file_dir.mkdir(parents=True, exist_ok=True)
        shape_json_file = json_file_dir / f"fixed_shapes.json"

        for input_tensor in model.graph.input:
            # Extract the dimensions' names and values
            dims_info = input_tensor.type.tensor_type.shape.dim
            for dim in dims_info:
                if dim.dim_param:
                    if dim.dim_param == "batch_size":
                        dim.ClearField("dim_param")
                        dim.dim_value = batch_size
                    if dim.dim_param == "sequence_length":
                        dim.ClearField("dim_param")
                        dim.dim_value = seq_len

        for output_tensor in model.graph.output:
            for dim in output_tensor.type.tensor_type.shape.dim:
                if dim.dim_param:
                    if dim.dim_param == "batch_size":
                        dim.ClearField("dim_param")
                        dim.dim_value = batch_size
                    if dim.dim_param == "sequence_length":
                        dim.ClearField("dim_param")
                        dim.dim_value = seq_len

        inferred_model = onnx.shape_inference.infer_shapes(model)
        inferred_graph = inferred_model.graph

        known_shapes = {}
        known_dim_names = {}
        for value_info in inferred_graph.value_info:
            name = value_info.name
            shape = [dim.dim_value for dim in value_info.type.tensor_type.shape.dim]
            known_shapes[name] = shape

        json_data = {}
        for node in inferred_graph.node:
            for input_name in node.input:
                if input_name in known_shapes:
                    shape = known_shapes[input_name]
                    if len(shape) > 0 and shape[0] <= 0:
                        shape[0] = batch_size
                    if len(shape) > 1 and shape[1] <= 0:
                        shape[1] = seq_len
                    json_data[input_name] = shape

        with open(shape_json_file, "w") as f:
            json.dump(json_data, f, indent=4)


def experimental_partitioner(model_path, unsupported_ops_json):
    # Load the ONNX model
    model = onnx.load(model_path)
    with open(unsupported_ops_json, "r") as f:
        unsupported_ops = json.load(f)

    assign_unique_names(model)

    # Get the graph from the model
    graph = model.graph

    # Create a dependency graph
    dependency_graph = {}
    # Create a dictionary of edges
    edge_dict = {}
    count_nodes = 0

    for node in graph.node:
        if node.op_type:
            for name in node.output:
                edge_dict[name] = []
            count_nodes += 1
    for node in graph.node:
        dependency_graph[node.name] = {
            "node": node,
            "inputs": set(node.input),
            "outputs": set(node.output),
            "dependency_count": 0,
            "supported": node.name not in unsupported_ops,
        }
        for name in node.input:
            if name in edge_dict:
                edge_dict[name].append(node.name)
                dependency_graph[node.name]["dependency_count"] += 1

    def build_initial_headlists(head_list, next_head_list):
        root_nodes = []
        for node in graph.node:
            if dependency_graph[node.name]["dependency_count"] == 0:
                root_nodes.append(node.name)

        type_looking_for = dependency_graph[root_nodes[0]]["supported"]
        for node_name in root_nodes:
            if dependency_graph[node_name]["supported"] == type_looking_for:
                head_list.append(node_name)
            else:
                next_head_list.append(node_name)

    head_list = []
    next_head_list = []
    build_initial_headlists(head_list, next_head_list)

    head_list2 = next_head_list[:]
    next_head_list2 = head_list[:]

    npu_partitions = []
    cpu_partitions = []

    def graph_cluster_topolocial_sort(head_list, next_head_list):
        added_to_a_partition = set()

        def dfs(head, next_head_list):
            result = []
            # All the nodes sent by the head_list (head) should be part of the same partition
            while head:
                current_node = head.pop(0)
                node_type = dependency_graph[current_node]["supported"]
                # result.append(node_type)

                def _dfs(node_name):
                    if node_name in added_to_a_partition:
                        return

                    dependency_graph[node_name]["dependency_count"] -= 1
                    if (
                        dependency_graph[node_name]["dependency_count"] <= 0
                        and node_type == dependency_graph[node_name]["supported"]
                    ):
                        result.append(node_name)
                        added_to_a_partition.add(node_name)
                        for edge in dependency_graph[node_name]["outputs"]:
                            for child in edge_dict[edge]:
                                _dfs(child)
                    elif (
                        dependency_graph[node_name]["dependency_count"] <= 0
                        and node_type != dependency_graph[node_name]["supported"]
                    ):
                        next_head_list.append(node_name)

                _dfs(current_node)

            if node_type == True:
                npu_partitions.append(result)
            else:
                cpu_partitions.append(result)
            return next_head_list

        # While head_list is not empty (More partitions left)
        while head_list:
            head_list = dfs(head_list, next_head_list)
            next_head_list = []

    graph_cluster_topolocial_sort(head_list, next_head_list)

    dependency_graph = {}

    for node in graph.node:
        for name in node.output:
            edge_dict[name] = []
        count_nodes += 1
    for node in graph.node:
        dependency_graph[node.name] = {
            "node": node,
            "inputs": set(node.input),
            "outputs": set(node.output),
            "dependency_count": 0,
            "supported": node.name not in unsupported_ops,
        }
        for name in node.input:
            if name in edge_dict:
                edge_dict[name].append(node.name)
                dependency_graph[node.name]["dependency_count"] += 1

    npu_partitions_save = [partition[:] for partition in npu_partitions]
    cpu_partitions_save = [partition[:] for partition in cpu_partitions]
    npu_partitions = []
    cpu_partitions = []
    graph_cluster_topolocial_sort(head_list2, next_head_list2)

    max_size_ = 0
    for partition in npu_partitions_save:
        if len(partition) > max_size_:
            max_size_ = len(partition)
    max_size_1 = 0
    for partition in npu_partitions:
        if len(partition) > max_size_1:
            max_size_1 = len(partition)

    if max_size_ > max_size_1:
        npu_partitions = npu_partitions_save
        cpu_partitions = cpu_partitions_save

    all_partitions = {}
    for i, partition in enumerate(npu_partitions):
        partition_name = f"partition_{i}"
        all_partitions[partition_name] = []
        for node_name in partition:
            all_partitions[partition_name].append(node_name)

    unsupported_ops_json_folder = unsupported_ops_json.split("/")
    unsupported_ops_json_folder = unsupported_ops_json_folder[:-1]
    partition_result_json = (
        "/".join(unsupported_ops_json_folder) + "/partition_result.json"
    )

    with open(partition_result_json, "w") as f:
        json.dump(all_partitions, f, indent=4)

    return 1
