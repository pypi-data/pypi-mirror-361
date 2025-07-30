# Usage example
# python vaiml_shape_infer.py --input_model laion--CLIP-ViT-B-32-laion2B-s34B-b79K_im_bs_1.onnx --dim_config="text_batch_size={10}"

import argparse
import json
import logging

import numpy as np
import onnx
import sympy
from pathlib import Path
from onnx import helper, numpy_helper, shape_inference
from packaging import version
from onnxruntime.tools import symbolic_shape_infer

assert version.parse(onnx.__version__) >= version.parse("1.8.0")

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def splitter(line):
    line = line.split(" ")
    return line


def true_or_false(arg):
    ua = str(arg).upper()
    if "TRUE".startswith(ua):
        return True
    elif "FALSE".startswith(ua):
        return False
    else:
        raise TypeError
        pass


def generate_infer_shape_json(input_model, dim_config, output_dir):
    logger = logging.getLogger("generate_infer_shape_json")
    output_dir.mkdir(parents=True, exist_ok=True)
    infer_shape_json_file = output_dir / "infer_shape.json"
    logger.info(f"Generating infer_shape json file: {infer_shape_json_file}")

    dim_config = dim_config.split(",")
    dim_config_dict = {}
    for dim in dim_config:
        dim = dim.split("=")
        dim[0] = dim[0].strip()
        dim[1] = dim[1].strip()
        logger.info(f"dim: {dim}")
        int_array = list(map(int, dim[1].strip("{}").split()))
        dim_config_dict[dim[0]] = int_array
    logger.info("dim_config_dict: {}".format(dim_config_dict))

    total_seqs = 1
    # get toal number of combinations of the dimension configuration
    dim_config_combinations = [{}]
    for key in dim_config_dict.keys():
        total_seqs *= len(dim_config_dict[key])
        pre_combination_len = len(dim_config_combinations)
        for j in range(0, pre_combination_len):
            combination = dim_config_combinations[j]
            for i in range(0, len(dim_config_dict[key])):
                new_combination = combination.copy()
                new_combination[key] = dim_config_dict[key][i]
                dim_config_combinations.append(new_combination)
        # remove the first pre_combination_len elements
        del dim_config_combinations[0:pre_combination_len]
    logger.info("total_seqs: {}".format(total_seqs))
    logger.info(f"dim_config_combinations: {dim_config_combinations}")

    shape_infer_dict = {}
    # create a dictionary that has the key value between 1 and total_seqs
    for i in range(1, total_seqs + 1):
        shape_infer_dict[i] = {}
        shape_infer_dict[i]["inputs"] = {}
        shape_infer_dict[i]["outputs"] = {}

    # load the model
    input_model = args.input_model
    model_path = Path(input_model)
    dim_updated = False
    if not model_path.exists():
        logger.info(f"Model {input_model} does not exist, exit...")
        sys.exit(1)
    model = onnx.load(args.input_model)
    # get the input and output names and shapes and store them in the shape_infer_dict
    for i in range(1, total_seqs + 1):
        for input in model.graph.input:
            input_name = input.name
            input_shape = []
            for dim in input.type.tensor_type.shape.dim:
                if dim.dim_param in dim_config_dict.keys():
                    shape = dim_config_combinations[i - 1][dim.dim_param]
                    # convert it to a string
                    input_shape.append(shape)
                    dim_updated = True
                    logger.info(
                        f"dimension {dim.dim_param} of input {input_name} is updated with {shape} "
                    )
                else:
                    shape = dim.dim_value
                    input_shape.append(shape)
            shape_infer_dict[i]["inputs"][input_name] = " ".join(map(str, input_shape))
        for output in model.graph.output:
            output_name = output.name
            output_shape = []
            for dim in output.type.tensor_type.shape.dim:
                if dim.dim_param in dim_config_dict.keys():
                    shape = dim_config_combinations[i - 1][dim.dim_param]
                    # convert it to a string
                    output_shape.append(shape)
                    dim_updated = True
                    logger.info(
                        f"dimension {dim.dim_param} of output {output_name} is updated with {shape} "
                    )
                else:
                    shape = dim.dim_value
                    output_shape.append(shape)
            shape_infer_dict[i]["outputs"][output_name] = " ".join(
                map(str, output_shape)
            )

    # get the shape_info.json file under current directory
    if output_dir == "":
        json_dir = Path.cwd()
    else:
        json_dir = Path(output_dir)
    infer_shape_json_file = json_dir / "shape_infer.json"
    with open(infer_shape_json_file, "w") as f:
        json.dump(shape_infer_dict, f, indent=4)
    logger.info(f"{infer_shape_json_file} is generated.")

    return str(infer_shape_json_file)


