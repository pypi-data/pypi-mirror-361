# squishie

<!-- BADGIE TIME -->

[![pipeline status](https://img.shields.io/gitlab/pipeline-status/saferatday0/sandbox/squishy?branch=main)](https://gitlab.com/saferatday0/sandbox/squishy/-/commits/main)
[![coverage report](https://img.shields.io/gitlab/pipeline-coverage/saferatday0/sandbox/squishy?branch=main)](https://gitlab.com/saferatday0/sandbox/squishy/-/commits/main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![cici enabled](https://img.shields.io/badge/%E2%9A%A1_cici-enabled-c0ff33)](https://gitlab.com/saferatday0/cici)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)

<!-- END BADGIE TIME -->

Squish multiple Pandoc-flavored Markdown files into one super squished document.

## Installation

```sh
python3 -m pip install squishie
```

## Usage

Create a directory with your Markdown files:

```console
$ tree
.
├── doc1.md
└── doc2.md

0 directories, 2 files
```

Each Markdown file should have Pandoc-compatible front matter. For example,
`doc1.md` has the following contents:

```yaml
# doc1.md
---
title: Doc 1
---
This is some text.
```

Add a squishie document file to the directory:

```yaml
# config.yaml
title: My squished document
version: "1.2.3"

sections:
  - file: doc1.md
  - file: doc2.md
```

Your directory should now look like this:

```console
$ tree
.
├── squishie.yaml
├── doc1.md
└── doc2.md

0 directories, 2 files
```

Run `squishie` with the `-c`/`--config` option to render the final document:

```sh
squishie -c squishie.yaml
```

```console
$ squishie -c squishie.yaml
---
title: My squished document
version: 1.2.3
---

# Doc 1

This is some text.

# Doc 2

This is different text.
```

Add the `-o`/`--output` option to write the output to a file:

```sh
squishie -c squishie.yaml -o my-squished-document.md
```

## License

Copyright 2025 UL Research Institutes.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
