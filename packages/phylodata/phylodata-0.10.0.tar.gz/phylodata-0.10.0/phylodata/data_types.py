"""This file contains all the types which are used to describe a PhyloData experiment.

For some types, there is an *editable* and *non-editable* version. We make this distinction
for the following reasons:

-   We can create two metadata files, making it very obvious which information can be manually
    corrected by the user and which information is an automated output of the pipeline.
-   Given the pipeline version, the non-editable information should always be reproducible.
-   When the pipeline changes (e.g. new features get added), the user-made corrections to
    the editable metadata can easily be integrated again.
"""

from datetime import date
from enum import Enum
from hashlib import md5
from io import BytesIO
from typing import Any, Optional

import msgspec


class ExperimentType(Enum):
    BEAST2_Experiment = "beast2Experiment"


class ClassificationEntryType(Enum):
    NCBI_TAXONOMY_ID = "ncibTaxonomyId"
    GLOTTOLOG_ID = "glottologId"


class FileType(Enum):
    BEAST2_CONFIGURATION = "beast2Configuration"
    BEAST2_POSTERIOR_LOGS = "beast2PosteriorLogs"
    BEAST2_POSTERIOR_TREES = "beast2PosteriorTrees"
    SUMMARY_TREE = "summaryTree"
    CODEPHY_MODEL = "codephyModel"
    PHYLO_DATA_EXPERIMENT = "phyloDataExperiment"
    UNKNOWN = "unknown"


class SampleType(Enum):
    SPECIES = "species"
    CELLS = "cells"
    LANGUAGE = "language"
    UNKNOWN = "unknown"


class DataType(Enum):
    RNA = "rna"
    DNA = "dna"
    AMINO_ACIDS = "aminoAcids"
    PHASED_DIPLOID_DNA = "phasedDiploidDna"
    TRAITS = "traits"
    UNKNOWN = "unknown"


class ModelType(Enum):
    SUBSTITUTION_MODEL = "substitutionModel"
    CLOCK_MODEL = "clockModel"
    TREE_PRIOR = "treePrior"
    TREE_LIKELIHOOD = "treeLikelihood"
    OTHER = "other"


class EditableExperiment(msgspec.Struct, rename="camel"):
    type: ExperimentType
    title: Optional[str] = None
    description: Optional[str] = None


class NonEditableExperiment(msgspec.Struct, rename="camel"):
    human_readable_id: str
    origin: str
    upload_date: date
    license: str = "CC0"
    id: Optional[str] = None


class EditablePaper(msgspec.Struct, rename="camel"):
    title: str
    year: int
    authors: list[str]
    abstract: str
    bibtex: str
    url: Optional[str] = None


class NonEditablePaper(msgspec.Struct, rename="camel"):
    doi: str


class File(
    msgspec.Struct, rename="camel", dict=True
):  # dict is true to omit private values (https://github.com/jcrist/msgspec/issues/199#issuecomment-2840826792)
    name: str
    type: FileType
    version: int
    size_bytes: int
    md5: str
    is_preview: bool = False
    local_path: Optional[str] = None
    remote_path: Optional[str] = None

    def __post_init__(self):
        self.bytes: BytesIO | None = None

    def set_bytes(self, bytes: BytesIO) -> "File":
        self.bytes = bytes
        return self

    @classmethod
    def from_bytes(
        cls,
        bytes: BytesIO,
        name: str,
        type: FileType,
        version: int,
        is_preview: bool = False,
    ) -> "File":
        buffer = bytes.getbuffer()
        return File(
            name=name,
            type=type,
            version=version,
            is_preview=is_preview,
            size_bytes=buffer.nbytes,
            md5=md5(buffer).hexdigest(),
        ).set_bytes(bytes)


class SampleData(msgspec.Struct, rename="camel"):
    type: DataType
    length: int
    data: str


class ClassificationEntry(msgspec.Struct, rename="camel"):
    classification_id: str
    scientific_name: str
    id_type: ClassificationEntryType
    common_name: Optional[str] = None
    id: Optional[str] = None


class Sample(msgspec.Struct, rename="camel"):
    sample_id: str
    scientific_name: str
    type: SampleType
    classification: list[ClassificationEntry]
    data: list[SampleData]
    common_name: Optional[str] = None
    id: Optional[str] = None


class Trees(msgspec.Struct, rename="camel"):
    number_of_trees: int
    number_of_tips: int
    ultrametric: bool
    time_tree: bool
    rooted: bool
    ccd1_entropy: float
    tree_ess: int
    ccd0_map_tree: str
    hipstr_tree: str
    leaf_to_sample_map: dict[str, str]
    average_root_age: float


class EvolutionaryModelComponent(msgspec.Struct, rename="camel"):
    name: str
    description: str
    type: ModelType
    documentation_url: str
    parameters: dict[str, Any]


class EvolutionaryModel(msgspec.Struct, rename="camel"):
    models: list[EvolutionaryModelComponent]


class Metadata(msgspec.Struct, rename="camel"):
    evo_data_pipeline_version: str


class NonEditablePaperWithExperiment(msgspec.Struct, rename="camel"):
    """This structure contains all experiment data which is
    computed by the pipeline and must not be changed manually."""

    paper: NonEditablePaper
    experiment: NonEditableExperiment
    files: list[File]
    trees: Trees
    evolutionary_model: EvolutionaryModel
    metadata: Metadata


class EditablePaperWithExperiment(msgspec.Struct, rename="camel"):
    """This structure contains all experiment data computed by the pipeline
    and may be changed manually."""

    paper: EditablePaper
    experiment: EditableExperiment
    samples: list[Sample]


def validate_editable_json(file_path: str):
    """Validates if the given file contains a valid EditablePaperWithExperiment object.
    Throws a msgspec.ValidationError if not."""
    with open(file_path) as handle:
        msgspec.json.decode(handle.read(), type=EditablePaperWithExperiment)


def get_schema():
    """Returns the formatted JSON schema corresponding to EditablePaperWithExperiment."""
    schema = msgspec.json.schema(EditablePaperWithExperiment)
    return msgspec.json.format(msgspec.json.encode(schema).decode())
