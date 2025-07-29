# Copyright Teklia (contact@teklia.com) & Denis Coquenet
# This code is licensed under CeCILL-C

# -*- coding: utf-8 -*-

import json
import logging
import random
from collections import defaultdict
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List
from uuid import UUID

from tqdm import tqdm

from arkindex_export import Dataset, DatasetElement, Element, open_database
from dan import SPLIT_NAMES, TEST_NAME, TRAIN_NAME, VAL_NAME
from dan.datasets.extract.db import (
    get_dataset_elements,
    get_elements,
    get_transcription_entities,
    get_transcriptions,
)
from dan.datasets.extract.exceptions import (
    NoTranscriptionError,
    ProcessingError,
)
from dan.datasets.extract.utils import (
    entities_to_xml,
    get_translation_map,
    normalize_linebreaks,
    normalize_spaces,
)
from dan.utils import parse_tokens

logger = logging.getLogger(__name__)


class ArkindexExtractor:
    """
    Extract data from Arkindex
    """

    def __init__(
        self,
        output: Path,
        dataset_ids: List[UUID] | None = None,
        element_type: List[str] = [],
        entity_separators: List[str] = ["\n", " "],
        tokens: Path | None = None,
        transcription_worker_versions: List[str | bool] = [],
        entity_worker_versions: List[str | bool] = [],
        transcription_worker_runs: List[str | bool] = [],
        entity_worker_runs: List[str | bool] = [],
        keep_spaces: bool = False,
        allow_empty: bool = False,
    ) -> None:
        self.dataset_ids = dataset_ids
        self.element_type = element_type
        self.output = output
        self.entity_separators = entity_separators
        self.tokens = parse_tokens(tokens) if tokens else {}
        self.transcription_worker_versions = transcription_worker_versions
        self.entity_worker_versions = entity_worker_versions
        self.transcription_worker_runs = transcription_worker_runs
        self.entity_worker_runs = entity_worker_runs
        self.allow_empty = allow_empty
        self.keep_spaces = keep_spaces

        data_path = self.output / "split.json"
        # New keys can appear between several extractions
        # We must explicitly define that this dict expects a dict as its value
        self.data = defaultdict(dict)
        if data_path.exists():
            self.data.update(json.loads(data_path.read_text()))

        # NER extraction
        self.translation_map: Dict[str, str] | None = get_translation_map(self.tokens)

    def translate(self, text: str):
        """
        Use translation map to replace XML tags to actual tokens
        """
        for pattern, repl in self.translation_map.items():
            text = text.replace(pattern, repl)
        return text

    def extract_transcription(self, element: Element):
        """
        Extract the element's transcription.
        If the entities are needed, they are added to the transcription using tokens.
        """
        transcriptions = get_transcriptions(
            element.id,
            self.transcription_worker_versions,
            self.transcription_worker_runs,
        )
        if len(transcriptions) == 0:
            if self.allow_empty:
                return ""
            raise NoTranscriptionError(element.id)

        transcription = random.choice(transcriptions)
        stripped_text = transcription.text.strip()

        if not self.tokens:
            return stripped_text

        entities = get_transcription_entities(
            transcription.id,
            self.entity_worker_versions,
            self.entity_worker_runs,
            supported_types=list(self.tokens),
        )

        if not entities.count():
            return stripped_text

        return self.translate(
            entities_to_xml(
                transcription.text, entities, entity_separators=self.entity_separators
            )
        )

    def format_text(self, text: str):
        if not self.keep_spaces:
            text = normalize_spaces(text)
            text = normalize_linebreaks(text)

        return text.strip()

    def process_element(self, dataset_parent_id: str, element_id: str):
        """
        Extract an element's data and save it to disk.
        The output path is directly related to the split of the element.
        """
        dataset_parent = DatasetElement.get_by_id(dataset_parent_id)
        element = Element.get_by_id(element_id)

        try:
            text = self.extract_transcription(element)
            text = self.format_text(text)

            self.data[dataset_parent.set_name][element.id] = {
                "dataset_id": dataset_parent.dataset_id,
                "text": text,
                "image": {
                    "iiif_url": element.image.url,
                    "polygon": json.loads(element.polygon),
                },
            }
        except ProcessingError as e:
            logger.warning(f"Skipping {element_id}: {str(e)}")

    def list_dataset_elements(self, dataset_id: UUID) -> list[dict]:
        # Retrieve the Dataset and its splits from the cache
        dataset = Dataset.get_by_id(dataset_id)
        splits = dataset.sets.split(",")
        if not set(splits).issubset(set(SPLIT_NAMES)):
            logger.warning(
                f'Dataset {dataset.name} ({dataset.id}) does not have "{TRAIN_NAME}", "{VAL_NAME}" and "{TEST_NAME}" steps'
            )
            return []

        # Iterate over the subsets to find the page images and labels.
        tasks = []
        for split in splits:
            with tqdm(
                get_dataset_elements(dataset, split),
                desc=f"Listing elements to extract from ({dataset_id}) for split ({split})",
            ) as pbar:
                # Iterate over the pages to create splits at page level.
                for dataset_parent in pbar:
                    parent = dataset_parent.element
                    base_description = f"Listing elements to extract from {parent.type} ({parent.id}) for split ({dataset_parent.set_name})"
                    pbar.set_description(desc=base_description)

                    if self.element_type == [parent.type]:
                        tasks.append(
                            {
                                "dataset_parent_id": dataset_parent.id,
                                "element_id": parent.id,
                            }
                        )
                        continue

                    # List children elements
                    tasks.extend(
                        [
                            {
                                "dataset_parent_id": dataset_parent.id,
                                "element_id": child.id,
                            }
                            for child in get_elements(parent.id, self.element_type)
                        ]
                    )

        return tasks

    def export(self):
        (self.output / "split.json").write_text(
            json.dumps(
                self.data,
                sort_keys=True,
                indent=4,
            )
        )

    def run(self):
        tasks = []
        for dataset_id in self.dataset_ids:
            tasks.extend(self.list_dataset_elements(dataset_id))

        logger.info(f"Found {len(tasks)} dataset elements to extract.")

        with (
            tqdm(desc="Extracting dataset elements", total=len(tasks)) as pbar,
            ThreadPoolExecutor() as executor,
        ):

            def process_future(future: Future):
                """
                Callback function called at the end of the thread
                """
                # Update the progress bar count
                pbar.update(1)

            for task in tasks:
                executor.submit(self.process_element, **task).add_done_callback(
                    process_future
                )

        if not self.data:
            raise Exception(
                "No data was extracted using the provided export database and parameters."
            )

        self.export()


def run(
    database: Path,
    dataset_ids: List[UUID],
    element_type: List[str],
    output: Path,
    entity_separators: List[str],
    tokens: Path,
    transcription_worker_versions: List[str | bool],
    entity_worker_versions: List[str | bool],
    transcription_worker_runs: List[str | bool],
    entity_worker_runs: List[str | bool],
    keep_spaces: bool,
    allow_empty: bool,
):
    assert database.exists(), f"No file found @ {database}"
    open_database(path=database)

    # Create directories
    output.mkdir(parents=True, exist_ok=True)

    ArkindexExtractor(
        dataset_ids=dataset_ids,
        element_type=element_type,
        output=output,
        entity_separators=entity_separators,
        tokens=tokens,
        transcription_worker_versions=transcription_worker_versions,
        entity_worker_versions=entity_worker_versions,
        transcription_worker_runs=transcription_worker_runs,
        entity_worker_runs=entity_worker_runs,
        keep_spaces=keep_spaces,
        allow_empty=allow_empty,
    ).run()
