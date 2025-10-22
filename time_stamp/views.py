from django.shortcuts import render
from django.http import JsonResponse
from time_entries.models import TimeEntry
from time_entries.forms import TimeEntryForm
from django.contrib.auth.decorators import login_required

@login_required
def timer_view(request):
    if request.method == 'POST':
        form = TimeEntryForm(request.POST, request.FILES)
        if form.is_valid():
            time_entry = form.save(commit=False)
            time_entry.user = request.user
            time_entry.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = TimeEntryForm()
        time_entries = TimeEntry.objects.filter(user=request.user).order_by('-start_time')[:10]
        context = {
            'form': form,
            'time_entries': time_entries
        }
    return render(request, 'time_stamp/timer.html', context)