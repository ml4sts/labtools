import pkg_resources as pkgrs
import os
import subprocess

def run(*args):
    return subprocess.check_call(['git'] + list(args))

def git_branch(name):
    run("checkout", "-b", br)


def load_template_file(template_file):
    '''
    load a template file from the package's template dir
    '''
    template_path_rel = os.path.join('templates', template_file)
    template_path = pkgrs.resource_filename(__name__, template_path_rel)
    with open(template_path, 'r') as tmpt_f:
        template = tmpt_f.read()

    return template
