# -*- coding: utf-8 -*-
"""
A memory-efficient ETL script to process ROS 2 bag files into HDF5 format.

This script is designed to be used within an Apache Airflow environment,
specifically with the PythonVirtualenvOperator. It reads ROS bag folders,
processes the messages in a streaming fashion to avoid high memory usage,
and saves the structured data into HDF5 files using PyTables.

Key Features:
- **Streaming Pipeline**: Avoids loading entire bag files into memory,
  preventing Out-of-Memory (OOM) errors with large files.
- **Dynamic Schema Creation**: Inspects ROS message types to automatically
  create corresponding table structures in the HDF5 file.
- **State Management**: Keeps track of already processed folders to avoid
  redundant work across DAG runs.
- **Custom Message Support**: Can register and use custom ROS message
  definitions provided in external folders.
"""

import gc
import keyword
import logging
import os
import pickle
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Type

import numpy as np
# The 'tables' and 'rosbags' imports are moved into the functions that use them.

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# --- Utility Functions ---


def sanitize_hdf5_identifier(name: str) -> str:
    """
    Cleans a string to make it a valid HDF5/PyTables identifier.

    This involves removing invalid characters, ensuring it doesn't start
    with a number, and appending an underscore if it's a Python keyword.

    Args:
        name: The input string to sanitize.

    Returns:
        A sanitized string suitable for use as a table or group name.
    """
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if sanitized and sanitized[0].isdigit():
        sanitized = "_" + sanitized
    if keyword.iskeyword(sanitized):
        sanitized += "_"
    return sanitized if sanitized else "unnamed"


def get_value_recursive(obj: Any, field_path_parts: List[str]) -> Any:
    """
    Safely retrieves a nested attribute from a message object.

    Traverses the object using a list of attribute names. Handles cases
    where parts of the path do not exist.

    Args:
        obj: The message object to traverse.
        field_path_parts: A list of strings representing the path.

    Returns:
        The retrieved value, or None if the path is invalid.
    """
    value = obj
    for part in field_path_parts:
        if value is None:
            return None
        try:
            value = getattr(value, part)
        except AttributeError:
            return None
    # Handle ROS Time/Duration objects
    if type(value).__name__ in ("Time", "Duration") and hasattr(value, "sec"):
        return value.sec + value.nanosec * 1e-9
    return value


def get_all_fields(
    typename: str,
    typestore: Any,
    current_prefix: str = "",
    visited: Optional[Set[str]] = None,
) -> List[Tuple[str, str, bool]]:
    """
    Recursively flattens a ROS message type to get all its fields.

    Args:
        typename: The name of the ROS message type (e.g., 'std_msgs/msg/String').
        typestore: The rosbags typestore instance.
        current_prefix: The prefix for the current nesting level.
        visited: A set of already visited type names to prevent infinite recursion.

    Returns:
        A list of tuples, where each tuple contains (flat_field_name, field_ros_type, is_array).
    """
    task_logger = logging.getLogger(f"{__name__}.get_all_fields")
    if visited is None:
        visited = set()
    if typename in visited:
        return []
    visited.add(typename)
    fields_list = []

    try:
        msg_def = typestore.get_msgdef(typename)
        field_defs = msg_def.fields
    except (KeyError, AttributeError):
        task_logger.warning(f"Could not find or parse message definition for type '{typename}'.")
        return []

    # Handle both list and dict formats for field definitions
    field_iterator = field_defs.items() if isinstance(field_defs, dict) else field_defs

    for field_info in field_iterator:
        field_name, field_type_tuple = field_info
        flat_name = f"{current_prefix}{field_name}"
        node_type_int, type_details = field_type_tuple

        is_array = node_type_int in (3, 4)  # 3=ARRAY, 4=SEQUENCE
        element_type_name = None

        if node_type_int in (1, 2):  # BASE or NAME
            element_type_name = type_details[0] if node_type_int == 1 else type_details
        elif is_array:
            element_type_tuple = type_details[0]
            element_nodetype_int, element_details = element_type_tuple
            if element_nodetype_int == 1:  # Array of BASE
                element_type_name = element_details[0]
            elif element_nodetype_int == 2:  # Array of NAME
                element_type_name = element_details

        if not element_type_name:
            continue

        is_complex = element_type_name in typestore.types and hasattr(typestore.get_msgdef(element_type_name), 'fields')

        if is_complex:
            nested_fields = get_all_fields(
                element_type_name, typestore, f"{flat_name}_", visited.copy()
            )
            fields_list.extend(nested_fields)
        else:
            fields_list.append((flat_name, element_type_name, is_array))

    return fields_list


