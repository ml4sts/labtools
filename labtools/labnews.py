'''
This module generates md files for lab news
'''
import os
import pkg_resources as pkgrs
from datetime import datetime
from .utils import load_template_file


template_dir = 'templates'
md_template_file = 'labnews.md'


def create_new_lab_news(slug=None, date='now', title=None, inline='false'):
    '''
    Create a markdown file for a lab news item
    '''
    # set date to now if not provided
    if date == 'now':
        date = datetime.now().isoformat(sep=' ')

    if title is None:
        title= slug

    # load the template
    md_template = load_template_file('labnews.md')


    # put the info into a dicationary for the template
    data_dict = {'date':date,
                'title':title,
                'inline':inline}

    # merge data with the template
    md_out = md_template.format_map(data_dict)

    # write to file
    print(data_dict)
    filename = '_news/' + date.split(' ')[0] + '-' + slug + '.md'
    print(filename)


    with open(filename,'w') as md_f:
        md_f.write(md_out)
    return None



if __name__ == '__main__':
    new_lab_news()
