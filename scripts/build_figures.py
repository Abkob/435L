from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch

OUT=Path(__file__).resolve().parents[1]/'docs/figures'
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12})

def box(ax,x,y,w,h,title,detail='',fill='#f5f7fa'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012,rounding_size=0.035',facecolor=fill,edgecolor='#485b6b',linewidth=1.3))
    ax.text(x+w/2,y+h-.23,title,ha='center',va='top',weight='bold',fontsize=12)
    if detail:ax.text(x+w/2,y+h-.64,detail,ha='center',va='top',fontsize=10,linespacing=1.45)

def arrow(ax,start,end,label=None):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=13,color='#536d82',linewidth=1.2))
    if label:ax.text((start[0]+end[0])/2,(start[1]+end[1])/2+(.22 if abs(start[1]-end[1])<.1 else 0),label,ha='center',va='center',fontsize=9,bbox={'facecolor':'white','edgecolor':'none','pad':2})

fig,ax=plt.subplots(figsize=(12,9));ax.set(xlim=(0,12),ylim=(0,9));ax.axis('off')
box(ax,3.8,7.8,4.4,.9,'Postman and API clients','Bearer token on protected requests')
arrow(ax,(6,7.8),(6,7.15),'REST / JSON')
labels=[('Identity','5101 • login, roles, sessions'),('Assets','5102 • inventory and history'),('Incidents','5103 • investigation lifecycle'),('Threat intelligence','5104 • indicators and search'),('Audit logs','5105 • immutable records'),('Reports','5106 • HTTP aggregation'),('Vulnerabilities','5107 • remediation lifecycle'),('Notifications','5108 • user alerts and read status'),('Playbooks','5109 • ordered response actions')]
for i,(title,detail) in enumerate(labels):
    row,col=divmod(i,3);box(ax,.4+col*4,5.95-row*1.4,3.2,1.02,title,detail)
ax.text(6,2.5,'HTTP integration: identity introspection • entity validation • report collection',ha='center',fontsize=11)
ax.text(6,2.15,'Durable outbox → audit and notification APIs → idempotent consumers',ha='center',fontsize=11)
arrow(ax,(6,1.98),(6,1.65))
box(ax,.8,.5,10.4,1.05,'Shared SQLite database','Foreign keys • transactions • unique constraints • histories • verified local backups','#eaf0f5')
ax.text(6,.15,'Nine independent processes; one shared relational store for Sprint 1',ha='center',fontsize=10)
fig.savefig(OUT/'architecture.png',dpi=180,bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(12,9));ax.set(xlim=(0,12),ylim=(0,9));ax.axis('off')
boxes={
 'users':(4.45,6.55,3.1,1.65,'Users','PK id\nusername and email UNIQUE\nrole • status • password hash'),
 'assets':(.2,3.7,3.4,1.65,'Assets','PK id • FK owner_id\nIP • type • criticality • status'),
 'incidents':(4.45,3.5,3.1,1.9,'Incidents','PK id\nFK reporter_id • analyst_id\nFK asset_id • lifecycle'),
 'logs':(8.4,6.55,3.4,1.65,'Logs','PK id • FK user_id\nimmutable event content'),
 'notifications':(8.4,3.7,3.4,1.65,'Notifications','PK id • FK user_id\nUnread / Read • timestamps'),
 'vulnerabilities':(.2,.6,3.4,1.75,'Vulnerabilities','PK id • FK asset_id\nCVE • CVSS • status\nseverity • resolution date'),
 'notes':(4.45,.6,3.1,1.75,'Investigation notes','PK id • FK incident_id\nFK analyst_id\ncontent • timestamp'),
 'threats':(8.4,.6,3.4,1.75,'Threats','PK id\nUNIQUE type and value\nseverity • source')}
for b in boxes.values():box(ax,*b)
arrow(ax,(4.5,6.55),(2,5.35),'1 owns many')
arrow(ax,(5.4,6.55),(5.4,5.4),'1 reports many')
arrow(ax,(6.65,6.55),(6.65,5.4),'1 assigned many')
arrow(ax,(7.55,7.35),(8.4,7.35),'1 : many')
arrow(ax,(7.55,6.55),(9.75,5.35),'1 : many')
arrow(ax,(3.6,4.6),(4.45,4.6),'1 : many')
arrow(ax,(1.8,3.7),(1.8,2.35),'1 : many')
arrow(ax,(6,3.5),(6,2.35),'1 : many')
ax.text(6,8.65,'Ownership and incident data relationships',ha='center',fontsize=17,weight='bold')
fig.savefig(OUT/'entity-relationships.png',dpi=180,bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(12,5.8));ax.set(xlim=(0,12),ylim=(0,5.8));ax.axis('off')
box(ax,.3,3.5,3.1,1.45,'Users','PK id\ncreator and assigned user')
box(ax,4.45,3.5,3.1,1.45,'Playbooks','PK id • FK created_by\ncategory • severity • deleted_at')
box(ax,8.6,3.5,3.1,1.45,'Response actions','PK id • FK playbook_id\nFK assigned_user_id • step')
box(ax,8.6,.65,3.1,1.65,'Action history','PK id • FK action_id\nFK actor_id and assignee\nold/new status • timestamp')
box(ax,.3,.65,3.1,1.65,'Asset history','PK id • logical asset_id\nFK actor_id\nbefore and after JSON')
box(ax,4.45,.65,3.1,1.65,'Outbox','PK event UUID\nsource • target • payload\ndelivery timestamp • retries')
arrow(ax,(3.4,4.3),(4.45,4.3),'1 : many')
arrow(ax,(7.55,4.3),(8.6,4.3),'1 : many')
arrow(ax,(10.15,3.5),(10.15,2.3),'1 : many')
arrow(ax,(1.85,3.5),(1.85,2.3),'actor')
ax.text(6,5.5,'Response execution and supporting history tables',ha='center',fontsize=17,weight='bold')
ax.text(6,.15,'Sessions reference users; login attempts support rate limiting. Logical asset IDs retain history after deletion.',ha='center',fontsize=10)
fig.savefig(OUT/'response-relationships.png',dpi=180,bbox_inches='tight');plt.close(fig)
print(OUT)
