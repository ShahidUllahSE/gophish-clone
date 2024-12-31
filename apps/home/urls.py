from django.urls import path
from apps.home import views  # Import views from the home app
from . import views
from .views import send_email,delete_template,edit_template

urlpatterns = [
    # Root route for the dashboard
    path('', views.index, name='home'),  

    # Serve landing-pages.html at /landing-pages/ and /landing-pages.html
    path('landing-pages/', views.landing_pages, name='landing_pages'),
    path('landing-pages.html', views.landing_pages, name='landing_pages_html'),

    # Email functionality route
    path('send_email/', views.send_email, name='send_email'),

    # Save, Edit, Delete and Preview Landing Page
    path('save_landing_page/', views.save_landing_page, name='save_landing_page'),
    path('edit_landing_page/<int:page_id>/', views.edit_landing_page, name='edit_landing_page'),
    path('delete_landing_page/<int:page_id>/', views.delete_landing_page, name='delete_landing_page'),
    path('preview_landing_page/<int:page_id>/', views.preview_landing_page, name='preview_landing_page'),

    # Capture form submission
    path('capture_submission/<int:page_id>/', views.capture_submission, name='capture_submission'),

    # Campaign and Page user routes
    path('campaign-user/', views.campaign_user, name='campaign_user'),
    path('campaign-user.html', views.campaign_user, name='campaign_user_html'),
    path('page-user/', views.page_user, name='page_user'),
    path('page-user.html', views.page_user, name='page_user_html'),

    # UI routes
    path('ui-tables/', views.ui_tables, name='ui_tables'),
    path('ui-tables.html', views.ui_tables, name='ui_tables_html'),
    path('ui-typography/', views.ui_typography, name='ui_typography'),
    path('ui-typography.html', views.ui_typography, name='ui_typography_html'),
    path('ui-icons/', views.ui_icons, name='ui_icons'),
    path('ui-icons.html', views.ui_icons, name='ui_icons_html'),
    path('ui-maps/', views.ui_maps, name='ui_maps'),
    path('ui-maps.html', views.ui_maps, name='ui_maps_html'),
    path('ui-notifications/', views.ui_notifications, name='ui_notifications'),
    path('ui-notifications.html', views.ui_notifications, name='ui_notifications_html'),

    # Additional functionality routes
    path('email-collection/<int:page_id>/', views.email_collection, name='email_collection'),  # Collect emails from a page
    path('analytics/<int:page_id>/', views.analytics_report, name='analytics_report'),  # View analytics report for a page
    path('geolocation/<int:page_id>/', views.geolocation_tracking, name='geolocation_tracking'),  # Geolocation tracking functionality

    # Import site and preview imported site routes
    path('import_site/', views.import_site, name='import_site'),
    path('preview_imported_site/', views.preview_imported_site, name='preview_imported_site'),
    path('logout/', views.logout_user, name='logout_user'),
    path('assign-group/', views.assign_user_to_group, name='assign_user_to_group'),
    path('login/', views.login_user, name='login_user'),
    path('register/', views.register_user, name='register_user'),
    path("save_group_data/", views.save_group_data, name="save_group_data"),
    path("fetch_groups/", views.fetch_groups, name="fetch_groups"),
    path("group/<int:group_id>/users/", views.group_users, name="group_users"),
    path("save-group/", views.save_group_data, name="save_group"),
    path('create-user/', views.create_user, name='create_user'),
     path('group-details/<int:group_id>/', views.edit_group, name='edit_group'),
    path('delete-group/<int:group_id>/', views.delete_group, name='delete_group'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    #  path('assign-group/', views.assign_user_to_group, name='assign_user_to_group'),
    
    
    # Path to save an email template
    path('save_email_template/', views.save_email_template, name='save_email_template'),
    
    # Path to fetch email templates (newly added)
    path('api/fetch_templates/', views.fetch_email_templates, name='fetch_email_templates'),

    path('api/delete_template/<int:template_id>/', delete_template),

    path('edit-template/<int:template_id>/', edit_template, name='edit_template'),

    
]
