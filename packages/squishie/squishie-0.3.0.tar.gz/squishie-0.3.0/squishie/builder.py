# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import typing
from pathlib import Path

import frontmatter
import msgspec
import yaml

from .models import Document, Section


def load_document(file: typing.IO):
    return msgspec.yaml.decode(file.read(), type=Document)


def build_page(text: str) -> str:
    metadata, content = frontmatter.parse(text)
    return "# {}\n\n{}".format(metadata["title"], content).rstrip()


def build_section(doc_dir: Path, section: Section) -> str:
    return build_page(open(doc_dir / section.file).read())


def filter_metadata(
    metadata: typing.Dict[str, typing.Any],
) -> typing.Dict[str, typing.Any]:
    return {
        key: value
        for key, value in metadata.items()
        if key
        not in (
            "title",
            "version",
        )
    }


def build_document(doc_dir: Path, document: Document) -> str:
    content = "\n\n".join(
        [build_section(doc_dir, section) for section in document.sections]
    )

    metadata = filter_metadata(document.metadata)

    output = ""
    output += "---\n"

    output += yaml.dump(
        dict(
            title=document.title,
            version=document.version,
        )
    )

    if metadata:
        output += "\n# metadata\n"
        output += yaml.dump(metadata)

    output += "---\n\n"

    output += content + "\n"

    return output
