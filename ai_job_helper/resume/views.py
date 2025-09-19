from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# Stop persisting resume sections: do not import models/forms/services
from accounts.models import UserProfile

@login_required
def home(request):
    # Render builder without server-side forms
    return render(request, "resume/builder.html", {})

@login_required
@csrf_exempt
def save_section(request, section):
    return JsonResponse({'error': 'Disabled. Resume sections are not persisted.'}, status=410)

@login_required
def compile_resume(request):
    return JsonResponse({'error': 'Disabled. Use browser print to PDF from preview.'}, status=410)

@login_required
def get_resume_data(request):
    return JsonResponse({'error': 'Disabled. Use client-side preview.'}, status=410)


@login_required
def save_resume_to_profile(request):
    """Save raw resume preview text sent from client into profile if no resume_file exists."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        payload_text = request.POST.get('text') or ''
        if not payload_text:
            try:
                body = json.loads(request.body or '{}')
                payload_text = body.get('text', '')
            except Exception:
                payload_text = ''
        if not payload_text:
            return JsonResponse({'success': False, 'message': 'No text provided.'}, status=400)
        profile = request.user.userprofile
        if profile.resume_file:
            return JsonResponse({'success': False, 'message': 'Resume file already uploaded; skipped saving text.'})
        profile.extracted_text = payload_text
        profile.resume_text = payload_text
        profile.save()
        return JsonResponse({'success': True, 'message': 'Resume text saved to profile.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