def parse_external_msg_definitions(
    definition_folders: List[str], task_logger: logging.Logger
) -> Dict[str, str]:
    """
    Scans specified folders for ROS message definitions (.msg, .srv, .action).

    Args:
        definition_folders: A list of paths to scan for message definitions.
        task_logger: The logger instance to use for output.

    Returns:
        A dictionary mapping fully-qualified ROS type names to their definition strings.
    """
    all_external_defs: Dict[str, str] = {}
    if not definition_folders:
        return {}

    for folder_path_str in definition_folders:
        base_path = Path(folder_path_str)
        if not base_path.is_dir():
            task_logger.warning(f"Provided definition path is not a directory: {folder_path_str}")
            continue

        msg_files = list(base_path.rglob("*.msg"))
        for def_file_path in msg_files:
            try:
                # Assumes a standard layout like .../my_package/msg/MyMessage.msg
                parts = def_file_path.parts
                if len(parts) >= 3 and parts[-2] == 'msg':
                    pkg_name = parts[-3]
                    type_stem = def_file_path.stem
                    ros_type_name = f"{pkg_name}/msg/{type_stem}"
                    content = def_file_path.read_text(encoding="utf-8")
                    all_external_defs[ros_type_name] = content
            except Exception as e:
                task_logger.error(f"Error processing definition file {def_file_path}: {e}")

    task_logger.info(f"Collected {len(all_external_defs)} external type definitions.")
    return all_external_defs


# --- DAG Task Functions ---


