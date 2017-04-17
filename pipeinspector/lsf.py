import subprocess

class BsubOption(object):
    def __init__(self, key, option_flag):
        self.key = key
        self.option_flag = option_flag

    def __call__(self, option_dict):
        if self.key in option_dict:
            return [self.option_flag, option_dict[self.key]]

class BsubEmailOption(BsubOption):
    def __call__(self, option_dict):
        return ['-N'] + super(BsubEmailOption, self).__call__(option_dict)

class BsubMemoryOption(BsubOption):
    def __init__(self):
        super(BsubMemoryOption, self).__init__('memory_in_gb', None)

    def __call__(self, option_dict):
        if self.key in option_dict:
            resource_string = '\"select[mem>{memory}000] rusage[mem={memory}000]\"'.format(memory=option_dict[self.key])
            memlimit = '{memory}000000'.format(memory=option_dict[self.key])
            return ['-M', memlimit, '-R', resource_string]

class BsubDockerOption(BsubOption):
    def __init__(self):
        super(BsubDockerOption, self).__init__('docker', '-a')
    def __call__(self, option_dict):
        if self.key in option_dict:
            docker_string = 'docker({registry})'.format(registry=option_dict[self.key])
            return [self.option_flag, docker_string]

class LsfJob(object):
    available_options = (
            BsubOption('queue', '-q'),
            BsubOption('threads', '-n'),
            BsubMemoryOption(),
            BsubDockerOption(),
            BsubOption('job_name', '-J'),
            BsubOption('stdout', '-oo'),
            BsubOption('stderr', '-eo'),
            BsubEmailOption('email', '-u'),
            BsubOption('group', '-g'),
            )

    def __init__(self, options):
        self.bsub_options = ['bsub']
        self.created_options = options

    def _construct_bsub(self, override_options):
        options = self.created_options.copy()
        options.update(override_options)
        return self.bsub_options + reduce(
                lambda x, y: x + y,
                filter(lambda x: x is not None,
                    [ x(options) for x in LsfJob.available_options ]
                    )
                )

    def _construct_cmd(self, cmd, cmd_options):
        return self._construct_bsub(cmd_options) + [cmd]

    def bsub_cmd(self, cmd, cmd_options):
        return ' '.join(self._construct_cmd(cmd, cmd_options))

    def dry_run(self, cmd, cmd_options):
        return self.bsub_cmd(cmd, cmd_options)

    def launch(self, cmd, cmd_options):
        print self._construct_cmd(cmd, cmd_options)
        proc = subprocess.call(self._construct_cmd(cmd, cmd_options))