def infer_models(input_model, infer_shape_json_file, output_dir, args):
    # load the json file and map each sequence length to the input output shape configurations
    model_name = Path(input_model).stem
    logger = logging.getLogger("infer_models")
    infer_shape_json_path = Path(infer_shape_json_file)
    if not infer_shape_json_path.exists():
        logger.info(f"{infer_shape_json_file} does not exist, exit...")
        sys.exit(1)
    with open(infer_shape_json_path, "r") as f:
        shape_infer_dict = json.load(f)

    model = onnx.load(input_model)
    # check if the model is valid
    try:
        onnx.checker.check_model(model)
    except Exception as e:
        logger.error(f"Model {input_model} is not valid: {e}")
        sys.exit(1)

    graph_inputs = model.graph.input
    graph_outputs = model.graph.output

    intermediate_model_path = Path(output_dir) / "intermediat.onnx"
    intermediate_model_name = str(intermediate_model_path)
    # iterate through the shape_infer_dict keys and generate one model for each key
    for key, value in shape_infer_dict.items():
        new_model_name = model_name + "_" + str(key) + ".onnx"
        new_model_path = output_dir / new_model_name
        logger.info(f"Generating model {new_model_path}...")
        for io_key, io_value in value.items():
            if io_key == "inputs":
                for input_key, input_value in io_value.items():
                    # update the input shape
                    dim_sizes = list(map(int, input_value.split(" ")))
                    for input in graph_inputs:
                        if input.name == input_key:
                            input_type = input.type.tensor_type
                            # update the shape
                            for i in range(len(input_type.shape.dim)):
                                input_type.shape.dim[i].dim_value = dim_sizes[i]
                            logger.info(
                                f"Updating input {input_key} shape to {dim_sizes}"
                            )
            elif io_key == "outputs":
                for output_key, output_value in io_value.items():
                    # update the output shape
                    dim_sizes = list(map(int, output_value.split(" ")))
                    for output in graph_outputs:
                        if output.name == output_key:
                            output_type = output.type.tensor_type
                            # update the shape
                            for i in range(len(output_type.shape.dim)):
                                output_type.shape.dim[i].dim_value = dim_sizes[i]
                            logger.info(
                                f"Updating output {output_key} shape to {dim_sizes}"
                            )
        # infer the shapes
        internal_model = onnx.shape_inference.infer_shapes(model)
        # save internal_model to intermediate_model_path
        onnx.save_model(internal_model, intermediate_model_name)
        # symbolic shape inference intermediate_model to new_model_path
        out_mp = symbolic_shape_infer.SymbolicShapeInference.infer_shapes(
            onnx.load(intermediate_model_name),
            args.int_max,
            args.auto_merge,
            args.guess_output_rank,
            args.verbose,
        )
        if out_mp:
            if args.save_as_external_data:
                onnx.save_model(
                    out_mp,
                    str(new_model_path),
                    save_as_external_data=True,
                    all_tensors_to_one_file=args.all_tensors_to_one_file,
                    location=args.external_data_location,
                    size_threshold=args.external_data_size_threshold,
                    convert_attribute=False,
                )
            else:
                onnx.save(out_mp, str(new_model_path))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Shape inference for dynamic ONNX models"
    )
    parser.add_argument(
        "--input_model",
        type=str,
        required=True,
        help="Path to the ONNX model file",
    )
    parser.add_argument(
        "--dim_config",
        type=str,
        default="",
        help="static values for the dynamic dimensions, e.g., 'batch_size={10}, sequence_length={8 256}'",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default=".",
        help="Path to save the inferred models. Default is current directory",
    )
    parser.add_argument(
        "--auto_merge",
        help="Automatically merge symbolic dims when confliction happens",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--int_max",
        help="maximum value for integer to be treated as boundless for ops like slice",
        type=int,
        default=2**31 - 1,
    )
    parser.add_argument(
        "--guess_output_rank",
        help="guess output rank to be the same as input 0 for unknown ops",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--verbose",
        help="Prints detailed logs of inference, 0: turn off, 1: warnings, 3: detailed",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--save_as_external_data",
        help="Saving an ONNX model to external data",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--all_tensors_to_one_file",
        help="Saving all the external data to one file",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--external_data_location",
        help="The file location to save the external file",
        default="./",
    )
    parser.add_argument(
        "--external_data_size_threshold",
        help="The size threshold for external data",
        type=int,
        default=1024,
    )
    return parser.parse_args()


if __name__ == "__main__":
    logger = logging.getLogger("__main__")
    args = parse_args()
    input_model = args.input_model
    dim_config = args.dim_config
    output_dir = args.output_dir
    model_name = Path(input_model).stem
    res_dir = Path(output_dir) / model_name

    logger.info(f"Input model: {input_model}")
    logger.info(f"Dim config: {dim_config}")
    logger.info(f"Results' dir: {res_dir}")

    infer_shape_json_file = generate_infer_shape_json(input_model, dim_config, res_dir)
    infer_models(input_model, infer_shape_json_file, res_dir, args)
    logger.info("Shape inference completed.")
