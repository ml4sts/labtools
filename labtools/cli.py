'''
This should be the CLI as minimal as possible; most functionality should be in 
the other modules.
'''

import click
import os
import json 
from .utils import load_template_file

from .labnews import create_new_lab_news
from .accountability import get_date_range, parse_template, generate_schedule_action
from .accountability import issues_to_checklist, generate_basic_acc_issue
from .accountability import file_generator, load_and_fill_template
from .accountability import initialize_accountability_repo, file_split

from .articles import create_github_paper_issue

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
    progress  = initialize_accountability_repo(path)
    click.echo(f'Initialized accountability repo at {path} with the \
               following changes:\n- {'\n- '.join(progress)}')


@acc.command()
@click.option('--template', default='accountability_issue.md',
              help='template file to use for issue')
@click.option('-u','--username', prompt='your github username',)

def log(template,username):
    '''
    Create the content for a lab accountability entry interactively
    '''
    # get template and reqs
    if not template.endswith('.md'):
        template += '.md'
    md_template_out, text_feilds, file_feilds = parse_template(template)

    
    # prompt for file fields first
    data_dict = {}
    
    # prompt for files first
    data_dict = {'username':username,
                 'dates':get_date_range(),}
    
    for field in file_feilds:
        file_name = click.prompt(f'Path to {field.replace('_',' ')} json:', 
                                 default='generate',
                                 show_default=True)
        if file_name == 'generate':
            command = file_generator[field].format(**data_dict)
            click.echo(f'Running command: {command}')
            os.system(command)
            file_name = command.split('>')[-1].strip()
            file_path = os.path.join(os.getcwd(), file_name)
        else:
            file_path = file_name


        # load json and convert to checklists
        with open(file_path,'r') as f:
            issues_json_dict = json.load(f)
        
        checklist_type = field.split('_')[0] == 'open'
        out_feild = field.replace('issues','checklist')
        checklist = issues_to_checklist(issues_json_dict, open=checklist_type)
        # add the checklist to the data dict
        # data_dict[out_feild] = checklist
        text_feilds[out_feild] += checklist
        # click.echo(f'{out_feild.replace('_',' ').title()}:\n')
        # click.echo(checklist)


    # prompt for text fields
    for field, prompt in text_feilds.items():
        prompt_reponse = click.edit(prompt,editor='nano')
        # response = prompt_reponse.replace(prompt,'').strip()
        _, response = prompt_reponse.split(file_split,1)
        data_dict[field] = response
       

    md_issue = load_and_fill_template(md_template_out, data_dict)    
    click.echo(md_issue)


@acc.command()
@click.option('-r','--reference-date', default=None,
              help='reference date for date range (ISO format|YYYY-MM-DD) otherwise today')
@click.option('-d','--duration', default=7, type=int,
              help='number of days to look back from reference date')
def dates(reference_date, duration):
    '''
    Get the date range for the accountability entry
    '''
    date_range = get_date_range(reference_date, duration)
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
    create a markdown contents for a lab accountability issue
    '''
    # create the markdown file from template filled with checklists
 
    md_issue = generate_basic_acc_issue(closed_issues_json,open_issues_json)    
    click.echo(md_issue)


@acc.command()
@click.option('--name', prompt='your name',)
@click.option('--username', prompt='your github username',)
@click.option('-w','--day-of-week', prompt='day of week to run (1=Mon, 5=Fri)',type=int)
def schedule(username,name,day_of_week,duratation):
    '''
    create the action to schedule acc issues
    '''
    action = generate_schedule_action(username,name,day_of_week)
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



# article scrapper tool

@lab.group()
def articles():
    """Tools for scraping research articles and creating issues."""
    pass


@articles.command("issue")
@click.option('-p', '--paper-url', required=True, help='Enter the paper URL (ACM or NeurIPS)')
@click.option('-r', '--reason', default='', help='Why should we read this paper?')
def articles_issue(paper_url, reason):
    """Scrape ACM/NeurIPS and create an issue (no files saved)."""
    try:
        msg_or_url = create_github_paper_issue(
            paper_url=paper_url,
            reason=reason
        )
        click.echo(msg_or_url)
    except Exception as e:
        raise click.ClickException(str(e))

@articles.command()
@click.argument('path', default='.')

def init(path):
    """
    Initialize an articles repo at PATH (default current dir)
    """
    # Create .github/workflows directory
    os.makedirs(os.path.join(path, '.github', 'workflows'), exist_ok=True)

    # Write workflow file from template
    workflow_action = load_template_file('create_article_issue.yml')
    workflow_path = os.path.join(path, '.github', 'workflows', 'create_article_issue.yml')
    with open(workflow_path, 'w', encoding='utf-8') as f:
        f.write(workflow_action)

    # Add .gitignore
    git_ignore = load_template_file('gitignore.txt')
    with open(os.path.join(path, '.gitignore'), 'w', encoding='utf-8') as f:
        f.write(git_ignore)

