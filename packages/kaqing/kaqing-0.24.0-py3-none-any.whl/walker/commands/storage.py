from walker.checks.check_utils import run_checks
from walker.columns.columns import Columns, collect_checks
from walker.commands.command import Command
from walker.commands.issues import Issues
from walker.config import Config
from walker.repl_state import ReplState
from walker.k8s_utils import list_pods
from walker.utils import lines_to_tabular, log

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
            self.show_table(state, [state.pod], state.namespace, show_output=show_output)
        elif state.statefulset:
            pod_names = [pod.metadata.name for pod in list_pods(state.statefulset, state.namespace)]
            self.show_table(state, pod_names, state.namespace, show_output=show_output)

        return state

    def show_table(self, state: ReplState, pods: list[str], ns: str, show_output=False):
        cols = Config().get('storage.columns', 'pod,volume_root,volume_cassandra,snapshots,data,compactions')
        header = Config().get('storage.header', 'POD_NAME,VOLUME /,VOLUME CASS,SNAPSHOTS,DATA,COMPACTIONS')
        columns = Columns.create_columns(cols)

        results = run_checks(cluster=state.statefulset, pod=state.pod, namespace=state.namespace, checks=collect_checks(columns), show_output=show_output)

        def line(pod_name: str):
            cells = [c.pod_value(results, pod_name) for c in columns]
            return ','.join(cells)

        lines = [line(pod) for pod in pods]
        lines.sort()

        log(lines_to_tabular(lines, header, separator=','))

        Issues.show(results)

    def completion(self, state: ReplState):
        if not state.statefulset:
            return {}

        return {Storage.COMMAND: None}

    def help(self, _: ReplState):
        return f'{Storage.COMMAND}: storage overview'