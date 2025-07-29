from kubernetes import client
from typing import List

from walker.checks.check_context import CheckContext
from walker.checks.check_result import CheckResult
from walker.checks.check_utils import run_checks
from walker.checks.compactionstats import CompactionStats
from walker.checks.disk import Disk
from walker.commands.command import Command
from walker.repl_state import ReplState
from walker.k8s_utils import get_app_ids, get_cr_name, list_pods, list_statefulset_names, get_host_id
from walker.utils import lines_to_tabular, log, log2

class Storage(Command):
    COMMAND = 'storage'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Storage, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Storage.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        args, show_output = Command.extract_options(args, ['-s', '--show'])

        if state.pod:
            pass
        elif state.statefulset:
            pods = list_pods(state.statefulset, state.namespace)
            results = run_checks(cluster=state.statefulset, namespace=state.namespace, checks=f'{Disk().name()},{CompactionStats().name()}', show_output=show_output)
            self.show_pods(pods, state.namespace, results, show_output=show_output)

        return state

    def show_pods(self, pods: List[client.V1Pod], ns: str, results: list[CheckResult], show_output = False):
        if len(pods) == 0:
            log2('No pods found.')
            return

        r_by_pod = {}
        for r in results:
            key = r.details[Disk().name()]['name']
            if not key:
                key = r.details[CompactionStats().name()]['name']

            r_by_pod[key] = r

        def line(pod: client.V1Pod):
            key = pod.metadata.name
            l = f"{key}@{ns},Unknown,Unknown,Unknown,Unknown"
            if key in r_by_pod:
                r = r_by_pod[key]
                dd = r.details[Disk().name()]
                fr = f"{dd['devices']['/']['per']}({dd['devices']['/']['used']})"
                fc = f"{dd['devices']['/c3/cassandra']['per']}({dd['devices']['/c3/cassandra']['used']})"

                cd = r.details[CompactionStats().name()]

                l = f"{key}@{ns},{fr},{fc},{dd['snapshot']}G,{cd['compactions']}"

            return l

        lines = [line(pod) for pod in pods]
        lines.sort()

        log(lines_to_tabular(lines, 'POD_NAME,/,CASS,SNAPSHOT,COMPACTIONS', separator=','))

    def completion(self, state: ReplState):
        if state.pod:
            return {Storage.COMMAND: None}

        # if not state.statefulset:
        #     return {Storage.COMMAND: {n: None for n in list_statefulset_names()}}

        return {Storage.COMMAND: None}

    def help(self, _: ReplState):
        return f'{Storage.COMMAND}: storage overview'