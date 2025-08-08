import os
import subprocess
from importlib.resources import files

def run(*args):
    return subprocess.check_call(['git'] + list(args))

def git_branch(name):
    run("checkout", "-b", name)


def load_template_file(template_file):
    '''
    load a template file from the package's template dir
    '''
    template_path = os.path.join(files(__package__), 'templates', template_file)
    with open(template_path,'r') as tmpt_f:
        template = tmpt_f.read()

    return template
