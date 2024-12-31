# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import json
import csv
import logging
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from .models import LandingPage, CapturedData
from .models import Group, User
from django.utils.timezone import now
from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
from .models import EmailTemplate  # Assuming EmailTemplate model is defined in models.py


logger = logging.getLogger(__name__)  # Set up logging


# apps/home/views.py
from django.shortcuts import render, redirect

def login_user(request):
    return render(request, 'accounts/login.html')

def register_user(request):
    return render(request, 'accounts/register.html')

def logout_user(request):
    """
    Logs out the current user and redirects to the home page.
    """
    logout(request)  # Logs out the user
    return redirect('home')  # Redirect to the home page



# View functions
def index(request):
    return render(request, 'home/index.html')


def landing_pages(request):
    try:
        pages = LandingPage.objects.all().order_by('-created_at')
        return render(request, 'home/landing-pages.html', {'pages': pages})
    except Exception as e:
        logger.error(f"Error fetching landing pages: {str(e)}")
        return render(request, 'home/landing-pages.html', {'error': str(e)})


def campaign_user(request):
    return render(request, 'home/campaign-user.html')


def page_user(request):
    return render(request, 'home/page-user.html')


def ui_tables(request):
    return render(request, 'home/ui-tables.html')


def ui_typography(request):
    return render(request, 'home/ui-typography.html')


def ui_icons(request):
    return render(request, 'home/ui-icons.html')


def ui_maps(request):
    return render(request, 'home/ui-maps.html')


def ui_notifications(request):
    return render(request, 'home/ui-notifications.html')


