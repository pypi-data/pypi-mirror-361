from typing import Literal
import codecs
from dkg.constants import CHUNK_BYTE_SIZE
from dkg.exceptions import DatasetInputFormatNotSupported, InvalidDataset
from dkg.types import JSONLD, NQuads
from pyld import jsonld
from dkg.constants import DEFAULT_RDF_FORMAT, DEFAULT_CANON_ALGORITHM, ESCAPE_MAP
from rdflib import Graph, BNode, URIRef, Dataset
from rdflib.exceptions import ParserError as RDFParserError
from uuid import uuid4
from web3 import Web3
import math
import hashlib
from eth_abi.packed import encode_packed


def normalize_dataset(
    dataset: JSONLD | NQuads,
    input_format: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
    output_format=DEFAULT_RDF_FORMAT,
    algorithm=DEFAULT_CANON_ALGORITHM,
) -> NQuads:
    normalization_options = {
        "algorithm": algorithm,
        "format": output_format,
    }

    match input_format.lower():
        case "json-ld" | "jsonld":
            pass
        case "n-quads" | "nquads":
            normalization_options["inputFormat"] = "application/n-quads"
        case _:
            raise DatasetInputFormatNotSupported(
                f"Dataset input format isn't supported: {input_format}. "
                "Supported formats: JSON-LD / N-Quads."
            )

    n_quads = jsonld.normalize(dataset, normalization_options)
    assertion = [quad for quad in n_quads.split("\n") if quad]

    if not assertion:
        raise InvalidDataset("Invalid dataset, no quads were extracted.")

    return assertion


def is_empty_dict(dictionary: dict):
    return len(dictionary.keys()) == 0 and isinstance(dictionary, dict)


def format_dataset(
    content: dict,
    input_format: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
    output_format=DEFAULT_RDF_FORMAT,
    algorithm=DEFAULT_CANON_ALGORITHM,
):
    private_assertion = None
    if content.get("private") and not is_empty_dict(content.get("private")):
        private_assertion = normalize_dataset(
            content.get("private"), input_format, output_format, algorithm
        )
    elif not content.get("public"):
        content = {"public": content}

    public_assertion = []
    if content.get("public"):
        public_assertion = normalize_dataset(
            content.get("public"), input_format, output_format, algorithm
        )

    if (
        public_assertion
        and len(public_assertion) == 0
        and private_assertion
        and len(private_assertion) == 0
    ):
        raise ValueError("File format is corrupted, no n-quads are extracted.")

    dataset = {"public": public_assertion}
    if private_assertion:
        dataset["private"] = private_assertion

    return dataset


def split_into_chunks(quads, chunk_size_bytes=32):
    # Concatenate the quads with newline characters
    concatenated_quads = "\n".join(quads)

    # Encode the concatenated string to bytes
    encoded_bytes = concatenated_quads.encode("utf-8")

    # Split the encoded bytes into chunks
    chunks = []
    start = 0

    while start < len(encoded_bytes):
        end = min(start + chunk_size_bytes, len(encoded_bytes))
        chunk = encoded_bytes[start:end]
        chunks.append(
            codecs.decode(chunk, "utf-8", errors="replace")
        )  # Decode bytes back to string
        start = end

    return chunks


def calculate_merkle_root(quads: list[str], chunk_size_bytes: int = CHUNK_BYTE_SIZE):
    chunks = split_into_chunks(quads, chunk_size_bytes)

    # Create leaves using solidityKeccak256 equivalent
    leaves = [
        bytes.fromhex(Web3.solidity_keccak(["string", "uint256"], [chunk, index]).hex())
        for index, chunk in enumerate(chunks)
    ]

    while len(leaves) > 1:
        next_level = []

        for i in range(0, len(leaves), 2):
            left = leaves[i]

            if i + 1 >= len(leaves):
                next_level.append(left)
                break

            right = leaves[i + 1]

            # Combine and sort the leaves
            combined = [left, right]
            combined.sort()

            # Calculate the hash of the combined leaves
            hash_value = Web3.keccak(b"".join(combined))
            next_level.append(hash_value)

        leaves = next_level

    return f"0x{leaves[0].hex()}"


