from io import BytesIO

import streamlit as st

from phylodata.data_types import EvolutionaryModel
from phylodata.evolutionary_model.parse_evolutionary_model import (
    parse_evolutionary_model,
)
from phylodata.module import Module


class EvolutionaryModelModule(Module[EvolutionaryModel]):
    def ui(self): ...

    def validate(self): ...

    def parse(self, beast2_configuration: BytesIO) -> EvolutionaryModel:
        st.text("Detecting the evolutionary model...")
        return parse_evolutionary_model(beast2_configuration)
