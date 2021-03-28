'''
This module generates md files for lab news
'''
import click
import yaml as yml
from .utils import load_template_file


@click.command()
@click.argument('name', default=None)
@click.option('--role', default='researcher', help='role in the lab')



def new_member(name, role):
    '''
    create a markdown file for a new lab member


    '''

    # load the template
    md_template = load_template_file('people.md')

    # put the info into a dicationary for the template
    data_dict = {'name':name,
                'role':role}

    # merge data with the template
    md_out = md_template.format_map(data_dict)

    # write to file
    name_lower = '_'.join(name.lower().split())
    filename = '_people/' + name_lower + '.md'


    with open(filename,'w') as md_f:
        md_f.write(md_out)
    return None



if __name__ == '__main__':
    new_member()