def generate_missing_ids_for_blank_nodes(nquads_list: list[str] | None) -> list[str]:
    if not nquads_list:
        return [""]

    generated_ids = {}

    def replace_blank_node(term):
        # Handle blank nodes
        if isinstance(term, BNode):
            if str(term) not in generated_ids:
                generated_ids[str(term)] = URIRef(f"uuid:{str(uuid4())}")
            return generated_ids[str(term)]

        return term  # Return IRIs or Literals unchanged

    all_nquads = "\n".join(nquad for nquad in nquads_list if nquad.strip())

    # Create a single Dataset
    g = Graph()
    try:
        g.parse(data=all_nquads, format="nt")
    except RDFParserError:
        raise UnsupportedJSONLD(nquads_list)

    # Process all quads
    result = []
    for s, p, o in g:
        updated_quad = (
            replace_blank_node(s),
            replace_blank_node(p),
            replace_blank_node(o),
        )
        result.append(
            f"{updated_quad[0].n3()} {updated_quad[1].n3()} {updated_quad[2].n3()} ."
        )

    return result


def group_nquads_by_subject(nquads_list: list[str], sort: bool = False):
    grouped = {}

    all_nquads = "\n".join(nquad for nquad in nquads_list if nquad.strip())

    d = Dataset()
    d.parse(data=all_nquads, format="nquads")

    for quad in d:
        subject, predicate, obj, graph = quad

        # Get subject key
        subject_key = (
            f"<<<{subject.subject}> <{subject.predicate}> <{subject.object}>>"
            if hasattr(subject, "subject")
            else f"<{subject}>"
        )

        # Initialize group if needed
        if subject_key not in grouped:
            grouped[subject_key] = []

        # Add quad to group
        quad_string = f"{subject.n3()} {predicate.n3()} {obj.n3()} ."
        grouped[subject_key].append(quad_string)

    # Return grouped quads (sorted if requested)
    grouped_items = sorted(grouped.items()) if sort else grouped.items()
    if sort:
        return [sorted(quads) for _, quads in grouped_items]
    else:
        return [quads for _, quads in grouped_items]


def calculate_number_of_chunks(quads, chunk_size_bytes=CHUNK_BYTE_SIZE):
    # Concatenate the quads with newline characters
    concatenated_quads = "\n".join(quads)

    total_size_bytes = len(concatenated_quads.encode("utf-8"))

    # Calculate and return the number of chunks
    return math.ceil(total_size_bytes / chunk_size_bytes)


def count_distinct_subjects(nquads_list: list[str]) -> int:
    # Create a new RDF graph
    graph = Graph()

    # Parse the joined N-Quads
    graph.parse(data="\n".join(nquads_list), format="nquads")

    # Extract unique subjects using set comprehension
    subjects = {str(quad[0]) for quad in graph}

    return len(subjects)


def solidity_packed_sha256(types: list[str], values: list) -> str:
    # Encode the values using eth_abi's encode_packed
    packed_data = encode_packed(types, values)

    # Calculate SHA256
    sha256_hash = hashlib.sha256(packed_data).hexdigest()

    return f"0x{sha256_hash}"


def escape_literal_string(s):
    for char, replacement in ESCAPE_MAP.items():
        s = s.replace(char, replacement)
    return s


def escape_literal_dict(obj):
    if isinstance(obj, dict):
        return {k: escape_literal_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [escape_literal_dict(i) for i in obj]
    elif isinstance(obj, str):
        return escape_literal_string(s=obj)
    else:
        return obj


# Used when JSON-LD parsing fails due to quads being passed instead of triples
class UnsupportedJSONLD(Exception):
    def __init__(self, nquads_list):
        self.nquads_list = nquads_list
        self.message = f"""
Unsupported JSON-LD input detected

After parsing the JSON-LD input, the parser detected creation of new named graphs.
The DKG does not support custom named graphs.

Problematic Quads:

{self.find_problematic_quads()}

Full Parsed N-Quads Array:

{self.format_nquads_list()}

"""
        super().__init__(self.message)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"

    def format_nquads_list(self):
        return "\n".join(nquad.strip() for nquad in self.nquads_list)

    def find_problematic_quads(self):
        problematic = []
        g = Graph()
        for quad in self.nquads_list:
            if not quad.strip():
                continue
            try:
                g.parse(data=quad, format="nt")
            except RDFParserError:
                problematic.append(quad)

        return "\n".join(f"{i + 1}. {quad}" for i, quad in enumerate(problematic))
