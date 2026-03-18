from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from time_entries.models import TimeEntry
from time_entries.forms import TimeEntryForm
from .models import TimerSession
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import datetime
import json
from django.utils import timezone

@login_required
def timer_view(request):
    if request.method == 'POST':
        form = TimeEntryForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            time_entry = form.save(commit=False)
            time_entry.user = request.user
            pause_duration_seconds = request.POST.get('pause_duration', 0)
            time_entry.pause_duration = datetime.timedelta(seconds=float(pause_duration_seconds))

            time_entry.save()
            
            session_id = request.POST.get('session_id')
            if session_id:
                try:
                    TimerSession.objects.filter(id=session_id, user=request.user).delete()
                except Exception:
                    pass
            
            return JsonResponse({'status': 'success'})

        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = TimeEntryForm(user=request.user)
        time_entries = TimeEntry.objects.filter(user=request.user).order_by('-date', '-start_time')[:10]
        context = {
            'form': form,
            'time_entries': time_entries
        }
        if request.user.is_staff or request.user.is_superuser:
            from accounts.models import CustomUser
            context['all_users'] = CustomUser.objects.filter(is_active=True).exclude(id=request.user.id)
    return render(request, 'time_stamp/timer.html', context)

@login_required
@require_POST
def start_timer_session(request):
    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')
        organization_id = data.get('organization_id')
        assigned_user_id = data.get('assigned_user_id')
        
        target_user = request.user
        assigned_by = None
        if assigned_user_id and (request.user.is_staff or request.user.is_superuser):
            from accounts.models import CustomUser
            target_user = get_object_or_404(CustomUser, id=assigned_user_id)
            assigned_by = request.user
            
        if not project_id:
            return JsonResponse({'status': 'error', 'message': 'Project is required'}, status=400)
            
        session = TimerSession.objects.create(
            user=target_user,
            assigned_by=assigned_by,
            project_id=project_id,
            organization_id=organization_id if organization_id else None,
            status='RUNNING',
            is_running=True,
            start_time=timezone.now(),
            activity_log=[{'action': 'Started', 'time': timezone.now().isoformat()}]
        )
        return JsonResponse({'status': 'success', 'session_id': session.id, 'start_time': session.start_time.isoformat()})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def pause_timer_session(request, session_id):
    session = get_object_or_404(TimerSession, id=session_id, user=request.user)
    if session.is_running:
        session.is_running = False
        session.status = 'PAUSED'
        session.pause_time = timezone.now()
        
        log = session.activity_log
        log.append({'action': 'Paused', 'time': session.pause_time.isoformat()})
        session.activity_log = log
        session.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Timer is not running'}, status=400)

@login_required
@require_POST
def resume_timer_session(request, session_id):
    session = get_object_or_404(TimerSession, id=session_id, user=request.user)
    if not session.is_running and session.status == 'PAUSED':
        now = timezone.now()
        paused_duration = now - session.pause_time
        session.accumulated_time += paused_duration
        
        session.is_running = True
        session.status = 'RUNNING'
        session.pause_time = None
        
        log = session.activity_log
        log.append({'action': 'Resumed', 'time': now.isoformat()})
        session.activity_log = log
        session.save()
        return JsonResponse({'status': 'success', 'accumulated_time': session.accumulated_time.total_seconds()})
    return JsonResponse({'status': 'error', 'message': 'Timer is already running'}, status=400)

@login_required
@require_POST
def stop_timer_session(request, session_id):
    session = get_object_or_404(TimerSession, id=session_id, user=request.user)
    now = timezone.now()
    
    if session.is_running:
        session.is_running = False
        log = session.activity_log
        log.append({'action': 'Stopped', 'time': now.isoformat()})
        session.activity_log = log
    elif session.status == 'PAUSED':
        paused_duration = now - session.pause_time
        session.accumulated_time += paused_duration
        log = session.activity_log
        log.append({'action': 'Stopped', 'time': now.isoformat()})
        session.activity_log = log

    session.status = 'DRAFT'
    session.end_time = now
    session.save()
    
    return JsonResponse({
        'status': 'success',
        'project_id': session.project_id,
        'organization_id': session.organization_id,
        'start_time': session.start_time.isoformat() if session.start_time else None,
        'end_time': session.end_time.isoformat() if session.end_time else None,
        'accumulated_pause_seconds': session.accumulated_time.total_seconds(),
    })

@login_required
@require_POST
def delete_timer_session(request, session_id):
    session = get_object_or_404(TimerSession, id=session_id, user=request.user)
    session.delete()
    return JsonResponse({'status': 'success'})

@login_required
def get_timer_options(request):
    from accounts.models import CustomUser, Organization, Contact
    from projects.models import Project
    
    user_id = request.GET.get('user_id')
    org_id = request.GET.get('org_id')
    contact_id = request.GET.get('contact_id')
    
    target_user = request.user
    if user_id and (request.user.is_staff or request.user.is_superuser):
        target_user = get_object_or_404(CustomUser, id=user_id)
        
    orgs = Organization.objects.filter(members__user=target_user, deleted=False).distinct().order_by('-id')
    
    if org_id:
        contacts = Contact.objects.filter(organization__members__user=target_user, organization_id=org_id, deleted=False).distinct().order_by('-id')
        if contact_id:
            projects = Project.objects.filter(members=target_user, organization_id=org_id, contact_id=contact_id, deleted=False).distinct().order_by('-id')
        else:
            projects = Project.objects.filter(members=target_user, organization_id=org_id, deleted=False).distinct().order_by('-id')
    else:
        contacts = Contact.objects.filter(organization__members__user=target_user, deleted=False).distinct().order_by('-id')
        if contact_id:
            projects = Project.objects.filter(members=target_user, contact_id=contact_id, deleted=False).distinct().order_by('-id')
        else:
            projects = Project.objects.filter(members=target_user, deleted=False).distinct().order_by('-id')
        
    org_data = [{'id': o.id, 'name': o.name} for o in orgs]
    contact_data = [{'id': c.id, 'name': c.name} for c in contacts]
    project_data = [{'id': p.id, 'name': p.name} for p in projects]
    
    return JsonResponse({
        'organizations': org_data,
        'contacts': contact_data,
        'projects': project_data
    })

@login_required
def get_active_sessions(request):
    sessions = TimerSession.objects.filter(user=request.user, status__in=['RUNNING', 'PAUSED', 'DRAFT']).order_by('-created_at')
    data = []
    for s in sessions:
        rate = 0.0
        currency = 'USD'
        if s.project_id:
            try:
                pm = ProjectMember.objects.get(project_id=s.project_id, user=s.user)
                rate = float(pm.hourly_rate)
                
                # Fetch project explicitly or through relation
                proj = Project.objects.get(id=s.project_id)
                if hasattr(proj, 'currency'):
                    currency = proj.currency
            except Exception:
                pass
            
        data.append({
            'id': s.id,
            'status': s.status,
            'project_id': s.project_id,
            'organization_id': s.organization_id,
            'is_running': s.is_running,
            'start_time': s.start_time.isoformat() if s.start_time else None,
            'pause_time': s.pause_time.isoformat() if s.pause_time else None,
            'end_time': s.end_time.isoformat() if s.end_time else None,
            'accumulated_time': s.accumulated_time.total_seconds(),
            'activity_log': s.activity_log,
            'hourly_rate': rate,
            'currency': currency
        })
    return JsonResponse({'status': 'success', 'sessions': data})