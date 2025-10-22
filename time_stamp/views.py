from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
    return render(request, 'time_stamp/timer.html', {'form': form})