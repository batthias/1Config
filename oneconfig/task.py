"""Run tasks for a project."""
import os
import sys
from subprocess import call


class Task(object):
    def __init__(self, name: str, content: dict):
        raise NotImplementedError()

    def run(self):
        """Runs the task."""
        assert self.name
        if self.shell:
            call()
        elif self.

    def __repr__(self):
        return f'<Task({name!r})>'




def run(*command_line_args):
    arg_parser = argparse.ArgumentParser(
        description='Run a task of the Mobius Vision SDK project',
        epilog='Available Tasks: ' + '\n'.join(
            f"{name}: {task['description']}" for name, task in self.available_tasks.items())
        )
    arg_parser.add_argument('taskname', help='Name of the task to be run', nargs=1)
    args = arg_parser.parse_args(command_line_args)

    try:
        task = TASKS[args.taskname[0]]
    except KeyError:
        sys.stderr.write(f'Task "{args.taskname[0]}" not supported by `manage.py`.')
    else:
        run_task(task)


if __name__ == '__main__':
    run(sys.argv)