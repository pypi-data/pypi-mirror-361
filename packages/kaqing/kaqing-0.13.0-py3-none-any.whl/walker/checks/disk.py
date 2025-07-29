import re
from walker.checks.check import Check
from walker.checks.check_context import CheckContext
from walker.checks.check_result import CheckResult
from walker.checks.issue import Issue
from walker.config import Config
from walker.k8s_utils import cassandra_pod_exec

class Disk(Check):
    def name(self):
        return 'disk'

    def check(self, ctx: CheckContext) -> CheckResult:
        issues: list[Issue] = []

        try:
            cass_data_path = Config().get('checks.cassandra-data-path', 'c3/cassandra')
            df_result = cassandra_pod_exec(ctx.pod, ctx.namespace, f"df -h | grep -e '{cass_data_path}' -e 'overlay'", show_out=ctx.show_output)
            snapshot_size = Config().get('checks.snapshot-size-cmd', "ls /c3/cassandra/data/data/*/*/snapshots | grep snapshots | sed 's/:$//g' | xargs -I {} du -sk {} | awk '{print $1}' | awk '{s+=$1} END {print s}'")
            ss_result = cassandra_pod_exec(ctx.pod, ctx.namespace, snapshot_size, show_out=ctx.show_output)
            result = self.build_details(ctx, df_result.stdout, ss_result.stdout)
            # TODO how's disk space issues defined?
            dev = result['devices']['/']
            root_used = float(dev['per'].strip('%'))
            if root_used > Config().get('checks.root-disk-threshold', 50):
                usage = f"{dev['per']}({dev['used']}/{dev['total']})"
                issues.append(Issue(
                    statefulset=ctx.statefulset,
                    namespace=ctx.namespace,
                    pod=ctx.pod,
                    category="disk",
                    desc=f"Root data disk is full: {usage}"
                ))
            dev = result['devices'][f'/{cass_data_path}']
            cass_used = float(dev['per'].strip('%'))
            if cass_used > Config().get('checks.cassandra-disk-threshold', 50):
                usage = f"{dev['per']}({dev['used']}/{dev['total']})"
                issues.append(Issue(
                    statefulset=ctx.statefulset,
                    namespace=ctx.namespace,
                    pod=ctx.pod,
                    category="disk",
                    desc=f"Cassandra data disk is full: {usage}"
                ))
        except Exception as e:
            print('SEAN', e)
            issues.append(self.issue_from_err(statefulset_name=ctx.statefulset, ns=ctx.namespace, pod_name=ctx.pod, exception=e))

        return CheckResult(self.name(), result, issues)

    def build_details(self, ctx: CheckContext, df_out: str, ss_out: str):
        # overlay                 499.9G     52.4G    447.5G  10% /
        # /dev/nvme2n1           1006.9G      2.6G   1004.2G   0% /c3/cassandra
        devices = {}
        for l in df_out.split('\n'):
            l = l.strip('\r')
            groups = re.match(r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$', l)
            if groups:
                dev = Disk.clean(groups[1])
                total = Disk.clean(groups[2])
                used = Disk.clean(groups[3])
                free = Disk.clean(groups[4])
                per = Disk.clean(groups[5])
                path = Disk.clean(groups[6])
                device = {'dev': dev, 'total': total, 'used': used, 'free': free, 'per': per, 'path': path}
                devices[path] = device

        return {
                'name': ctx.pod,
                'namespace': ctx.namespace,
                'statefulset': ctx.statefulset,
                'snapshot': round(float(ss_out.strip(' \r\n')) / 1024 / 1024, 2),
                'devices': devices}

    def clean(s: str):
        return re.sub(r'[^a-zA-Z0-9/%]', '', s)
