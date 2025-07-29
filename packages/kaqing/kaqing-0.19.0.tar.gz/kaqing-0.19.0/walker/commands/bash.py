from walker.commands.command import Command
from walker.repl_state import ReplState, RequiredState
from walker.k8s_utils import cassandra_nodes_exec, cassandra_pod_exec

class Bash(Command):
    COMMAND = 'bash'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Bash, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Bash.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, s0: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, s0)

        state, args = self.apply_state(args, s0)
        if not self.validate_state(state):
            return state

        if not len(args):
            s0.enter_bash()

            return state

        a = ' '.join(args)
        command = f'bash -c "{a}"'

        if state.pod:
            return cassandra_pod_exec(state.pod, state.namespace, command)
        elif state.statefulset:
            return cassandra_nodes_exec(state.statefulset, state.namespace, command, 'bash')

    def completion(self, state: ReplState):
        if state.pod or state.statefulset:
            return {Bash.COMMAND: None}

        return {}

    def help(self, _: ReplState):
        return f'{Bash.COMMAND}: run bash'