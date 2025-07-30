"""Generate JSON schema for EditablePaperWithExperiment data type."""

import msgspec

from phylodata.data_types import EditablePaperWithExperiment

schema = msgspec.json.schema(EditablePaperWithExperiment)

with open("../website/src/lib/schema.json", "wb") as f:
    f.write(msgspec.json.format(msgspec.json.encode(schema)))
