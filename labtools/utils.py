import pkg_resources as pkgrs
import os
import subprocess

def run(*args):
    return subprocess.check_call(['git'] + list(args))

def git_branch(name):
    run("checkout", "-b", br)


def load_template_file(md_template_file):
    '''
    load a template file from the package's template dir
    '''
    md_template_path_rel = os.path.join('templates',md_template_file)
    md_template_path = pkgrs.resource_filename(__name__,md_template_path_rel)
    with open (md_template_path,'r') as tmpt_f:
        md_template = tmpt_f.read()

    return md_template
