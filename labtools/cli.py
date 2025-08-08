import click
import os
import json 
from .utils import load_template_file

from .labnews import create_new_lab_news
from .accountability import get_date_range
from .accountability import issues_to_checklist

@click.group()
def lab():
    '''
    Lab tools for managing lab news
    '''
    pass

@lab.group()
def acc():
    '''
    tools for managing lab accountability
    '''
    pass

@acc.command()
@click.argument('path', default='.')
def init(path):
    '''
    Initialize a lab accountability repo, at PATH (default current dir)
    '''
    # write the scheduleer.yml to .github/workflows
    os.makedirs(os.path.join(path,'.github','workflows'),exist_ok=True)
    # write the template for issues to .github/ISSUE_TEMPLATE
    os.makedirs(os.path.join(path,'.github','ISSUE_TEMPLATE'),exist_ok=True)
    
      
    scheduler_action = load_template_file('scheduler.yml')
    # write the scheduler action to .github/workflows/scheduler.yml
    out_path = os.path.join(path,'.github','workflows','scheduler.yml')
    
    with open(out_path,'w') as f:
        f.write(scheduler_action) 

    git_ignore = load_template_file('gitignore.txt')
    with open(os.path.join(path,'.gitignore'),'w') as f:
        f.write(git_ignore) 

    




@acc.command()

def log():
    '''
    Create the content for a lab accountability entry interactively
    '''
    # prompt for entry info, open editor, save entry, git add and commit


@acc.command()
@click.option('-d','--reference-date', default=None,
              help='reference date for date range (ISO format|YYYY-MM-DD) otherwise today')
def dates(reference_date=None):
    '''
    get date range for accountability entry
    '''
    date_range = get_date_range(reference_date)
    click.echo(date_range)

@acc.command()
@click.argument('file', default=None,)
def checklist(file):
    '''
    create a markdown checklist of issues to address in accountability entry
    '''
    # load json from buffer in file or stdin
    with open(file,'r') as f:
        issues_json_dict = json.load(f)
    checklist = issues_to_checklist(issues_json_dict)
    click.echo(checklist)

@acc.command()
@click.option('-c','--closed-issues-json', default='closed_issues.json',
              type =click.File('r'))
@click.option('-o','--open-issues-json', default='open_issues.json',
              type =click.File('r'))
def create(closed_issues_json,open_issues_json):
    '''
    create a markdown file for a lab accountability entry
    '''
    # create the markdown file from template filled with checklists

    
    closed_issues = json.load(closed_issues_json)
    closed_checklist = issues_to_checklist(closed_issues,open=False)

    
    open_issues = json.load(open_issues_json)
    open_checklist = issues_to_checklist(open_issues)

    # load the template from package
    md_template = load_template_file('accountability_issue.md')

    md_issue = md_template.format_map({'closed_checklist':closed_checklist,
                                     'open_checklist':open_checklist})
    click.echo(md_issue)


@acc.command()
@click.option('--name', prompt='your name',)
@click.option('--username', prompt='your github username',)
@click.option('-d','--day-of-week', prompt='day of week to run (0=Mon, 6=Sun)',type=int)
def schedule(username,name,day_of_week):
    '''
    create the action to schedule acc issues
    '''
    secret_required = '{{ secrets.GITHUB_TOKEN }}'
    template = load_template_file('create_acc_issue.yml')

    action = template.format_map({'secret_required':secret_required,
                                  'username':username, 'name':name, 
                                  'day_of_week':day_of_week})
    with open(f'.github/workflows/scheduled_acc_{username}.yml','w') as f:
        f.write(action)
    

@lab.group()
def site():
    '''
    Site tools for managing lab website content
    '''
    pass

@site.command()
@click.argument('slug', default=None)
@click.option('--date', default='now', help='date of post')
@click.option('--title', prompt='News title',
              help='one line to display as headline of news post', default=None)
@click.option('--inline', default='false')

def news(slug, date, title, inline):
    '''
    create a markdown file for a lab news item


    '''
    create_new_lab_news(slug, date, title, inline)

