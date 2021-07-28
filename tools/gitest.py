from jira import JIRA
from github import Github, Organization, NamedUser, PullRequest, Repository

def create_jira_client(user, token, instance_name):
    options = {'server': 'https://jira.zalando.net/'.format(instance_name)}
    return JIRA(options, basic_auth=(user, token))

def get_lead_time(jira: JIRA, project: str, dt: str):
    query = 'project={} and created > {} and status=Done and type=Task'
    issues = [jira.issue(x) for x in jira.search_issues(query.format(project, dt))]
    return [[x.key,  x.fields.summary, 'Story', x.fields.created, x.fields.updated] for x in issues]

def get_incidents(jira: JIRA, project: str, dt: str):
    query = 'project={} and created > {} and type=Bug'
    issues = [jira.issue(x) for x in jira.search_issues(query.format(project, dt))]
    return [[x.key,  x.fields.summary, 'Bug', x.fields.created, x.fields.updated] for x in issues]

def create_github(url, token):
    return Github(base_url="https://{}/api/v3".format(url), login_or_token=token)

def get_org(g: Github, org_name: str):
    return [x for x in g.get_user().get_orgs() if x.name == org_name][0]

def get_members(org: Organization.Organization):
    return [(m.name, t.name) for t in org.get_teams() for m in t.get_members()]

def is_prod_bump(p: PullRequest.PullRequest):
    files = [x for x in p.get_files() if 'tags-info.json' in  x.filename]
    return len(files) > 0

def get_changes(p: PullRequest.PullRequest):
    from functools import reduce
    res = [[x.additions, x.changes, x.deletions] for x in p.get_files()]
    return reduce(lambda x,y: [x[0] + y[0], x[1] + y[1], x[2] + y[2]],res)

def get_comment_time(p: PullRequest.PullRequest):
    from datetime import datetime
    return str(min([x.created_at for x in p.get_comments()], default=datetime.min))

def get_merged_prs(repo: Repository.Repository):
    prs = (x for x in repo.get_pulls(state='closed') if x.merged)
    return ([x.user.name, x.comments, x.commits, str(parse(x.last_modified)),
             str(x.created_at), get_comment_time(x), is_prod_bump(x)] + get_changes(x) for x in prs)

def get_all_data(o: Organization.Organization):
    return (m for r in o.get_repos() for m in get_merged_prs(r))

git_tk = '9aaf7d192590a0f3c3128ec81dabe82325803520'

jira_client = create_jira_client('alemser', 'Z1@OceanO2010', 'Merchant Product Performance')
lead_time = get_lead_time(jira_client, 'mpp', '2021-07-01')
print(lead_time)

github_client = create_github('github.bus.zalan.do', git_tk)
org = get_org(github_client, 'Merchant Product Performance')

repo = github_client.get_repo("mpp/product-performance-api")
# pulls = repo.get_pulls(state='closed', base='master')
# filtered = filter(lambda pr: str(pr.title).startswith('MPP-1017'), pulls)
# print(get_comment_time(list(filtered)[0]))

issues = github_client.search_issues('is:pr in:title MPP-1017 is:merged')

for issue in issues:
    print(issue.__dict__.keys())
    print(issue.user.login)
    print(issue.created_at)
    print(issue.closed_at)
