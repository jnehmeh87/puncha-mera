import os
import django
import random
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puncha_mera.settings')
django.setup()

from django.utils import timezone
from accounts.models import Organization, Membership, Contact
from projects.models import Project
from time_entries.models import TimeEntry

def run():
    print("Generating comprehensive, multi-currency mock data for Advanced Analytics...")

    # Ensure there are some organizations with members
    orgs = Organization.objects.all()
    if not orgs.exists():
        print("No organizations found. Please run initial setup first.")
        return

    # Let's target the first org for rigorous testing
    target_org = orgs.first()
    print(f"Targeting Organization: {target_org.name}")

    # Create dummy clients (Contacts)
    client_names = ['Acme Corp (US)', 'TechNova (EU)', 'Nordic Tech (SE)', 'London Finance (UK)']
    clients = []
    for c_name in client_names:
        c, created = Contact.objects.get_or_create(
            name=c_name, 
            organization=target_org, 
            contact_type='Client',
            defaults={'company_email': f'contact@{c_name.split()[0].lower()}.com'}
        )
        clients.append(c)

    # Create projects with distinct currencies mapped to those clients
    project_configs = [
        {'name': 'Acme Web Redesign', 'client': clients[0], 'currency': 'USD', 'type': 'External'},
        {'name': 'TechNova Mobile App', 'client': clients[1], 'currency': 'EUR', 'type': 'External'},
        {'name': 'Nordic Database Migration', 'client': clients[2], 'currency': 'SEK', 'type': 'External'},
        {'name': 'UK Audit Dashboard', 'client': clients[3], 'currency': 'GBP', 'type': 'External'},
        {'name': 'Internal R&D', 'client': clients[0], 'currency': 'USD', 'type': 'Internal'},
    ]
    
    projects = []
    for cfg in project_configs:
        p, created = Project.objects.get_or_create(
            name=cfg['name'],
            organization=target_org,
            contact=cfg['client'],
            defaults={
                'currency': cfg['currency'],
            }
        )
        if not created:
            p.currency = cfg['currency'] # Ensure currency is right
            p.save()
        
        # We attach the 'type' directly to the object instance as a temporary attribute for the script
        p._script_type = cfg['type']
        projects.append(p)

    # Get all members of this org
    memberships = Membership.objects.filter(organization=target_org).select_related('user')
    users = [m.user for m in memberships]
    
    if not users:
        print("No users found in the target organization.")
        return

    print(f"Distributing time entries across {len(users)} users over the past 45 days...")

    # Clear old generated entries to keep the database fresh for the target org
    TimeEntry.objects.filter(project__in=projects).delete()

    now = timezone.now()
    total_entries_created = 0

    # Distribute entries
    for user in users:
        base_rate = random.choice([50, 75, 100, 150, 200])
        
        # Ensure user is a ProjectMember for all projects to configure rates properly
        for p in projects:
            is_billable = p._script_type == 'External'
            rate_multiplier = {'USD': 1.0, 'EUR': 0.9, 'SEK': 10.5, 'GBP': 0.8}.get(p.currency, 1.0)
            user_hourly_rate = round(base_rate * rate_multiplier * random.uniform(0.9, 1.2), 2) if is_billable else 0.00
            
            # Using get_or_create from projects.models import ProjectMember (need to import it at top)
            from projects.models import ProjectMember
            pm, pm_created = ProjectMember.objects.get_or_create(
                project=p,
                user=user,
                defaults={'hourly_rate': user_hourly_rate}
            )
            # Update rate just in case
            if not pm_created:
                pm.hourly_rate = user_hourly_rate
                pm.save()

        for days_back in range(45):
            date_of_entry = now.date() - datetime.timedelta(days=days_back)
            
            # Skip weekends (mostly)
            if date_of_entry.weekday() >= 5 and random.random() < 0.9:
                continue

            # 1 to 3 time entries per working day for each user
            for _ in range(random.randint(1, 3)):
                proj = random.choice(projects)
                
                # Randomize duration from 0.5 to 4.5 hours
                duration_hours = random.uniform(0.5, 4.5)
                
                # Create plausible start and end times
                start_hour = random.randint(8, 14)
                start_minute = random.choice([0, 15, 30, 45])
                start_time = datetime.time(hour=start_hour, minute=start_minute)
                
                # Calculate end time using timedelta on a dummy datetime
                dummy_start = datetime.datetime.combine(date_of_entry, start_time)
                dummy_end = dummy_start + datetime.timedelta(hours=duration_hours)
                end_time = dummy_end.time()

                TimeEntry.objects.create(
                    user=user,
                    project=proj,
                    organization=target_org,
                    title=f"Dev work on {proj.name}",
                    date=date_of_entry,
                    start_time=start_time,
                    end_time=end_time
                )
                total_entries_created += 1

    print(f"Successfully generated {total_entries_created} sophisticated time entries with diverse currencies and realistic distribution!")

if __name__ == '__main__':
    run()
