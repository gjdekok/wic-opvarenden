from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Min, Max, F, Q
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

from .models import Deed, ValidatedDeed
from .forms import DeedVerificationForm


class CustomLoginView(LoginView):
    template_name = 'login.html'

class CustomLogoutView(LogoutView):
    next_page = '/login'

@login_required
def first_deed(request):
    first_deed = Deed.objects.first()
    return redirect('verify_deed', deed_id=first_deed.id)

@login_required
def verify_deed(request, deed_id):
    deed = get_object_or_404(Deed, id=deed_id)
    old_validation_status = Deed.objects.get(id=deed_id).validation_complete
    
    # Get list of filtered deeds from session
    filtered_deed_ids = request.session.get('filtered_deed_ids', [])
    try:
        current_index = filtered_deed_ids.index(int(deed_id))
        prev_deed_id = filtered_deed_ids[current_index - 1] if current_index > 0 else None
        next_deed_id = filtered_deed_ids[current_index + 1] if current_index < len(filtered_deed_ids) - 1 else None
    except ValueError:  # if current deed_id is not in the list
        prev_deed_id = None
        next_deed_id = None

    prev_deed = Deed.objects.filter(id=prev_deed_id).first() if prev_deed_id else None
    next_deed = Deed.objects.filter(id=next_deed_id).first() if next_deed_id else None

    if request.method == 'POST':
        form = DeedVerificationForm(request.POST, instance=deed)
        if form.is_valid():
            with transaction.atomic():
                deed = form.save(commit=False)
                new_validation_status = form.cleaned_data.get('validation_complete')

                if new_validation_status and not old_validation_status:
                    # Only proceed if final_name is not empty
                    if deed.final_name:
                        print("Creating ValidatedDeed")
                        deed.save()
                        # Logic to copy data to ValidatedDeed
                        ValidatedDeed.objects.create(
                        deed_uri=deed.deed_uri,
                        deed_date=deed.deed_date,
                        name=deed.final_name,
                        location=deed.final_location,
                        ship_name=deed.final_ship_name,
                        role=deed.final_role,
                        organization=deed.final_organization,
                        captain=deed.final_captain,
                        chamber=deed.final_chamber,
                        shiptype=deed.final_shiptype,
                        remarks=deed.final_remarks,
                        sailor_uri=deed.sailor_uri,
                        location_uri=deed.location_uri
                    )
                    else:
                        print("Final name is empty, not creating ValidatedDeed")
                        deed.save()
                elif not new_validation_status and old_validation_status:
                    print("Deleting from ValidatedDeed, if exists")
                    deed.save()
                    # Try to remove data from ValidatedDeed, if it exists
                    ValidatedDeed.objects.filter(deed_uri=deed.deed_uri).delete()
                else:
                    deed.save()

                next_url = request.POST.get('next_url')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('deed_list')

        else:
            messages.error(request, 'There was an error with the submitted form. Please try again.')
    else:
        form = DeedVerificationForm(instance=deed)

    context = {
        'deed': deed,
        'form': form,
        'prev_deed': prev_deed,
        'next_deed': next_deed,      
    }
    return render(request, 'verify_deed.html', context)


@login_required
def deed_list(request):
    if request.method == 'POST':
        # Datatable server-side processing
        draw = int(request.POST.get('draw', None))
        start = int(request.POST.get('start', None))
        length = int(request.POST.get('length', None))
        search_value = request.POST.get('search[value]', None)
        order_column = int(request.POST.get('order[0][column]', None))
        order = request.POST.get('order[0][dir]', None)

        order_column = ['id', 'deed_date', 'final_name', 'final_location', 'final_ship_name', 'final_role', 'final_organization', 'final_captain', 'final_creditor_name', 'validation_complete'][order_column]

        # Initial query set
        query_set = Deed.objects.all()

        # Apply the year filter if provided
        min_year = request.POST.get('minYear', None)
        max_year = request.POST.get('maxYear', None)
        if min_year and max_year:
            query_set = query_set.filter(deed_date__year__gte=min_year, deed_date__year__lte=max_year)
        
        total_count = query_set.count()

        # Apply search filter
        if search_value:
            query_set = query_set.filter(Q(final_name__icontains=search_value) | 
                                          Q(final_location__icontains=search_value) | 
                                          Q(final_ship_name__icontains=search_value) | 
                                          Q(final_role__icontains=search_value) | 
                                          Q(final_organization__icontains=search_value) |
                                          Q(final_captain__icontains=search_value))  # added line

        count = query_set.count()

        # First reorder the queryset
        query_set = query_set.order_by('id')

        # Apply order
        if order == 'desc':
            query_set = query_set.order_by(F(order_column).desc(nulls_last=True), 'id')
        else:
            query_set = query_set.order_by(F(order_column).asc(nulls_last=True), 'id')

        # Then save ids of filtered deeds to session
        filtered_deeds_ids = list(query_set.values_list('id', flat=True))
        request.session['filtered_deed_ids'] = filtered_deeds_ids

        # Then apply length and start
        query_set = query_set[start:(start + length)]

        data = list(query_set.values('id', 'deed_date', 'final_name', 'final_location', 'final_ship_name', 'final_role', 'final_organization', 'final_captain', 'final_creditor_name', 'validation_complete'))  # added final_captain

        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_count,
            'recordsFiltered': count,
            'data': data,
        })

    else:
        # For GET request return the initial page
        deed_dates = Deed.objects.aggregate(min_year=Min('deed_date__year'), max_year=Max('deed_date__year'))
        min_year = deed_dates['min_year']
        max_year = deed_dates['max_year']

        return render(request, 'deed_list.html', {'min_year': min_year, 'max_year': max_year})



@login_required
def get_ship_names(request):
    if request.method == 'GET':
        term = request.GET.get('term', '')  # Get the term sent by autocomplete
        ship_names = Deed.objects.filter(
            suggested_ship_name__icontains=term  # Filter suggested_ship_name by the term
        ).values_list('final_ship_name', flat=True).distinct()
        data = list(ship_names)
        return JsonResponse(data, safe=False)

@login_required
def get_roles(request):
    if request.method == 'GET':
        term = request.GET.get('term', '')  # Get the term sent by autocomplete
        roles = Deed.objects.filter(
            final_role__icontains=term  # Use 'final_role__icontains'
        ).values_list('final_role', flat=True).distinct()
        data = list(roles)
        return JsonResponse(data, safe=False)

@login_required
def get_organizations(request):
    if request.method == 'GET':
        term = request.GET.get('term', '')  # Get the term sent by autocomplete
        organizations = Deed.objects.filter(
            final_organization__icontains=term  # Use 'final_organization__icontains'
        ).values_list('final_organization', flat=True).distinct()
        data = list(organizations)
        return JsonResponse(data, safe=False)