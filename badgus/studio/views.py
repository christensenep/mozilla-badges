import badger.views
from badger import settings as bsettings
from badger.forms import BadgeNewForm
import constance.config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponseRedirect, HttpResponse,
        HttpResponseForbidden, HttpResponseNotFound, Http404)
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.encoding import force_text
from django.views.decorators.http import (require_GET, require_POST,
                                          require_http_methods)
import json
from urllib import urlencode

from badger.models import Badge
from .models import Design
from .forms import DesignForm


try:
    from funfactory.urlresolvers import reverse
except ImportError:
    from django.core.urlresolvers import reverse


def _show_meta_data_form (image, request):
    # Render meta form
    # Annoyingly we're having to recreate all this logic here :(
    form = BadgeNewForm()
    form.initial['tags'] = request.GET.get('tags', '')
    return render_to_response('%s/badge_create.html' % bsettings.TEMPLATE_BASE, dict(
        image = image,
        form = form,
    ), context_instance=RequestContext(request))


def _save_badge (form, previous, request):
    # Process meta form
    # We're having to replicate all of this logic too
    badge = form.save(commit=False)
    badge.creator = request.user
    badge.save()
    form.save_m2m()
    previous.badge = badge
    previous.save()
    return HttpResponseRedirect(reverse(
            'badger.views.detail', args=(badge.slug,)))



@require_http_methods(['GET', 'POST'])
@login_required
def create (request):
    # Restrict badge creation to mozillians, if enabled.
    if constance.config.BADGER_ALLOW_ADD_ONLY_BY_MOZILLIANS:
        profile = request.user.get_profile()
        if not profile.is_vouched_mozillian():
            return HttpResponseForbidden()

    previous = Design.get_previous_for_user(request.user)

    if request.method == 'POST':
        if request.POST.get('is_design', 0):
            form = DesignForm(request.POST)
            if form.is_valid():
                design = form.save(commit=False)
                design.creator = request.user
                design.save()

                if previous:
                    previous.delete()

                return _show_meta_data_form(design.image, request)

            messages.error(request, 'There was an error saving your design')
        else:
            request.FILES['image'] = previous.image
            form = BadgeNewForm(request.POST, request.FILES)
            if form.is_valid():
                return _save_badge(form, previous, request)
            else:
                return _show_meta_data_form(previous.image, request)
    else:
        form = DesignForm()

    if (previous):
        print request.GET
        if 'yes' in request.GET.get('resume', []):
            form = DesignForm(instance=previous)
        else:
            attrs = request.GET.copy()
            attrs['resume'] = 'yes'
            messages.info(request, 'You have a previously started design - <a href="?%s" class="alert-link">would you like to finish it?</a>' % (
                urlencode(attrs)
            ))

    return render_to_response('studio/create.html', dict(
        form=form,
    ), context_instance=RequestContext(request))


@require_http_methods(['GET', 'POST'])
@login_required
def edit_meta (request, slug):
    badge = get_object_or_404(Badge, slug=slug)
    try:
        design = Design.objects.get(badge=badge)
        request.can_edit_design = True
    except Design.DoesNotExist:
        request.can_edit_design = False

    if request.method == 'GET':
        return badger.views.edit(request, slug)

    response = badger.views.edit(request, slug)
    if not isinstance(response, HttpResponseRedirect):
        return response

    if request.POST['action'] != 'save-edit-image':
        return response

    return HttpResponseRedirect(reverse('edit_badge_design', args=(slug,)))


@require_http_methods(['GET', 'POST'])
@login_required
def edit_design (request, slug):
    badge = get_object_or_404(Badge, slug=slug)
    if not badge.allows_edit_by(request.user):
        return HttpResponseForbidden()

    design = Design.objects.get(badge=badge)
    if not design:
        return HttpResponseNotFound()

    if request.method == 'GET':
        form = DesignForm(instance=design)
    else:
        form = DesignForm(request.POST)
        if form.is_valid():
            new_design = form.save(commit=False)
            new_design.creator = design.creator
            design.save()
            badge.image = new_design.image
            badge.save()
            return HttpResponseRedirect(reverse('badger.views.detail', args=(slug,)))

    return render_to_response('studio/edit.html', dict(
        badge=badge,
        form=form,
    ), context_instance=RequestContext(request))

