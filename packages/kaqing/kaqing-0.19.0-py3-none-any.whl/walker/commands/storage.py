from walker.checks.check_result import CheckResult
from walker.checks.check_utils import run_checks, run_checks_on_pod
from walker.checks.compactionstats import CompactionStats
from walker.checks.disk import Disk
from walker.commands.command import Command
from walker.commands.issues import Issues
from walker.config import Config
from walker.repl_state import ReplState
from walker.k8s_utils import list_pods
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

        checks = [Disk(), CompactionStats()]
        if state.pod:
            results = run_checks_on_pod(cluster=state.statefulset, pod=state.pod, namespace=state.namespace, checks=checks, show_output=show_output)
            self.show_pods([state.pod], state.namespace, [results])

            log()
            keyspaces = []
            for keyspace in results.details[Disk().name()]['keyspaces']:
                size = int(float(keyspace['size']) / 1024.)
                keyspaces.append(f"{keyspace['name']},{keyspace['path']},{size}M")
            log(lines_to_tabular(keyspaces, 'KEYSPACE,PATH,SIZE', separator=','))
        elif state.statefulset:
            pod_names = [pod.metadata.name for pod in list_pods(state.statefulset, state.namespace)]
            results = run_checks(cluster=state.statefulset, namespace=state.namespace, checks=','.join([c.name() for c in checks]), show_output=show_output)
            self.show_pods(pod_names, state.namespace, results)

        return state

    def show_pods(self, pods: list[str], ns: str, results: list[CheckResult]):
        if len(pods) == 0:
            log2('No pods found.')
            return

        r_by_pod = {}
        for r in results:
            key = r.details[Disk().name()]['name']
            if not key:
                key = r.details[CompactionStats().name()]['name']

            r_by_pod[key] = r

        def line(pod_name: str):
            l = f"{pod_name}@{ns},Unknown,Unknown,Unknown,Unknown"
            if pod_name in r_by_pod:
                r = r_by_pod[pod_name]
                dd = r.details[Disk().name()]
                fr = f"{dd['devices']['/']['per']}({dd['devices']['/']['used']}/{dd['devices']['/']['total']})"
                cass_data_path = Config().get('checks.cassandra-data-path', '/c3/cassandra')
                fc = f"{dd['devices'][cass_data_path]['per']}({dd['devices'][cass_data_path]['used']}/{dd['devices'][cass_data_path]['total']})"

                cd = r.details[CompactionStats().name()]

                l = f"{pod_name}@{ns},{fr},{fc},{dd['snapshot']}G,{dd['data']['size']},{cd['compactions']}"

            return l

        lines = [line(pod) for pod in pods]
        lines.sort()

        log(lines_to_tabular(lines, f'POD_NAME,/,CASS,SNAPSHOTS,DATA,COMPACTIONS', separator=','))
        issues = CheckResult.issues(results)
        Issues.show_issues(issues)

    def completion(self, state: ReplState):
        if not state.statefulset:
            return {}

        return {Storage.COMMAND: None}

    def help(self, _: ReplState):
        return f'{Storage.COMMAND}: storage overview'