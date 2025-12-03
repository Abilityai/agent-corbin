#!/usr/bin/env python3
"""
Process email batch data from MCP retrieval
"""
import json
import re
from pathlib import Path
from collections import Counter
from datetime import datetime

# Email data collected from MCP batch retrieval
emails_data = [
    {"from": "ADWEEK AI, Tech & Money Newsletter <edit@e.adweek.com>", "subject": "Amazon's New Power Play"},
    {"from": "Gamma <invoice+statements+acct_1MS6sAE3HBB5yrHt@stripe.com>", "subject": "Your receipt from Gamma"},
    {"from": "Suriya Ganesh <suriya@turnuptalent.ai>", "subject": "Is AI Agent Reliability a problem you're solving?"},
    {"from": "Alana Kahan <alana.kahan@1706advisorsclarityplan.com>", "subject": "quick question on benefits costs"},
    {"from": "Curt Gooden <curtgooden@ceocoaching.com>", "subject": "Eugene and Curt Gooden"},
    {"from": "Curt Gooden <curtgooden@ceocoaching.com>", "subject": "Re: INTRO: AI SaaS Coach Platform Project Leader"},
    {"from": "Deepak Shukla <d.shukla@thepearllemongroupuk.com>", "subject": "Sharing our experience Ability ai"},
    {"from": "Polina from Fibery <polina@fibery.io>", "subject": "See Fibery's October updates"},
    {"from": "Jon Zemmelman <jon@aifund.ai>", "subject": "Updated invitation: Eugene Vyborov and Jon Zemmelman"},
    {"from": "Jon Zemmelman <jon@aifund.ai>", "subject": "Invitation: Eugene Vyborov and Jon Zemmelman"},
    {"from": "Jay L <jay@rapidlendfinance.com>", "subject": "Re: Eugene, question about Ability.ai"},
    {"from": "Sara Torabi <s.torabi@pnptc.com>", "subject": "Plug and Play - Invitation for Smart Tech Pitch Session"},
    {"from": "Rohan Agrawal <rohan.agrawal.ceo@conciergeaiworks.com>", "subject": "your website called — it wants better answers"},
    {"from": "Rohan Agrawal <rohan.agrawal.ceo@conciergeaiworks.com>", "subject": "See Concierge live on Ability.ai's site"},
    {"from": "Sviat Sviatnenko <sviat.sviatnenko@endeavor.org>", "subject": "[Invitation] Endeavor Ukraine celebrates anniversary in NYC"},
    {"from": "Leo Bosuener <leo.b@atsocalgrwth.com>", "subject": "Re: Ability.ai on Product Hunt?"},
    {"from": "Adam Gilbert <a.gilbert@viewenginemail.com>", "subject": "Rev Share Partnership"},
    {"from": "Valeriy Grabko <valeriy.grabko@gmail.com>", "subject": "Accepted: Catch UP"},
    {"from": "Valeriy Grabko <valeriy.grabko@gmail.com>", "subject": "Accepted: Catch UP"},
    {"from": "Andrii Oliiarnyk via Docusign <dse_NA3@docusign.net>", "subject": "Complete with Docusign"},
    {"from": "Natalia Gaydukova <Natalia@now-for-women.com>", "subject": "Re: W1 AI Agent Ready for Testing"},
    {"from": "Natalia Gaydukova <Natalia@now-for-women.com>", "subject": "Re: W1 AI Agent Ready for Testing"},
    {"from": "Natalia Gaydukova <Natalia@now-for-women.com>", "subject": "Re: W1 AI Agent Ready for Testing"},
    {"from": "Vinodh Boopalan <vinodh.b@taramstech.com>", "subject": "Build Update"},
    {"from": "Shaan Mukhtar <shaan@anyscale.com>", "subject": "Re: Finish Ray Summit registration"},
    {"from": "Shaan Mukhtar <shaan@anyscale.com>", "subject": "Finish Ray Summit registration with 75% off"},
    {"from": "Victoria Loskutova <vic.loskutova@gmail.com>", "subject": "Accepted: Victoria Loskutova and Eugene Vyborov"},
    {"from": "William Salcido <william@bedrockanalytics.com>", "subject": "Accepted: Will Salcido and Eugene Vyborov"},
    {"from": "Mitch DeForest <m.deforest@ability.ai>", "subject": "Re: Response to Business Model Discussion"},
    {"from": "Mitch DeForest <m.deforest@ability.ai>", "subject": "Re: Response to Business Model Discussion"},
    {"from": "Mitch DeForest <m.deforest@ability.ai>", "subject": "Re: Intro - Ability"},
    {"from": "Mitch DeForest <m.deforest@ability.ai>", "subject": "Re: hatchworks"},
    {"from": "Mitch DeForest <m.deforest@ability.ai>", "subject": "Re: hatchworks"},
    {"from": "Oleksander Korin <o.korin@ability.ai>", "subject": "Declined: Discuss Engineering"},
    {"from": "Oleksander Korin <o.korin@ability.ai>", "subject": "Accepted: Discuss Engineering"},
    {"from": "Oleksii Dolhov <o.dolhov@ability.ai>", "subject": "Accepted: Intelligence Design Weekly"},
    {"from": "Ian Robertson <ian.robertson@anyscale.com>", "subject": "Ray Summit Discount"},
    {"from": "Josh gyau <joshgyau@system3solutions.com>", "subject": "Eugene, question"},
    {"from": "Ava Lee <ava.l@storygen-content.com>", "subject": "Re: pay per meeting business dev, Eugene"},
    {"from": "Andrew Jackson <andrew@aeroforge.org>", "subject": "podcast guesting for Eugene"},
    {"from": "Lee Chapman <leechapman@funnelbuildermarket.org>", "subject": "Eugene, can I run something by you?"},
    {"from": "Shany Rimon <shanyrim@gmail.com>", "subject": "Accepted: Shany Rimon and Eugene Vyborov"},
    {"from": "Lexi Kaz <lexi@elevate-ak-infinite.com>", "subject": "Re: October Feature Offer"},
    {"from": "Devin Shrake <devin@appbound.io>", "subject": "Accepted: Devin Shrake and Eugene Vyborov"},
    {"from": "Emma Williams <emma.williams@deepinstantlyaibot.com>", "subject": "outbound + AI Agent Systems"},
    {"from": "Anthony Venus <antvenus1@gmail.com>", "subject": "Re: hatchworks"},
]