@csrf_exempt
def save_landing_page(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            capture_data = data.get('capture_data', False)
            redirect_url = data.get('redirect_url', None)
            collect_emails = data.get('collect_emails', False)
            credential_harvesting = data.get('credential_harvesting', False)
            import_site = data.get('import_site', None)
            geolocation_tracking = data.get('geolocation_tracking', False)

            if not title or not content:
                return JsonResponse({'error': 'Title and content are required.'}, status=400)

            # Handle importing content from a URL
            if import_site:
                try:
                    response = requests.get(import_site, timeout=10)
                    response.raise_for_status()
                    content = response.text
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error importing site: {str(e)}")
                    return JsonResponse({'error': f"Error importing site: {str(e)}"}, status=400)

            landing_page = LandingPage.objects.create(
                title=title,
                content=content,
                capture_data=capture_data,
                redirect_url=redirect_url,
                collect_emails=collect_emails,
                credential_harvesting=credential_harvesting,
                geolocation_tracking=geolocation_tracking,
            )
            return JsonResponse({'message': 'Landing page saved successfully!'}, status=200)
        except Exception as e:
            logger.error(f"Error saving landing page: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def edit_landing_page(request, page_id):
    page = get_object_or_404(LandingPage, id=page_id)
    if request.method == 'GET':
        return JsonResponse({
            'title': page.title,
            'content': page.content,
            'capture_data': page.capture_data,
            'redirect_url': page.redirect_url,
            'collect_emails': page.collect_emails,
            'credential_harvesting': page.credential_harvesting,
            'geolocation_tracking': page.geolocation_tracking,
        })
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            page.title = data.get('title', page.title)
            page.content = data.get('content', page.content)
            page.capture_data = data.get('capture_data', page.capture_data)
            page.redirect_url = data.get('redirect_url', page.redirect_url)
            page.collect_emails = data.get('collect_emails', page.collect_emails)
            page.credential_harvesting = data.get('credential_harvesting', page.credential_harvesting)
            page.geolocation_tracking = data.get('geolocation_tracking', page.geolocation_tracking)
            page.save()
            return JsonResponse({'message': 'Landing page updated successfully!'}, status=200)
        except Exception as e:
            logger.error(f"Error editing landing page: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def delete_landing_page(request, page_id):
    if request.method == 'DELETE':
        page = get_object_or_404(LandingPage, id=page_id)
        page.delete()
        return JsonResponse({'message': 'Landing page deleted successfully!'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def capture_submission(request, page_id):
    page = get_object_or_404(LandingPage, id=page_id)
    if page.capture_data:
        data = request.POST.dict()
        try:
            if page.collect_emails:
                email = data.get('email')
                if email:
                    try:
                        validate_email(email)
                    except ValidationError:
                        return JsonResponse({'error': 'Invalid email format.'}, status=400)
            CapturedData.objects.create(landing_page=page, submitted_data=data)
            if page.redirect_url:
                return redirect(page.redirect_url)
            return JsonResponse({'message': 'Data captured successfully!'})
        except Exception as e:
            logger.error(f"Error capturing submission: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Data capture not enabled for this page.'}, status=400)


@csrf_exempt
def analytics_report(request, page_id):
    try:
        page = get_object_or_404(LandingPage, id=page_id)
        data = list(CapturedData.objects.filter(landing_page=page).values())
        return JsonResponse({'analytics': data})
    except Exception as e:
        logger.error(f"Error generating analytics report: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def import_site(request):
    """
    Imports the HTML content from a given site URL and handles common errors.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            site_url = data.get('site_url', None)

            if not site_url:
                return JsonResponse({'error': 'Site URL is required.'}, status=400)

            if not site_url.startswith(('http://', 'https://')):
                return JsonResponse({'error': 'Invalid URL format.'}, status=400)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }

            response = requests.get(site_url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise error for HTTP codes like 406

            soup = BeautifulSoup(response.content, 'html.parser')
            for tag in soup(['script', 'iframe', 'style', 'link']):
                tag.decompose()

            sanitized_html = soup.prettify()
            return JsonResponse({'content': sanitized_html}, status=200)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 406:
                logger.error(f"406 Error for URL {site_url}: {str(e)}")
                return JsonResponse({'error': 'The server rejected the request. The URL may block automated access.'}, status=400)
            logger.error(f"HTTP error for URL {site_url}: {str(e)}")
            return JsonResponse({'error': f"HTTP error: {str(e)}"}, status=400)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error importing site: {str(e)}")
            return JsonResponse({'error': f"Error importing site: {str(e)}"}, status=400)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': f"Unexpected error: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def send_email(request):
    if request.method == 'POST':
        try:
            to_email = request.POST.get('to')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            if not to_email or not subject or not message:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            try:
                validate_email(to_email)
            except ValidationError:
                return JsonResponse({'error': 'Invalid email format.'}, status=400)

            send_mail(subject, message, 'your_email@example.com', [to_email])
            return JsonResponse({'message': 'Email sent successfully!'}, status=200)
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def preview_landing_page(request, page_id):
    page = get_object_or_404(LandingPage, id=page_id)
    return render(request, 'home/preview.html', {'content': page.content})

@csrf_exempt
def preview_imported_site(request):
    """
    Preview the HTML content fetched from the imported site.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get("content", "")

            if not content:
                return JsonResponse({"error": "Content is empty."}, status=400)

            # Render the imported content in a preview template
            return render(request, "home/preview_imported_site.html", {"content": content})

        except Exception as e:
            logger.error(f"Error rendering preview: {str(e)}")
            return JsonResponse({"error": f"Error rendering preview: {str(e)}"}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def geolocation_tracking(request, page_id):
    """
    Fetch geolocation data for a submission.
    """
    try:
        page = get_object_or_404(LandingPage, id=page_id)
        if not page.geolocation_tracking:
            return JsonResponse({'error': 'Geolocation tracking is not enabled for this page.'}, status=400)

        response = requests.get('http://ip-api.com/json/', timeout=5)
        response.raise_for_status()
        geo_data = response.json()
        return JsonResponse({'geolocation': geo_data}, status=200)

    except requests.exceptions.RequestException as e:
        logger.error(f"Geolocation tracking failed: {str(e)}")
        return JsonResponse({'error': f"Geolocation tracking failed: {str(e)}"}, status=400)
    except Exception as e:
        logger.error(f"Error during geolocation tracking: {str(e)}")
        return JsonResponse({'error': f"Error during geolocation tracking: {str(e)}"}, status=400)


@csrf_exempt
def email_collection(request, page_id):
    """
    Collect emails for a specific landing page.
    """
    page = get_object_or_404(LandingPage, id=page_id)
    if request.method == 'POST':
        try:
            email = request.POST.get('email', '').strip()
            if not email:
                return JsonResponse({'error': 'Email is required.'}, status=400)

            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'error': 'Invalid email format.'}, status=400)

            CapturedData.objects.create(
                landing_page=page,
                submitted_data={'email': email},
            )
            return JsonResponse({'message': 'Email collected successfully!'}, status=200)
        except Exception as e:
            logger.error(f"Error collecting email: {str(e)}")
            return JsonResponse({'error': f"Error collecting email: {str(e)}"}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def analytics_report_paginated(request, page_id):
    """
    Analytics report with pagination for captured data.
    """
    try:
        page = get_object_or_404(LandingPage, id=page_id)
        captured_data = CapturedData.objects.filter(landing_page=page)
        page_number = int(request.GET.get('page', 1))
        per_page = 10
        start = (page_number - 1) * per_page
        end = start + per_page
        data = list(captured_data.values()[start:end])

        return JsonResponse({
            'page': page_number,
            'total_entries': captured_data.count(),
            'entries': data,
        })
    except Exception as e:
        logger.error(f"Error generating paginated analytics report: {str(e)}")
        return JsonResponse({'error': f"Error generating paginated analytics report: {str(e)}"}, status=400)


@csrf_exempt
def delete_captured_data(request, data_id):
    """
    Delete specific captured data.
    """
    if request.method == 'DELETE':
        try:
            captured_data = get_object_or_404(CapturedData, id=data_id)
            captured_data.delete()
            return JsonResponse({'message': 'Captured data deleted successfully!'}, status=200)
        except Exception as e:
            logger.error(f"Error deleting captured data: {str(e)}")
            return JsonResponse({'error': f"Error deleting captured data: {str(e)}"}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def custom_404_view(request, exception=None):
    """
    Custom 404 error page.
    """
    return render(request, 'home/404.html', status=404)


def custom_500_view(request):
    """
    Custom 500 error page.
    """
    return render(request, 'home/500.html', status=500)

# ----------------------------------------------------------------------------------------------------------

# Saving Group Data
@csrf_exempt
def save_group_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            group_name = data['group_name']
            users = data['users']

            try:
                group = Group.objects.get(name=group_name)
                
                for user in users:
                    User.objects.get_or_create(
                        first_name=user['firstName'],
                        last_name=user['lastName'],
                        email=user['email'],
                        position=user['position'],
                        group=group
                    )

            except Group.DoesNotExist:
            
                group = Group.objects.create(name=group_name)
                
                for user in users:
                    User.objects.create(
                        first_name=user['firstName'],
                        last_name=user['lastName'],
                        email=user['email'],
                        position=user['position'],
                        group=group
                    )
            
            return JsonResponse({'message': 'Group and users saved successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# Fetching All Groups

def fetch_groups(request):
    """
    Fetch all groups with their user counts and return as JSON.
    """
    groups = Group.objects.all().values("id", "name", "updated_at")
    response = []

    # Loop through each group and count the users
    for group in groups:
        response.append({
            "id": group["id"],
            "name": group["name"],
            "user_count": User.objects.filter(group_id=group["id"]).count(),
            "updated_at": group["updated_at"].strftime("%Y-%m-%d")
        })

    return JsonResponse({"groups": response})

#  Group Users Page

def group_users(request, group_id):
    """
    Display the list of users in a specific group.
    """
    group = get_object_or_404(Group, id=group_id)
    users = User.objects.filter(group=group)
    return render(request, "group_users.html", {"group": group, "users": users})


# Delete Group
@csrf_exempt
def delete_group(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
        group.delete()
        return JsonResponse({'message': 'Group deleted successfully!'}, status=200)
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Group not found!'}, status=404)


# Delete User
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    """
    Deletes a user from a group.
    """
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return JsonResponse({'message': 'User deleted successfully!'}, status=200)


# UI Tables View

def ui_tables(request):
    groups = Group.objects.all()
    return render(request, 'home/ui-tables.html', {'groups': groups})


# Bulk Import Users
@csrf_exempt
@require_http_methods(["POST"])
def bulk_import(request):
    if 'csvupload' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    file = request.FILES['csvupload']
    group_id = request.POST.get("group_id")

    if not group_id:
        return JsonResponse({'error': 'Group ID is required'}, status=400)

    group = get_object_or_404(Group, id=group_id)

    try:
        reader = csv.DictReader(file.read().decode('utf-8').splitlines())

        for row in reader:
            # Ensure that the required fields are available in each row
            if not all(key in row for key in ['first_name', 'last_name', 'email', 'position']):
                return JsonResponse({'error': 'Missing required fields in the CSV'}, status=400)

            # Create new user
            User.objects.create(
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                position=row["position"],
                group=group
            )

        return JsonResponse({'message': 'Users imported successfully!'})

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)


# create_user

def create_user(request):
    if request.method == 'POST':
        # Your logic for creating the user goes here
        # For example, using request.POST to get data and save it to the database
        email = request.POST.get('email')
        name = request.POST.get('name')

        # Check if email exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already in use.'}, status=400)
        
        # Create a new user if the email doesn't exist
        user = User.objects.create(email=email, name=name)
        return JsonResponse({'status': 'success', 'message': 'User created successfully', 'user_id': user.id})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)



def assign_user_to_group(request):
    # Add logic for assigning users to a group
    return JsonResponse({'message': 'User assigned to group successfully!'})


def group_view(request):
    groups = Group.objects.all()  # Fetch all groups from the database
    return render(request, 'home/ui-tables.html', {'groups': groups})  # Pass to template

# Edit Group
@csrf_exempt
def edit_group(request, group_id):
    """
    If it's a GET request, return the current group details.
    If it's a POST request, update the group with new data.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            group_name = data.get('group_name')

            # Fetch the group and update it
            group = Group.objects.get(id=group_id)
            group.name = group_name
            group.save()

            return JsonResponse({'message': 'Group updated successfully!'}, status=200)
        except Group.DoesNotExist:
            return JsonResponse({'error': 'Group not found!'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        # If it's not a POST request, return the current group details
        group = get_object_or_404(Group, id=group_id)
        group_data = {
            'name': group.name,
            'updated_at': group.updated_at.strftime("%Y-%m-%d"),
        }
        return JsonResponse({'group': group_data})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    """
    Deletes a user from a group.
    """
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({'message': 'User deleted successfully!'}, status=200)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found!'}, status=404)


@csrf_exempt
def save_email_template(request):
    if request.method == 'POST':
        try:
            # Parse the incoming data from the request body
            data = json.loads(request.body)

            # Log the data for debugging
            print(data)

            # Use default values for optional fields if they are missing
            name = data.get('name', '')  # Default to empty string if 'name' is missing
            envelope_sender = data.get('envelope_sender', '')  # Default to empty string if 'envelope_sender' is missing
            subject = data.get('subject', '')  # Default to empty string if 'subject' is missing
            use_tracker = data.get('use_tracker', False)  # Default to False if 'use_tracker' is missing
            text_content = data.get('text_content', '')  # Default to empty string if 'text_content' is missing
            html_content = data.get('html_content', '')  # Default to empty string if 'html_content' is missing

            # Save the template to the database
            template = EmailTemplate(
                name=name,
                envelope_sender=envelope_sender,
                subject=subject,
                use_tracker=use_tracker,
                text_content=text_content,
                html_content=html_content
            )
            template.save()

            return JsonResponse({"status": "success", "message": "Template saved successfully!"}, status=201)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)


def home_page(request):
    if request.method == 'GET':
        # Fetch all email templates from the database
        templates = EmailTemplate.objects.all()
        
        # Prepare the data for rendering
        template_data = [
            {
                "name": template.name,
                "envelope_sender": template.envelope_sender,
                "subject": template.subject,
                "use_tracker": template.use_tracker,
                "text_content": template.text_content,
                "html_content": template.html_content,
            }
            for template in templates
        ]

        return render(request, 'home/home.html', {'templates': template_data})


def fetch_email_templates(request):
    if request.method == 'GET':
        # Fetch all email templates from the database
        templates = EmailTemplate.objects.all()

        # Prepare the data for the response
        template_data = [
            {
                "id": template.id,
                "name": template.name,
                "envelope_sender": template.envelope_sender,
                "subject": template.subject,
                "use_tracker": template.use_tracker,
                "text_content": template.text_content,
                "html_content": template.html_content,
            }
            for template in templates
        ]

        # Return the data as JSON
        return JsonResponse({"templates": template_data})
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_template(request, template_id):
    if request.method == 'DELETE':
        try:
            # Fetch the template from the database by its ID
            template = EmailTemplate.objects.get(id=template_id)
            
            # Delete the template
            template.delete()

            # Return a success message
            return JsonResponse({'message': 'Template deleted successfully'}, status=200)

        except EmailTemplate.DoesNotExist:
            # Return an error if the template does not exist
            return JsonResponse({'error': 'Template not found'}, status=404)

    else:
        # Return an error if the request method is not DELETE
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def edit_template(request, template_id):
    if request.method == 'POST':
        try:
            # Parse the incoming data from the request body
            data = json.loads(request.body)

            # Fetch the template by its ID
            template = EmailTemplate.objects.get(id=template_id)

            # Update the fields with the new data from the request
            template.name = data.get('name', template.name)  # Default to current value if not provided
            template.envelope_sender = data.get('envelope_sender', template.envelope_sender)
            template.subject = data.get('subject', template.subject)
            template.use_tracker = data.get('use_tracker', template.use_tracker)
            template.text_content = data.get('text_content', template.text_content)
            template.html_content = data.get('html_content', template.html_content)

            # Save the updated template
            template.save()

            return JsonResponse({'message': 'Template updated successfully!'}, status=200)

        except EmailTemplate.DoesNotExist:
            # Return an error if the template does not exist
            return JsonResponse({'error': 'Template not found'}, status=404)

        except Exception as e:
            # Return a generic error if something else goes wrong
            return JsonResponse({'error': str(e)}, status=400)
    else:
        # Return an error if the request method is not POST
        return JsonResponse({'error': 'Invalid request method'}, status=400)
        