def get_dag_config(**context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses and validates the DAG run configuration from Airflow context.

    Args:
        context: The Airflow task instance context.

    Returns:
        A dictionary containing the validated configuration parameters.
    """
    params = context.get("params", {})
    config = {
        "input_folder": params.get("input_folder"),
        "output_folder": params.get("output_folder"),
        "ros_distro": params.get("ros_distro", "humble"),
        "custom_msg_definition_folders": params.get("custom_msg_definition_folders", []) or [],
        "timestamp_hdf5_name": params.get("timestamp_hdf5_name", "timestamp_s"),
        "hdf5_chunk_size": params.get("hdf5_chunk_size", 5000),
    }
    if not all([config["input_folder"], config["output_folder"]]):
        raise ValueError("'input_folder' and 'output_folder' must be provided in DAG params.")
    logger.info(f"DAG Configuration loaded: {config}")
    return config


def find_untransformed_folders(config: Dict[str, Any]) -> List[str]:
    """
    Scans the input directory and identifies rosbag folders that have not yet been processed.

    It checks for a state file (`processed_rosbags_folders.pkl`) in the output
    directory to determine which folders have been successfully processed in previous runs.

    Args:
        config: The DAG configuration dictionary.

    Returns:
        A sorted list of absolute paths to the rosbag folders that need processing.
    """
    input_folder = config["input_folder"]
    output_folder = config["output_folder"]
    pickle_path = os.path.join(output_folder, "processed_rosbags_folders.pkl")
    already_transformed_folders: Set[str] = set()

    if os.path.exists(pickle_path):
        try:
            with open(pickle_path, "rb") as f:
                loaded_data = pickle.load(f)
                if isinstance(loaded_data, set):
                    already_transformed_folders = loaded_data
        except (pickle.UnpicklingError, EOFError):
            logger.warning(f"State file {pickle_path} is corrupted. Re-initializing.")

    try:
        all_potential_folders = [
            d for d in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, d))
        ]
        rosbag_folders = {
            d for d in all_potential_folders if os.path.isfile(os.path.join(input_folder, d, "metadata.yaml"))
        }
        untransformed_names = sorted(list(rosbag_folders - already_transformed_folders))
        untransformed_paths = [os.path.join(input_folder, name) for name in untransformed_names]
        
        logger.info(f"Found {len(rosbag_folders)} total rosbags. "
                    f"{len(already_transformed_folders)} already processed. "
                    f"{len(untransformed_paths)} new folders to process.")
        return untransformed_paths
    except FileNotFoundError:
        logger.error(f"Input directory not found: {input_folder}")
        return []


def prepare_processing_kwargs(config: Dict[str, Any], untransformed_folder_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Formats the list of folder paths and static config into a list of dictionaries
    for dynamic task mapping.

    Args:
        config: The static DAG configuration dictionary.
        untransformed_folder_paths: A list of folder paths to be processed.

    Returns:
        A list of dictionaries, where each dict contains all arguments for one task call.
    """
    if not untransformed_folder_paths:
        logger.info("No new folders to process, returning empty list for mapping.")
        return []
    
    kwargs_list = [
        {"config": config, "folder_path": path}
        for path in untransformed_folder_paths
    ]
    logger.info(f"Prepared {len(kwargs_list)} arguments for dynamic task processing.")
    return kwargs_list


def process_rosbag_to_hdf5(config: Dict[str, Any], folder_path: str) -> Dict[str, Any]:
    """
    Processes a single rosbag folder and streams its contents into an HDF5 file.

    This function accepts 'config' and 'folder_path' as separate keyword arguments
    to be compatible with Airflow's dynamic task mapping.

    Args:
        config: The static DAG configuration dictionary.
        folder_path: The absolute path to the rosbag folder to process.

    Returns:
        A dictionary summarizing the result of the operation.
    """
    import tables
    from rosbags.highlevel import AnyReader
    import logging
    import os
    from preprocessing.ros_etl_utils import sanitize_hdf5_identifier, _initialize_typestore, _stream_and_write_chunks, _prepare_hdf5_tables
    import gc
    from pathlib import Path


    task_logger = logging.getLogger(f"{__name__}.process_rosbag")
    folder_name = os.path.basename(folder_path)
    safe_folder_name = sanitize_hdf5_identifier(folder_name)
    output_hdf5_path = os.path.join(config["output_folder"], f"{safe_folder_name}.h5")
    task_logger.info(f"START: Processing '{folder_name}' -> '{output_hdf5_path}'")

    h5file = None
    try:
        typestore = _initialize_typestore(config, task_logger)
        h5file = tables.open_file(output_hdf5_path, mode="w", title=f"Data from {folder_name}")
        
        with AnyReader([Path(folder_path)], default_typestore=typestore) as reader:
            table_info_map = _prepare_hdf5_tables(reader, h5file, typestore, config, task_logger)
            if not table_info_map:
                raise RuntimeError("No valid HDF5 tables could be prepared.")
            
            _stream_and_write_chunks(reader, table_info_map, config, task_logger)

        task_logger.info(f"SUCCESS: Finished processing '{folder_name}'.")
        return {"input_foldername": folder_name, "status": "success"}

    except Exception as e:
        task_logger.critical(f"FAILURE: Error processing {folder_name}: {e}", exc_info=True)
        # Cleanup partially created file on error
        if h5file and h5file.isopen:
            h5file.close()
        if os.path.exists(output_hdf5_path):
            os.remove(output_hdf5_path)
        return {"input_foldername": folder_name, "status": "failed"}
    finally:
        if h5file and h5file.isopen:
            h5file.close()
        gc.collect()


def log_processed_folders(
    config: Dict[str, Any],
    processed_results: List[Optional[Dict[str, str]]],
) -> None:
    """
    Updates the state file with the names of successfully processed folders.

    Args:
        config: The DAG configuration dictionary.
        processed_results: A list of result dictionaries from the processing tasks.
    """
    pickle_path = os.path.join(config["output_folder"], "processed_rosbags_folders.pkl")
    
    try:
        with open(pickle_path, "rb") as f:
            previously_processed = pickle.load(f)
    except (FileNotFoundError, pickle.UnpicklingError):
        previously_processed = set()

    newly_processed = {
        res["input_foldername"]
        for res in processed_results
        if res and res.get("status") == "success"
    }

    if not newly_processed:
        logger.info("No new folders were successfully processed in this run.")
        return

    updated_set = previously_processed.union(newly_processed)
    try:
        with open(pickle_path, "wb") as f:
            pickle.dump(updated_set, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info(f"Updated state file. Added {len(newly_processed)} folders. "
                    f"Total processed: {len(updated_set)}.")
    except Exception as e:
        logger.critical(f"CRITICAL: Failed to write state file to {pickle_path}: {e}")


# --- Core Processing Helper Functions ---


def _initialize_typestore(config: Dict[str, Any], task_logger: logging.Logger):
    """Initializes the rosbags typestore and registers custom message types."""
    from rosbags.typesys import Stores, get_typestore, get_types_from_msg

    ros_distro = config.get("ros_distro", "humble").upper()
    typestore_enum = getattr(Stores, f"ROS2_{ros_distro}", Stores.ROS2_HUMBLE)
    typestore = get_typestore(typestore_enum)
    
    custom_msg_folders = config.get("custom_msg_definition_folders", [])
    if custom_msg_folders:
        task_logger.info("Parsing external message definitions...")
        custom_defs_text = parse_external_msg_definitions(custom_msg_folders, task_logger)
        custom_types = {}
        for name, text in custom_defs_text.items():
            try:
                custom_types.update(get_types_from_msg(text, name))
            except Exception as e:
                task_logger.error(f"Failed to parse custom message '{name}': {e}")
        
        if custom_types:
            typestore.register(custom_types)
            task_logger.info(f"Successfully registered {len(custom_types)} custom message types.")
    
    task_logger.info(f"Initialized typestore for ROS 2 {ros_distro}.")
    return typestore


def _prepare_hdf5_tables(
    reader,
    h5file,
    typestore,
    config: Dict[str, Any],
    task_logger: logging.Logger,
) -> Dict[str, Dict[str, Any]]:
    """
    Scans rosbag connections and creates corresponding HDF5 tables.

    This function does NOT read message data. It only inspects metadata to
    build the HDF5 file structure upfront.
    """
    import tables
    import os 

    table_info_map = {}
    filters = tables.Filters(complib="zlib", complevel=5)

    for conn in reader.connections:
        try:
            table_description, numpy_dtype, field_details = _create_schema_for_topic(conn.msgtype, typestore, config, task_logger)
            if not table_description:
                task_logger.warning(f"Could not create schema for topic '{conn.topic}'. Skipping.")
                continue

            full_topic_path = conn.topic.strip("/")
            parent_group = os.path.dirname("/" + full_topic_path)
            table_name = os.path.basename(full_topic_path)

            table = h5file.create_table(
                where=parent_group,
                name=table_name,
                description=table_description,
                title=f"Data for topic {conn.topic}",
                filters=filters,
                expectedrows=conn.msgcount,
                createparents=True
            )

            table_info_map[conn.topic] = {
                "table": table,
                "numpy_dtype": numpy_dtype,
                "field_details": field_details,
            }
        except Exception as e:
            task_logger.error(f"Failed to prepare table for topic '{conn.topic}': {e}")

    task_logger.info(f"Prepared {len(table_info_map)} HDF5 tables.")
    return table_info_map


def _stream_and_write_chunks(
    reader,
    table_info_map: Dict[str, Dict[str, Any]],
    config: Dict[str, Any],
    task_logger: logging.Logger,
):
    """
    Streams messages from the rosbag, buffers them, and writes them in chunks.
    """
    CHUNK_SIZE = config.get("hdf5_chunk_size", 5000)
    topic_buffers = {
        topic: {"data": [], "count": 0} for topic in table_info_map
    }

    connections_to_process = [
        conn for conn in reader.connections if conn.topic in table_info_map
    ]

    task_logger.info(f"Streaming messages with chunk size {CHUNK_SIZE}...")
    for conn, timestamp, rawdata in reader.messages(connections=connections_to_process):
        topic = conn.topic
        buffer = topic_buffers[topic]
        info = table_info_map[topic]
        
        msg = reader.deserialize(rawdata, conn.msgtype)
        row_data = _create_row_from_message(msg, info["field_details"], timestamp)
        buffer["data"].append(row_data)
        buffer["count"] += 1
        
        if buffer["count"] >= CHUNK_SIZE:
            structured_array = np.array(buffer["data"], dtype=info["numpy_dtype"])
            info["table"].append(structured_array)
            buffer["data"].clear()
            buffer["count"] = 0

    task_logger.info("Writing final chunks...")
    for topic, buffer in topic_buffers.items():
        if buffer["count"] > 0:
            info = table_info_map[topic]
            structured_array = np.array(buffer["data"], dtype=info["numpy_dtype"])
            info["table"].append(structured_array)


def _create_schema_for_topic(
    msgtype_name: str, typestore, config: Dict[str, Any], task_logger: logging.Logger
):
    """
    Creates PyTables description, NumPy dtype, and field details for a given message type.
    """
    import tables

    pytables_desc = {}
    numpy_dtype_list = []
    field_details = {}

    ts_name = sanitize_hdf5_identifier(config["timestamp_hdf5_name"])
    pytables_desc[ts_name] = tables.Float64Col(pos=0)
    numpy_dtype_list.append((ts_name, np.float64))
    field_details[ts_name] = {'is_timestamp': True}
    col_pos = 1

    TYPE_MAP = {
        'bool': (tables.BoolCol, np.bool_), 'byte': (tables.Int8Col, np.int8),
        'char': (tables.UInt8Col, np.uint8), 'float32': (tables.Float32Col, np.float32),
        'float64': (tables.Float64Col, np.float64), 'int8': (tables.Int8Col, np.int8),
        'uint8': (tables.UInt8Col, np.uint8), 'int16': (tables.Int16Col, np.int16),
        'uint16': (tables.UInt16Col, np.uint16), 'int32': (tables.Int32Col, np.int32),
        'uint32': (tables.UInt32Col, np.uint32), 'int64': (tables.Int64Col, np.int64),
        'uint64': (tables.UInt64Col, np.uint64),
    }

    all_fields = get_all_fields(msgtype_name, typestore)

    for flat_field_name, ros_type, is_array in all_fields:
        sanitized_name = sanitize_hdf5_identifier(flat_field_name)
        if sanitized_name in pytables_desc:
            task_logger.warning(f"Skipping field '{flat_field_name}' due to name collision on '{sanitized_name}'.")
            continue

        col_options = {"pos": col_pos}
        pytables_col = None
        numpy_dt = None
        
        if is_array:
            itemsize = 65535
            pytables_col = tables.StringCol
            col_options['itemsize'] = itemsize
            numpy_dt = f'S{itemsize}'
        elif ros_type == 'string':
            itemsize = 256
            pytables_col = tables.StringCol
            col_options['itemsize'] = itemsize
            numpy_dt = f'S{itemsize}'
        elif ros_type in TYPE_MAP:
            pytables_col, numpy_dt = TYPE_MAP[ros_type]
        else:
            task_logger.warning(f"Field '{flat_field_name}' has an unhandled type '{ros_type}'. Skipping.")
            continue

        pytables_desc[sanitized_name] = pytables_col(**col_options)
        numpy_dtype_list.append((sanitized_name, numpy_dt))
        field_details[sanitized_name] = {
            'original_name': flat_field_name,
            'is_array': is_array,
            'numpy_dt': numpy_dt,
        }
        col_pos += 1

    if len(pytables_desc) <= 1:
        return None, None, None

    description_class = type(f"Desc_{sanitize_hdf5_identifier(msgtype_name)}", (tables.IsDescription,), pytables_desc)
    return description_class, np.dtype(numpy_dtype_list), field_details


def _create_row_from_message(
    msg: Any, field_details: Dict, timestamp: int
) -> Tuple:
    """
    Converts a deserialized message object into a tuple for a structured NumPy array.
    """
    import pickle
    import numpy as np
    
    row_values = []
    for field_name, details in field_details.items():
        if details.get('is_timestamp'):
            row_values.append(timestamp / 1e9)
            continue

        value = get_value_recursive(msg, details['original_name'].split('_'))
        
        if details.get('is_array'):
            if value is None:
                value = b''
            else:
                try:
                    value = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                except Exception:
                    value = b''
        elif value is None:
            numpy_type = details.get('numpy_dt')
            if isinstance(numpy_type, type) and np.issubdtype(numpy_type, np.floating):
                value = np.nan
            elif isinstance(numpy_type, type) and np.issubdtype(numpy_type, np.integer):
                value = 0
            elif isinstance(numpy_type, type) and np.issubdtype(numpy_type, np.bool_):
                value = False
            else:
                value = b''

        row_values.append(value)
    return tuple(row_values)
