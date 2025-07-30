# pully

<!-- BADGIE TIME -->

[![pipeline status](https://img.shields.io/gitlab/pipeline-status/saferatday0/sandbox/pully?branch=main)](https://gitlab.com/saferatday0/sandbox/pully/-/commits/main)
[![latest release](https://img.shields.io/gitlab/v/release/saferatday0/sandbox/pully)](https://gitlab.com/saferatday0/sandbox/pully/-/releases)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![cici enabled](https://img.shields.io/badge/%E2%9A%A1_cici-enabled-c0ff33)](https://gitlab.com/saferatday0/cici)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)

<!-- END BADGIE TIME -->

`pully` is a tool for managing a large number of Git repository checkouts
effectively.

## Installation

```sh
python3 -m pip install pully
```

## Usage

Track a group by path:

```sh
pully add -G saferatday0
```

Track a subgroup by path:

```sh
pully add -G saferatday0/infra
```

Track a project by path:

```sh
pully add -P saferatday0/badgie
```

A `.pully.json` file will be created to track your projects.
