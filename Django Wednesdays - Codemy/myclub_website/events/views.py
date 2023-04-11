from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Event, Venue
from django.contrib.auth.models import User
from .forms import VenueForm, EventForm, EventFormAdmin
from django.http import HttpResponse
import csv

from django.contrib import messages

# PDF stuff
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

# Pagination stuff
from django.core.paginator import Paginator




def my_events(request):
     if request.user.is_authenticated:
          me = request.user.id
          events = Event.objects.filter(attendees=me)
          return render(request, 'events/my_events.html', {
               "events": events
          })
     else:
        messages.success(request, "You Are Not Authorized to View this page.")
        return redirect('home')



def venue_pdf(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)

    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    venues = Venue.objects.all()
    lines = []
    for venue in venues:
         lines.append(venue.name)
         lines.append(venue.address)
         lines.append(venue.zip_code)
         lines.append(venue.phone)
         lines.append("========")

    for line in lines:
         textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='venue.pdf')





def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=venues.csv'

    # Create a csv writer
    writer = csv.writer(response)

    # Designate the model
    venues = Venue.objects.all()

    # Add column headings
    writer.writerow(['Venue Name', 'Address', 'Zip Code', 'Phone'])

    for venue in venues:
         writer.writerow([venue.name, venue.address, venue.zip_code, venue.phone])

    return response




def venue_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=venues.txt'

    # Designate the model
    venues = Venue.objects.all()

    lines = []
    for venue in venues:
         lines.append(f'{venue.name}\n{venue.address}\n{venue.zip_code}\n\n\n')


    # Write to textfile
    response.writelines(lines)

    return response





def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()

    return redirect('list-venues')


def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user == event.manager:
        event.delete()
        messages.success(request, "You deleted an Event.")
        return redirect('list-events')
    else:
        messages.success(request, "You Are Not Authorized to delete this Event.")
        return redirect('list-events')
         




def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)

    if request.user.is_superuser:
        form = EventFormAdmin(request.POST or None, instance=event)
    else:
        form = EventForm(request.POST or None, instance=event)

    if form.is_valid():
                form.save()
                return redirect('list-events')

    return render(request, 'events/update_event.html', {
        'event': event,
        'form': form
    })



def add_event(request):
    submitted = False

    if request.method == 'POST':
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
        else:
            form = EventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.manager = request.user
                event.save()
                return HttpResponseRedirect('/add_event?submitted=True')

    else:
        if request.user.is_superuser:
             form = EventFormAdmin(request.POST)
        else:
             form = EventForm(request.POST)

        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'events/add_event.html', {
        'form': form,
        'submitted': submitted
    })


def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None, request.FILES or None, instance=venue)

    if form.is_valid():
                form.save()
                return redirect('list-venues')

    return render(request, 'events/update_venue.html', {
        'venue': venue,
        'form': form
    })




def search_events(request):
    if request.method == "POST":
        searched = request.POST['searched']
        events = Event.objects.filter(name__contains=searched)
        return render(request, 'events/search_events.html', {
            "searched": searched,
            "events": events
        })
    else: 
        return render(request, 'events/search_events.html')




def search_venues(request):
    if request.method == "POST":
        searched = request.POST['searched']
        venues = Venue.objects.filter(name__contains=searched)
        return render(request, 'events/search_venues.html', {
            "searched": searched,
            "venues": venues
        })
    else: 
        return render(request, 'events/search_venues.html')

def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue_owner = User.objects.get(pk=venue.owner)
    return render(request, 'events/show_venue.html', {
        'venue': venue,
        'venue_owner': venue_owner
    })




def list_venues(request):
    venue_list = Venue.objects.all()

    # set up pagination
    p = Paginator(Venue.objects.all(), 2)
    page = request.GET.get('page')

    venues = p.get_page(page)

    nums = "a" * venues.paginator.num_pages

    return render(request, 'events/venue.html', {
        'venue_list': venue_list,
        'venues': venues,
        "nums": nums
    })




def add_venue(request):
    submitted = False

    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.owner = request.user.id
            venue.save()
            # form.save()
            return HttpResponseRedirect('/add_venue?submitted=True')
    else:
        form = VenueForm
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'events/add_venue.html', {
        'form': form,
        'submitted': submitted
    })







def all_events(request):
    event_list = Event.objects.all().order_by('-event_date')

    return render(request, 'events/events_list.html', {
        'event_list': event_list
    })




# # Create your views here.
# def home(request, year=datetime.now().year, month=datetime.now().strftime("%B")):
#     month = month.capitalize()
#     month_number = datetime.strptime(month, '%B').month
#     month_number = int(month_number)

#     cal = HTMLCalendar().formatmonth(
#         year,
#         month_number
#     )

#     return render(request, 'events\home.html', {
#         'year': year,
#         'month': month,
#         'month_number': month_number,
#         'cal': cal
#     })

def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	name = "John"
	month = month.capitalize()
        
	# Convert month from name to number
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	# create a calendar
	cal = HTMLCalendar().formatmonth(
		year, 
		month_number)
	# Get current year
	now = datetime.now()
	current_year = now.year
	
	# Query the Events Model For Dates
	event_list = Event.objects.filter(
		event_date__year = year,
		event_date__month = month_number
		)

	# Get current time
	time = now.strftime('%I:%M %p')
	return render(request, 
		'events/home.html', {
		"name": name,
		"year": year,
		"month": month,
		"month_number": month_number,
		"cal": cal,
		"current_year": current_year,
		"time":time,
		"event_list": event_list,
		})