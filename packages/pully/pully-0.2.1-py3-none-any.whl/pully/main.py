# SPDX-FileCopyrightText: 2025 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import argparse
import subprocess
from pathlib import Path

import gitlab
from termcolor import colored

from . import pullyfile
from .pullyfile import PullyProject

BASE_DIR = Path.cwd()


def sync_project(glproject, project_path: Path):
    project_path.mkdir(exist_ok=True, parents=True)
    git_dir = project_path / ".git"
    if not git_dir.exists():
        print(
            colored("cloning", "green"),
            glproject.path_with_namespace,
            colored(f"({glproject.id})", "green"),
        )
        try:
            subprocess.run(
                ["git", "clone", glproject.ssh_url_to_repo, str(project_path)],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as excinfo:
            print(
                colored("failed", "yellow"),
                glproject.path_with_namespace,
                colored("(git error)", "yellow"),
            )
    else:
        print(
            colored(
                f"skipping {glproject.path_with_namespace} (already cloned)", "grey"
            )
        )


def get_gitlab_group_id_from_full_path(gl: gitlab.Gitlab, group_path: str) -> int:
    print("searching for group id by full path")
    groups = gl.groups.list(search=group_path)
    for group in groups:
        if group.full_path == group_path:
            return group.id
    raise ValueError("group id not found")


def get_gitlab_project_id_from_full_path(glgroup, project_path: str) -> int:
    print("searching for project id by full path")
    glprojects = glgroup.projects.list(search=project_path)
    for glproject in glprojects:
        if glproject.path == project_path:
            return glproject.id
    raise ValueError("project id not found")


def get_gitlab_group_id(gl: gitlab.Gitlab, args) -> int | None:
    if args.group_path:
        return get_gitlab_group_id_from_full_path(gl, args.group_path)
    return args.group_id


def get_gitlab_project_id(gl: gitlab.Gitlab, args) -> int | None:
    if args.project_path:
        return get_gitlab_project_id_from_full_path(gl, args.project_path)
    return args.project_id


def add_command(args):
    gl = gitlab.Gitlab()

    group_id = None
    project_id = None

    if args.group_path:
        group_id = get_gitlab_group_id_from_full_path(gl, args.group_path)
    elif args.group_id:
        group_id = args.group_id
    elif args.project_path:
        project_path = Path(args.project_path)
        group_path = str(project_path.parent)
        group_id = get_gitlab_group_id_from_full_path(gl, group_path)
        glgroup = gl.groups.get(group_id)
        project_id = get_gitlab_project_id_from_full_path(
            glgroup, str(project_path.name)
        )
        group_id = None
    elif args.project_id:
        project_id = args.project_id

    if group_id and project_id:
        raise ValueError("found both group id and project id")

    if group_id:
        print("found group id:", group_id)
    elif project_id:
        print("found project id:", project_id)

    if group_id:
        glgroup = gl.groups.get(id=group_id)
        glprojects = glgroup.projects.list(
            archived=False,
            visibility="public",
            include_subgroups=True,
            order_by="name",
            sort="asc",
            limit=3,
            all=True,
        )
    elif project_id:
        glprojects = [gl.projects.get(id=project_id)]

    projects = {}

    for glproject in glprojects:
        project_path = Path(glproject.path_with_namespace)
        projects[glproject.id] = PullyProject(
            path=str(project_path),
        )
        sync_project(glproject, project_path)

    config = pullyfile.PullyFile(projects=projects)

    with open(BASE_DIR / ".pully.json", "wb") as handle:
        handle.write(pullyfile.dumps(config))


def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument("-C", "--directory", type=str)

    subparsers = parser.add_subparsers(required=True)

    add_parser = subparsers.add_parser("add")
    add_parser.set_defaults(func=add_command)

    id_group = add_parser.add_mutually_exclusive_group(required=True)
    id_group.add_argument("-g", "--group-id", type=int)
    id_group.add_argument("-G", "--group-path", type=str)
    id_group.add_argument("-p", "--project-id", type=int)
    id_group.add_argument("-P", "--project-path", type=str)

    args = parser.parse_args()
    args.func(args)