# Automated email filters
automated_keywords = {
    'noreply', 'no-reply', 'donotreply', 'notifications', 'automated', 'system',
    'bounce', 'mailer-daemon', 'support', 'help', 'info', 'hello', 'team',
    'mail.beehiiv.com', 'substack.com', 'calendly.com', 'linkedin.com',
    'facebook.com', 'twitter.com', 'calendar.google.com', 'e.read.ai',
    'stripe.com', 'mercury.com', 'docusign', 'luma-mail.com', 'skool.com',
    'invoice', 'billing', 'receipt', 'notification'
}

def is_automated(email, name=""):
    email_lower = email.lower()
    name_lower = name.lower()

    for keyword in automated_keywords:
        if keyword in email_lower or keyword in name_lower:
            return True

    # Check for internal Ability.ai emails
    if '@ability.ai' in email_lower:
        return True

    return False

def extract_email_and_name(from_field):
    """Extract email and name from 'Name <email>' format"""
    email_match = re.search(r'<(.+?)>', from_field)
    if email_match:
        email = email_match.group(1).strip()
        name = from_field[:from_field.index('<')].strip().strip('"')
    else:
        email = from_field.strip()
        name = ""
    return email, name

# Process emails
collaborators = {}
for email_data in emails_data:
    from_field = email_data['from']
    subject = email_data['subject']

    email, name = extract_email_and_name(from_field)

    # Skip automated emails
    if is_automated(email, name):
        continue

    # Track collaborator
    if email not in collaborators:
        collaborators[email] = {
            'name': name,
            'count': 0,
            'subjects': []
        }

    collaborators[email]['count'] += 1
    if len(collaborators[email]['subjects']) < 3:
        collaborators[email]['subjects'].append(subject)

# Filter by minimum 2 messages
collaborators = {
    email: data for email, data in collaborators.items()
    if data['count'] >= 2
}

print(f"Found {len(collaborators)} collaboration partners (2+ messages)")
print("\n" + "="*80)
for email, data in sorted(collaborators.items(), key=lambda x: x[1]['count'], reverse=True):
    print(f"{data['name']} <{email}> - {data['count']} messages")
    for subj in data['subjects'][:2]:
        print(f"  • {subj}")
    print()

# Load existing linkedin contacts
linkedin_dir = Path('/Users/eugene/Dropbox/Coding/N8N_Main_repos/Corbin20/linkedin_contacts')
existing_emails = set()

print("="*80)
print("Loading existing contact database...")
for file_path in linkedin_dir.glob("*.json"):
    if file_path.name == "schema.json":
        continue

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Check google_contact emails
            google_contact = data.get('google_contact', {})
            if google_contact:
                for em in google_contact.get('emails', []):
                    existing_emails.add(em.lower())

            # Check Apollo emails
            apollo = data.get('apollo_enrichment', {})
            person_data = apollo.get('person_data', {})
            if person_data and isinstance(person_data, dict):
                em = person_data.get('email')
                if em:
                    existing_emails.add(em.lower())
    except:
        pass

print(f"Loaded {len(existing_emails)} existing contact emails")

# Identify new contacts
new_contacts = []
for email, data in collaborators.items():
    if email.lower() not in existing_emails:
        new_contacts.append({
            'email': email,
            'name': data['name'],
            'message_count': data['count'],
            'subjects': data['subjects']
        })

print(f"\n{len(new_contacts)} NEW contacts to add:\n")
for contact in sorted(new_contacts, key=lambda x: x['message_count'], reverse=True):
    print(f"  {contact['name']} <{contact['email']}> - {contact['message_count']} messages")

# Generate report
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
report_path = Path(f'/Users/eugene/Dropbox/Coding/N8N_Main_repos/Corbin20/email_enrichment_report_{timestamp}.json')

report = {
    'generated_at': datetime.now().isoformat(),
    'total_collaborators': len(collaborators),
    'existing_in_database': len(collaborators) - len(new_contacts),
    'new_contacts': new_contacts,
    'all_collaborators': collaborators
}

with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n{'='*80}")
print(f"Report saved: {report_path}")
print(f"{'='*80}")
