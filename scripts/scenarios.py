"""Reproducible positive and negative requests, shared by HTTP and Postman runs."""
from dataclasses import dataclass,field

@dataclass
class Scenario:
    service:str
    name:str
    method:str
    path:str
    expected:int=200
    role:str='admin'
    body:dict|None=None
    save:dict=field(default_factory=dict)
    checks:list=field(default_factory=list)

def scenarios():
    result=[]
    def add(service,name,method,path,expected=200,role='admin',body=None,save=None,checks=None):
        result.append(Scenario(service,name,method,path,expected,role,body,save or {},checks or []))
    add('users','Administrator login','POST','/users/login',role='',body={'login':'{{admin_login}}','password':'{{admin_password}}'},save={'admin_token':'token','admin_id':'user.id'})
    add('users','Failed login','POST','/users/login',401,'',{'login':'{{admin_login}}','password':'WrongPassword!123'})
    roles={'analyst':'Security Analyst','employee':'Regular Employee/User','auditor':'Auditor','other':'Regular Employee/User','spare':'Regular Employee/User'}
    for key,role in roles.items():
        data={'full_name':'Demo '+key.title(),'username':'{{run_id}}_'+key,'email':'{{run_id}}_'+key+'@example.test','password':'DemoPassword!2026','department':'Security' if key=='analyst' else 'Operations','role':role}
        add('users','Register '+key,'POST','/users/register',201,'admin',data,{key+'_id':'id'})
        add('users','Login '+key,'POST','/users/login',200,'',{'login':data['username'],'password':'DemoPassword!2026'},{key+'_token':'token'})
    add('users','Reject duplicate username','POST','/users/register',409,'admin',dict(data,email='{{run_id}}_duplicate@example.test'))
    add('users','Reject public privilege escalation','POST','/users/register',403,'',dict(data,username='{{run_id}}_evil',email='{{run_id}}_evil@example.test',role='Security Administrator'))
    add('users','Reject invalid email','POST','/users/register',400,'',dict(data,email='invalid'))
    add('users','Reject weak password','POST','/users/register',400,'',dict(data,password='123'))
    add('users','Reject missing required fields','POST','/users/register',400,'',{'username':'bad'})
    add('users','Update own profile','PUT','/users/{{employee_id}}',200,'employee',{'full_name':'Demo Employee Updated','department':'IT'},checks=[['department','IT']])
    add('users','Retrieve own profile','GET','/users/{{run_id}}_employee',role='employee',checks=[['full_name','Demo Employee Updated']])
    add('users','Reject other profile access','GET','/users/{{run_id}}_employee',403,'other')
    add('users','List users','GET','/users')
    add('users','Find missing username','GET','/users/missing_{{run_id}}',404)
    add('users','Role and permission catalog','GET','/users/permissions')
    add('users','Reject analyst user management','GET','/users',403,'analyst')
    add('users','Reject missing authentication','GET','/users',401,'')
    add('users','Assign Auditor role','PUT','/users/{{spare_id}}/role',body={'role':'Auditor'})
    add('users','Revoked session after role change','GET','/users',401,'spare')
    add('users','Remove elevated role','DELETE','/users/{{spare_id}}/role',checks=[['role','Regular Employee/User']])
    add('users','Suspend account','PUT','/users/{{spare_id}}/status',body={'account_status':'Suspended'})
    add('users','Suspended login rejected','POST','/users/login',401,'',{'login':'{{run_id}}_spare','password':'DemoPassword!2026'})
    add('users','Set account inactive','PUT','/users/{{spare_id}}/status',body={'account_status':'Inactive'})
    add('users','Inactive login rejected','POST','/users/login',401,'',{'login':'{{run_id}}_spare','password':'DemoPassword!2026'})
    add('users','Reactivate account','PUT','/users/{{spare_id}}/status',body={'account_status':'Active'})
    add('users','Unauthorized user deletion','DELETE','/users/{{spare_id}}',403,'employee')
    add('users','Delete spare account','DELETE','/users/{{spare_id}}')
    add('users','Deleted user returns 404','GET','/users/{{run_id}}_spare',404)

    for n,(typ,criticality) in enumerate([('Server','Critical'),('Workstation','Medium'),('Application','Low')],1):
        add('assets','Create '+typ.lower(),'POST','/assets',201,body={'name':'{{run_id}} '+typ,'asset_type':typ,'ip_address':f'192.0.2.{10+n}','department':'IT','owner_id':'{{employee_id}}','criticality':criticality,'operating_system':'Linux','location':'Lab','status':'Active'},save={f'asset{n}_id':'id'})
    add('assets','Asset before update','GET','/assets/{{asset1_id}}')
    add('assets','Update asset','PUT','/assets/{{asset1_id}}',body={'name':'{{run_id}} Protected Server','status':'Under Maintenance'},checks=[['status','Under Maintenance']])
    add('assets','Asset after update','GET','/assets/{{asset1_id}}')
    add('assets','Asset change history','GET','/assets/{{asset1_id}}/history')
    add('assets','List assets','GET','/assets',role='auditor')
    for key,val in [('name','Protected'),('asset_type','Server'),('ip_address','192.0.2.11'),('department','IT'),('criticality','Critical')]:add('assets','Search assets by '+key,'GET','/assets/search?'+key+'='+val)
    add('assets','Missing asset','GET','/assets/99999999',404)
    add('assets','Invalid IP address','PUT','/assets/{{asset1_id}}',400,body={'ip_address':'999.2.3.4'})
    add('assets','Invalid criticality','PUT','/assets/{{asset1_id}}',400,body={'criticality':'Urgent'})
    add('assets','Unauthorized asset delete','DELETE','/assets/{{asset3_id}}',403,'analyst')
    add('assets','Delete unreferenced asset','DELETE','/assets/{{asset3_id}}')
    add('assets','Employee cannot list assets','GET','/assets',403,'employee')

    for n,severity in enumerate(('Low','Medium','High','Critical'),1):
        add('incidents','Report '+severity.lower()+' incident','POST','/incidents',201,'employee',{'title':f'{severity} lab incident','description':'Fictional controlled lab event for workflow verification.','category':'Phishing','severity':severity,'asset_id':'{{asset1_id}}','reporter_id':'{{employee_id}}'},{f'incident{n}_id':'id'})
    add('incidents','List all incidents','GET','/incidents',role='auditor')
    add('incidents','Employee submitted incidents','GET','/incidents',role='employee')
    add('incidents','Reject other reporter access','GET','/incidents/{{incident1_id}}',403,'other')
    add('incidents','Reject unassigned analyst','GET','/incidents/{{incident1_id}}',403,'analyst')
    add('incidents','Missing incident','GET','/incidents/99999999',404)
    add('incidents','Unauthorized assignment','PUT','/incidents/{{incident1_id}}/assign',403,'analyst',{'analyst_id':'{{analyst_id}}'})
    add('incidents','Reject non-analyst assignee','PUT','/incidents/{{incident1_id}}/assign',400,body={'analyst_id':'{{employee_id}}'})
    add('incidents','Assign analyst','PUT','/incidents/{{incident1_id}}/assign',body={'analyst_id':'{{analyst_id}}'})
    add('incidents','Analyst assigned incidents','GET','/incidents',role='analyst')
    add('assets','Analyst related asset','GET','/assets/{{asset1_id}}',role='analyst')
    add('assets','Analyst unrelated asset rejected','GET','/assets/{{asset2_id}}',403,'analyst')
    add('assets','Analyst scoped asset search','GET','/assets/search?department=IT',role='analyst')
    add('incidents','Reject skipped incident lifecycle','PUT','/incidents/{{incident1_id}}/status',409,'analyst',{'status':'Closed'})
    add('incidents','Investigation note','POST','/incidents/{{incident1_id}}/notes',201,'analyst',{'content':'Reviewed the lab message headers and isolated the affected test account.'})
    add('incidents','Retrieve incident with notes','GET','/incidents/{{incident1_id}}',role='analyst')
    for status in ('Under Investigation','Mitigated','Resolved','Closed'):add('incidents','Incident becomes '+status,'PUT','/incidents/{{incident1_id}}/status',role='analyst',body={'status':status},checks=[['status',status]])
    add('incidents','Employee status modification rejected','PUT','/incidents/{{incident2_id}}/status',403,'employee',{'status':'Under Investigation'})
    add('incidents','Invalid incident severity','POST','/incidents',400,'employee',{'title':'Invalid','description':'Rejected','category':'Phishing','severity':'Urgent','asset_id':'{{asset1_id}}'})
    add('assets','Prevent deletion of referenced asset','DELETE','/assets/{{asset1_id}}',409)

    for n,(kind,value,severity) in enumerate([('IP Address','198.51.100.10','High'),('Domain','{{run_id}}.example.test','Medium'),('File Hash','a'*64,'Critical')],1):
        # The two fixed indicators use a run-derived value for safe collection reruns.
        if kind=='IP Address':value='{{indicator_ip}}'
        if kind=='File Hash':value='{{indicator_hash}}'
        add('threats','Create '+kind+' indicator','POST','/threats',201,body={'threat_type':kind,'value':value,'description':'Fictional test indicator; not external threat intelligence.','severity':severity,'source':'Local lab'},save={f'threat{n}_id':'id'})
    add('threats','Duplicate indicator rejected','POST','/threats',409,body={'threat_type':'Domain','value':'{{run_id}}.example.test','description':'Duplicate','severity':'Low','source':'Lab'})
    add('threats','Invalid domain rejected','POST','/threats',400,body={'threat_type':'Domain','value':'not a domain','description':'Invalid','severity':'Low','source':'Lab'})
    add('threats','Invalid hash rejected','POST','/threats',400,body={'threat_type':'File Hash','value':'xyz','description':'Invalid','severity':'Low','source':'Lab'})
    add('threats','List threat indicators','GET','/threats',role='analyst')
    add('threats','Threat before update','GET','/threats/{{threat1_id}}')
    add('threats','Update threat information','PUT','/threats/{{threat1_id}}',body={'severity':'Critical','description':'Escalated lab indicator','source':'Lab review'})
    add('threats','Threat after update','GET','/threats/{{threat1_id}}')
    for key,val in [('threat_type','Domain'),('value','example.test'),('severity','Critical'),('source','Lab')]:add('threats','Search threats by '+key,'GET','/threats/search?'+key+'='+val,role='analyst')
    add('threats','Missing threat','GET','/threats/99999999',404)
    add('threats','Unauthorized threat deletion','DELETE','/threats/{{threat3_id}}',403,'analyst')
    add('threats','Delete threat','DELETE','/threats/{{threat3_id}}')
    add('threats','Employee threat access rejected','GET','/threats',403,'employee')

    for n,(severity,cvss) in enumerate([('Critical',9.8),('High',8.1),('Low',2.0)],1):
        add('vulnerabilities','Create '+severity.lower()+' vulnerability','POST','/vulnerabilities',201,body={'title':severity+' lab vulnerability','description':'Fictional record for API verification; identifier is a format example.','cve':f'CVE-2026-9900{n}','cvss':cvss,'severity':severity,'asset_id':'{{asset1_id}}','discovery_source':'Local test scanner'},save={f'vuln{n}_id':'id'})
    add('vulnerabilities','List vulnerabilities','GET','/vulnerabilities',role='analyst')
    add('vulnerabilities','Vulnerability before update','GET','/vulnerabilities/{{vuln1_id}}')
    add('vulnerabilities','Update vulnerability details','PUT','/vulnerabilities/{{vuln1_id}}',role='analyst',body={'description':'Remediation verified in controlled lab','cvss':9.1})
    add('vulnerabilities','Reject skipped remediation lifecycle','PUT','/vulnerabilities/{{vuln1_id}}',409,'analyst',{'status':'Closed'})
    for status in ('Under Investigation','In Progress','Resolved','Closed'):add('vulnerabilities','Vulnerability becomes '+status,'PUT','/vulnerabilities/{{vuln1_id}}',role='analyst',body={'status':status},checks=[['status',status]])
    add('vulnerabilities','Vulnerability after update','GET','/vulnerabilities/{{vuln1_id}}')
    for key,val in [('cve','CVE-2026-99001'),('severity','Critical'),('asset_id','{{asset1_id}}'),('status','Closed')]:add('vulnerabilities','Search vulnerabilities by '+key,'GET','/vulnerabilities/search?'+key+'='+val,role='analyst')
    add('vulnerabilities','Missing vulnerability','GET','/vulnerabilities/99999999',404)
    add('vulnerabilities','Invalid CVSS','PUT','/vulnerabilities/{{vuln1_id}}',400,body={'cvss':11})
    add('vulnerabilities','Unauthorized vulnerability delete','DELETE','/vulnerabilities/{{vuln3_id}}',403,'analyst')
    add('vulnerabilities','Delete vulnerability','DELETE','/vulnerabilities/{{vuln3_id}}')

    for n,kind in enumerate(('Security Alert','System Notification'),1):
        add('notifications','Create '+kind.lower(),'POST','/notifications',201,body={'user_id':'{{employee_id}}','title':kind+' example','message':'Controlled local demonstration','notification_type':kind,'severity':'Medium'},save={f'notification{n}_id':'id'})
    add('notifications','Employee personal notifications','GET','/notifications/user/{{employee_id}}',role='employee')
    add('notifications','Analyst assignment notification','GET','/notifications/user/{{analyst_id}}',role='analyst')
    add('notifications','Notification before read','GET','/notifications/{{notification1_id}}',role='employee',checks=[['status','Unread']])
    add('notifications','Mark notification read','PUT','/notifications/{{notification1_id}}/read',role='employee',checks=[['status','Read']])
    add('notifications','Notification after read','GET','/notifications/{{notification1_id}}',role='employee')
    add('notifications','Reject other notification access','GET','/notifications/{{notification1_id}}',403,'other')
    for key,val in [('user_id','{{employee_id}}'),('notification_type','Security%20Alert'),('severity','Medium'),('status','Read')]:add('notifications','Search notifications by '+key,'GET','/notifications/search?'+key+'='+val)
    add('notifications','Missing notification','GET','/notifications/99999999',404)
    add('notifications','Auditor cannot mark read','PUT','/notifications/{{notification1_id}}/read',403,'auditor')
    add('notifications','Unauthorized notification delete','DELETE','/notifications/{{notification2_id}}',403,'employee')
    add('notifications','Delete notification','DELETE','/notifications/{{notification2_id}}')

    for n in (1,2):add('playbooks','Create response playbook '+str(n),'POST','/playbooks',201,body={'name':'{{run_id}} Phishing response '+str(n),'description':'Controlled lab response procedure','incident_category':'Phishing','severity':'High'},save={f'playbook{n}_id':'id'})
    add('playbooks','List playbooks','GET','/playbooks',role='analyst')
    for n in (1,2):add('playbooks','Add ordered action '+str(n),'POST','/playbooks/{{playbook1_id}}/actions',201,'analyst',{'description':'Isolate test account' if n==1 else 'Verify recovery','step_number':n,'assigned_user_id':'{{analyst_id}}'},{f'action{n}_id':'id'})
    add('playbooks','Reject out of order action','PUT','/actions/{{action2_id}}/status',409,'analyst',{'status':'In Progress'})
    add('playbooks','Reject skipped action status','PUT','/actions/{{action1_id}}/status',409,'analyst',{'status':'Completed'})
    for n in (1,2):
        for status in ('In Progress','Completed'):add('playbooks',f'Action {n} becomes {status}','PUT',f'/actions/{{{{action{n}_id}}}}/status',role='analyst',body={'status':status},checks=[['status',status]])
    add('playbooks','Playbook with ordered actions and history','GET','/playbooks/{{playbook1_id}}',role='auditor')
    add('playbooks','Missing playbook','GET','/playbooks/99999999',404)
    add('playbooks','Unauthorized playbook deletion','DELETE','/playbooks/{{playbook2_id}}',403,'analyst')
    add('playbooks','Delete unused playbook','DELETE','/playbooks/{{playbook2_id}}')

    for n,user in enumerate(('admin','employee'),1):add('logs','Create manual audit log '+str(n),'POST','/logs',201,body={'user_id':'{{'+user+'_id}}','action':'lab.review','description':'Manual verification event','severity':'Information','related_service':'logs'},save={f'log{n}_id':'id'})
    add('logs','List automatic and manual logs','GET','/logs',role='auditor')
    add('logs','Retrieve audit record','GET','/logs/{{log1_id}}',role='analyst')
    add('logs','Missing audit record','GET','/logs/99999999',404)
    for key,val in [('user_id','{{employee_id}}'),('date','{{today}}'),('action','login.failed'),('severity','Warning'),('related_service','incidents')]:add('logs','Search logs by '+key,'GET','/logs/search?'+key+'='+val,role='auditor')
    add('logs','Logs by user','GET','/logs/user/{{employee_id}}',role='auditor')
    add('logs','Unauthorized audit deletion','DELETE','/logs/{{log2_id}}',403,'analyst')
    add('logs','Delete manual audit log','DELETE','/logs/{{log2_id}}')
    for kind in ('summary','incidents','assets','threats','vulnerabilities','activity'):add('reports','Generate '+kind+' report','GET','/reports/'+kind,role='auditor')
    add('reports','Analyst reports rejected','GET','/reports/summary',403,'analyst')
    add('reports','Employee reports rejected','GET','/reports/summary',403,'employee')
    add('users','Employee logout','POST','/users/logout',role='employee')
    add('users','Logged out token rejected','GET','/users/{{run_id}}_employee',401,'employee')
    return result
