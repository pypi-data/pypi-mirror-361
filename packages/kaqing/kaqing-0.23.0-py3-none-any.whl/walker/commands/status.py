import sys

from walker.checks.check_result import CheckResult
from walker.checks.check_utils import run_checks
from walker.checks.compactionstats import CompactionStats
from walker.checks.gossip import Gossip
from walker.commands.command import Command
from walker.commands.issues import Issues
from walker.config import Config
from walker.repl_state import ReplState, RequiredState
from walker.k8s_utils import get_user_pass, cassandra_pod_exec, pod_names
from walker.utils import lines_to_tabular, log, log2
from walker.checks.status import parse_nodetool_status

class Status(Command):
    COMMAND = 'status'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Status, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Status.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        args, show_output = Command.extract_options(args, ['-s', '--show'])

        if state.namespace and state.pod:
            self.show_single_pod(state.statefulset, state.pod, state.namespace, show_output=show_output)
        elif state.namespace and state.statefulset:
            self.merge(state.statefulset, pod_names(state.statefulset, state.namespace), state.namespace, Config().get('nodetool.samples', sys.maxsize), show_output=show_output)

        return state

    def show_single_pod(self, statefulset: str, pod_name: str, ns: str, show_output = False):
        pod_name = pod_name.split('(')[0]
        user, pw = get_user_pass(pod_name, ns)
        try:
            result = cassandra_pod_exec(pod_name, ns, f"nodetool -u {user} -pw {pw} status", show_out=False)
            status = parse_nodetool_status(result.stdout)
            check_results = run_checks(cluster=statefulset, namespace=ns, checks=[CompactionStats(), Gossip()], show_output=show_output)
            self.show(status, check_results)
        except Exception as e:
            log2(e)

    def merge(self, statefulset: str, pod_names: list[str], ns: str, samples: int, show_output=False):
        statuses: list[list[dict]] = []
        for pod_name in pod_names:
            pod_name = pod_name.split('(')[0]
            user, pw = get_user_pass(pod_name, ns)

            try:
                result = cassandra_pod_exec(pod_name, ns, f"nodetool -u {user} -pw {pw} status", show_out=False)
                status = parse_nodetool_status(result.stdout)
                if status:
                    statuses.append(status)
                if samples <= len(statuses) and len(pod_names) != len(statuses):
                    break
            except Exception as e:
                log2(e)

        combined_status = self.merge_status(statuses)
        log2(f'Showing merged status from {len(statuses)}/{len(pod_names)} nodes...')
        check_results = run_checks(cluster=statefulset, namespace=ns, checks=[CompactionStats(), Gossip()], show_output=show_output)
        self.show(combined_status, check_results)

        return combined_status

    def merge_status(self, statuses: list[list[dict]]):
        combined = statuses[0]

        status_by_host = {}
        for status in statuses[0]:
            status_by_host[status['host_id']] = status
        for status in statuses[1:]:
            for s in status:
                if s['host_id'] in status_by_host:
                    c = status_by_host[s['host_id']]
                    if c['status'] == 'UN' and s['status'] == 'DN':
                        c['status'] = 'DN*'
                else:
                    combined.append(s)

        return combined

    def merge_gossip(self, check_results: list[CheckResult]):
        hosts_with_gossip_issue = set()

        for r in check_results:
            for issue in r.issues:
                if issue.category == 'gossip':
                    hosts_with_gossip_issue.add(issue.host['value'])

        return hosts_with_gossip_issue

    def merge_compactions(self, check_results: list[CheckResult]):
        compactions_by_host = {}
        for cr in check_results:
            host = cr.details['compactionstats']['host_id']
            c = cr.details['compactionstats']['compactions']
            compactions_by_host[host] = c

        return compactions_by_host

    def show(self, status: list[dict[str, any]], check_results: list[CheckResult]):
        compactions_by_host = self.merge_compactions(check_results)
        hosts_with_gossip_issue = self.merge_gossip(check_results)

        columns = Config().get('status.columns', 'status,address,load,tokens,owns,host_id,gossip,compactions').split(',')
        header = Config().get('status.header', '--,Address,Load,Tokens,Owns,Host ID,GOSSIP,COMPACTIONS')
        def line(s: dict[str, any]):
            host = s['host_id']

            values = []
            for column in columns:
                if column == 'gossip':
                    values.append('DOWN' if host in hosts_with_gossip_issue else 'UP')
                elif column == 'compactions':
                    values.append(compactions_by_host[host])
                else:
                    values.append(s[column])

            return ','.join(values)

        log(lines_to_tabular([line(d) for d in status], header, separator=','))

        Issues.show(check_results)

    def completion(self, state: ReplState):
        if not state.pod and state.statefulset:
            return {Status.COMMAND: None}

        return {}

    def help(self, _: ReplState):
        return f'{Status.COMMAND}: show nodetool status merged from all nodes'