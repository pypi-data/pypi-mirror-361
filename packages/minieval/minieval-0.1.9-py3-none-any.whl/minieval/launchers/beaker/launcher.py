import os
import re
import secrets
import string
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import beaker as bk
from gantry.api import launch_experiment
from rich.console import Console

from minieval.cli import apply_overrides
from minieval.datatypes import LauncherConfig
from minieval.launchers.beaker.constants import WEKA_CLUSTERS
from minieval.launchers.beaker.defaults import get_env_vars

console = Console()


@dataclass
class BeakerConfig(LauncherConfig):
    workspace: str
    cluster: List[str]
    budget: str

    # Optional args
    hostname: Optional[List[str]] = None  # specific nodes to run a job
    max_retries: int = 0
    gpus: int = 0
    num_nodes: int = 1
    image: str = "ai2/cuda12.8-dev-ubuntu22.04-torch2.7.0"
    description: str = "davidh training job"
    task_name: str = "davidh_task"
    priority: str = "normal"
    preemptible: bool = True
    pure_docker_mode: bool = True  # If false, will cd into os.getcwd()
    beaker_datasets: List[Dict[str, str]] = field(
        default_factory=list
    )  # TODO: Add parser from mason.py
    env: List[Dict[str, str]] = field(default_factory=list)  # TODO: Add parser from mason.py
    secret: List[Dict[str, str]] = field(default_factory=list)  # TODO: Add parser from mason.py
    no_host_networking: bool = False
    follow: bool = False


def gen_uuid(length: int = 8) -> str:
    """Random base-36 string of `length` digits."""
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def make_command(cmd: List[str], config: BeakerConfig) -> str:
    # escape the command (e.g., --stop_strings "</answer>")
    for i in range(len(cmd)):
        if "</" in cmd[i]:
            cmd[i] = f"'{cmd[i]}'"

    # special logic to deal with escape like
    # python mason.py ... -- python x.py --dataset_mixer '{"trl-internal-testing/sentiment-trl-style": 1.0}'
    # we need to wrap the json string with single quote
    for idx in range(len(cmd)):
        if "{" in cmd[idx]:
            cmd[idx] = "'" + cmd[idx] + "'"

    setup_cmd = ""
    if not config.pure_docker_mode:
        setup_cmd = f"cd {os.getcwd()} && "

    # override accelerate call
    join_cmd = " ".join(cmd)
    if config.num_nodes > 1:
        if "--num_processes" not in join_cmd and "accelerate" in join_cmd:
            raise ValueError(
                "num_processes must be specified in the command for accelerate-based multi-node jobs."
            )
        join_cmd = re.sub(
            r"--num_processes (\d+)",
            lambda m: (
                f"--num_processes {int(m.group(1)) * config.num_nodes} "
                f"--num_machines {config.num_nodes} "
                "--machine_rank $BEAKER_REPLICA_RANK "
                "--main_process_ip $BEAKER_LEADER_REPLICA_HOSTNAME "
                "--main_process_port 29400 "
            ),
            join_cmd,
        )

    cmd = setup_cmd + join_cmd

    return cmd


def parse_commands() -> List[List[str]]:
    """
    Parse commands separated by '--' into list of command lists.

    E.g.:    launch.py [options] -- cmd1 arg1 -- cmd2 arg2
    Returns: [["cmd1", "arg1"], ["cmd2", "arg2"]]
    """
    if len(sys.argv) < 2:
        raise ValueError("No command provided. Usage: launch.py [options] -- command")

    try:
        first_cmd_idx = sys.argv.index("--")
    except ValueError:
        raise ValueError("No command separator '--' found. Usage: launch.py [options] -- command")

    # Get everything after first --
    remaining_args = sys.argv[first_cmd_idx + 1 :]

    if not remaining_args:
        raise ValueError("No command provided after '--'")

    # Split into separate commands on --
    commands = []
    current_cmd = []

    for arg in remaining_args:
        if arg == "--":
            if current_cmd:
                commands.append(current_cmd)
                current_cmd = []
        else:
            current_cmd.append(arg)

    if current_cmd:
        commands.append(current_cmd)

    if not commands:
        raise ValueError("No valid commands found")

    return commands


def launch_gantry(config: BeakerConfig):
    global_wandb_id = gen_uuid()

    beaker_client = bk.Beaker.from_env(default_workspace=config.workspace)

    beaker_secrets = [
        secret.name for secret in beaker_client.secret.list(workspace=config.workspace)
    ]
    whoami = beaker_client.user_name

    commands = parse_commands()

    full_commands = []
    for command in commands:
        full_commands += [make_command(command, config)]

    assert len(full_commands) == 1, "only one command supported for now"
    full_commands = full_commands[0]

    env_vars, env_secrets = get_env_vars(
        config.cluster,
        beaker_secrets,
        whoami,
        global_wandb_id,
        config.pure_docker_mode,
        config.num_nodes,
        config.env,
        config.secret,
        config.preemptible,
    )
    env_vars = [f"{var.name}={var.value}" for var in env_vars]
    env_secrets = [f"{var.name}={var.secret}" for var in env_secrets]

    # TODO: Move this to constants
    weka = [
        "oe-adapt-default:/oe-adapt-default",
        "oe-training-default:/oe-training-default",
        "oe-eval-default:/oe-eval-default",
    ]

    # TODO: put this somewhere better
    UV_INIT = "deactivate && pip install uv && uv venv && source .venv/bin/activate && "
    UV_DEPS = "uv pip install torch && sudo apt install -y libmpich-dev && "

    # Launch the experiment
    launch_experiment(  # launch_experiment()
        args=full_commands.split(" "),
        workspace=config.workspace,
        clusters=config.cluster,
        budget=config.budget,
        # datasets= # TODO: add ability to add this
        name=config.task_name,
        description=config.description,
        hostnames=config.hostname,
        beaker_image=config.image,
        gpus=config.gpus,
        preemptible=config.preemptible,
        retries=config.max_retries,
        # mounts=mounts, # need to fix
        replicas=config.num_nodes,
        host_networking=not config.no_host_networking,
        env_vars=env_vars,
        env_secrets=env_secrets,
        yes=True,
        # new stuff
        allow_dirty=True,
        priority=config.priority,
        # dry_run=False,
        weka=weka,
        timeout=(
            99999999 if config.follow else 0
        ),  # only way to follow the experiment without canceling
        # install="pip install -e '.[all]'",
        install=UV_INIT
        + UV_DEPS
        + "uv pip install -e '.[all]'",  # Workaournd as Gantry doesn't support uv
    )


def main():
    config = apply_overrides(
        BeakerConfig(workspace="ai2/davidh", cluster=WEKA_CLUSTERS, budget="ai2/oe-eval", gpus=1)
    )
    launch_gantry(config)


if __name__ == "__main__":
    main()
