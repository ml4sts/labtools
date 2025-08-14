import os
import subprocess
from importlib.resources import files

def run(*args):
    return subprocess.check_call(['git'] + list(args))

def git_branch(name):
    run("checkout", "-b", name)

TEMPLATE_MARKER = '# TEMPLATE NOTE:'

def load_template_file(template_file):
    '''
    load a template file from the package's template dir
    '''
    template_path = os.path.join(files(__package__), 'templates', template_file)
    with open(template_path,'r') as tmpt_f:
        template_raw = tmpt_f.readlines()

    template_lines = [ln for ln in template_raw if not ln.startswith(TEMPLATE_MARKER)]
    template = ''.join(template_lines) 

    return template
