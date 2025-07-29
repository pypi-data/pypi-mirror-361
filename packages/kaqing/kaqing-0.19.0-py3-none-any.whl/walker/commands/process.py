from kubernetes.utils import parse_quantity

from walker.checks.check_result import CheckResult
from walker.checks.check_utils import run_checks, run_checks_on_pod
from walker.checks.cpu import Cpu
from walker.checks.memory import Memory
from walker.commands.command import Command
from walker.commands.issues import Issues
from walker.repl_state import ReplState
from walker.k8s_utils import list_pods
from walker.utils import lines_to_tabular, log, log2

class Process(Command):
    COMMAND = 'process'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Process, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Process.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        args, show_output = Command.extract_options(args, ['-s', '--show'])

        checks = [Cpu(), Memory()]
        if state.pod:
            results = run_checks_on_pod(cluster=state.statefulset, pod=state.pod, namespace=state.namespace, checks=checks, show_output=show_output)
            self.show_pods([state.pod], state.namespace, [results])
        elif state.statefulset:
            pod_names = [pod.metadata.name for pod in list_pods(state.statefulset, state.namespace)]
            results = run_checks(cluster=state.statefulset, namespace=state.namespace, checks=','.join([c.name() for c in checks]), show_output=show_output)
            self.show_pods(pod_names, state.namespace, results)

        return state

    def show_pods(self, pods: list[str], ns: str, results: list[CheckResult]):
        if len(pods) == 0:
            log2('No pods found.')
            return

        r_by_pod: dict[str, CheckResult] = {}
        for r in results:
            key = r.details[Cpu().name()]['name']
            if not key:
                key = r.details[Memory().name()]['name']

            r_by_pod[key] = r

        def line(pod_name: str):
            l = f"{pod_name}@{ns},Unknown,Unknown,Unknown,Unknown"
            if pod_name in r_by_pod:
                r = r_by_pod[pod_name]
                cpu = r.details[Cpu().name()]
                mem = r.details[Memory().name()]

                busy = 100.0 - float(cpu['idle'])
                l = f"{pod_name}@{ns},{round(busy)}%({round(parse_quantity(cpu['cpu']), 2)}),{to_g(mem['used'])}/{to_g(mem['limit'])}"

            return l

        def to_g(v: str):
            try:
                return f'{round(parse_quantity(v) / 1024 / 1024 / 1024, 2)}G'
            except:
                return v

        lines = [line(pod) for pod in pods]
        lines.sort()

        log(lines_to_tabular(lines, f'POD_NAME,CPU,MEM/LIMIT', separator=','))
        issues = CheckResult.issues(results)
        Issues.show_issues(issues)

    def completion(self, state: ReplState):
        if not state.statefulset:
            return {}

        return {Process.COMMAND: None}

    def help(self, _: ReplState):
        return f'{Process.COMMAND}: storage overview'