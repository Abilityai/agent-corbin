#!/usr/bin/env python3
"""
Apollo Campaign Manager
Comprehensive campaign and sequence management for Apollo.io
"""

import os
import sys
import json
import argparse
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in skill directory
skill_dir = Path(__file__).parent
env_path = skill_dir / '.env'
if env_path.exists():
    load_dotenv(env_path)


class ApolloAPIError(Exception):
    """Custom exception for Apollo API errors"""
    pass


class ApolloCampaignManager:
    """Manager for Apollo.io campaign and sequence operations"""

    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize Apollo Campaign Manager

        Args:
            api_key: Apollo Master API key (reads from env if not provided)
            base_url: Apollo API base URL (reads from env if not provided)
        """
        self.api_key = api_key or os.getenv('APOLLO_API_KEY')
        self.base_url = base_url or os.getenv('APOLLO_BASE_URL', 'https://api.apollo.io/api/v1')

        if not self.api_key:
            raise ApolloAPIError("Apollo API key not found. Set APOLLO_API_KEY environment variable.")

        self.headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'X-Api-Key': self.api_key
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to Apollo API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON data

        Raises:
            ApolloAPIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Headers already include Authorization with Bearer token
        # No need to add api_key to params or body

        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise ApolloAPIError(
                    "403 Forbidden: Master API key required. "
                    "Ensure you're using a Master API key, not a regular API key."
                )
            elif e.response.status_code == 404:
                raise ApolloAPIError(f"404 Not Found: {endpoint}")
            else:
                raise ApolloAPIError(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            raise ApolloAPIError(f"Network error: {e}")

    # ==================== Sequence Operations ====================

    def search_sequences(self, query: str = None, page: int = 1) -> Dict[str, Any]:
        """
        Search for sequences in Apollo account

        Args:
            query: Optional search query to filter sequences
            page: Page number for pagination (default: 1)

        Returns:
            Dictionary containing sequences data
        """
        payload = {'page': page}
        if query:
            payload['q'] = query

        return self._make_request('POST', 'emailer_campaigns/search', json=payload)

    def add_contacts_to_sequence(
        self,
        sequence_id: str,
        contact_ids: List[str],
        mailbox_id: str = None,
        send_email_from_user_id: str = None
    ) -> Dict[str, Any]:
        """
        Add contacts to a sequence

        Args:
            sequence_id: ID of the sequence
            contact_ids: List of contact IDs to add
            mailbox_id: Optional email account ID to send from
            send_email_from_user_id: Optional user ID to send emails from

        Returns:
            API response with operation results
        """
        payload = {
            'contact_ids': contact_ids,
            'emailer_campaign_id': sequence_id
        }

        if mailbox_id:
            payload['mailbox_id'] = mailbox_id
        if send_email_from_user_id:
            payload['send_email_from_user_id'] = send_email_from_user_id

        endpoint = f'emailer_campaigns/{sequence_id}/add_contact_ids'
        return self._make_request('POST', endpoint, json=payload)

    def update_contact_status_in_sequence(
        self,
        sequence_id: str,
        contact_ids: List[str],
        action: str = 'finish'
    ) -> Dict[str, Any]:
        """
        Update contact status in a sequence (finish or remove)

        Args:
            sequence_id: ID of the sequence
            contact_ids: List of contact IDs to update
            action: 'finish' to mark as complete, 'remove' to remove entirely

        Returns:
            API response with operation results
        """
        payload = {
            'emailer_campaign_id': sequence_id,
            'contact_ids': contact_ids,
            'status': action
        }

        return self._make_request('POST', 'emailer_campaigns/remove_or_stop_contact_ids', json=payload)

    # ==================== Email Account Operations ====================

    def list_email_accounts(self) -> Dict[str, Any]:
        """
        List all email accounts/mailboxes in Apollo account

        Returns:
            Dictionary containing email accounts data
        """
        return self._make_request('GET', 'email_accounts')

    # ==================== People Search Operations ====================

    def search_people(
        self,
        query: str = None,
        person_titles: List[str] = None,
        person_locations: List[str] = None,
        person_seniorities: List[str] = None,
        organization_ids: List[str] = None,
        page: int = 1,
        per_page: int = 25
    ) -> Dict[str, Any]:
        """
        Search for people in Apollo's database

        Args:
            query: General search query
            person_titles: List of job titles to filter by
            person_locations: List of locations to filter by
            person_seniorities: List of seniority levels (e.g., ['senior', 'manager'])
            organization_ids: List of organization IDs to filter by
            page: Page number (default: 1)
            per_page: Results per page (default: 25, max: 100)

        Returns:
            Dictionary containing people search results
        """
        payload = {
            'page': page,
            'per_page': min(per_page, 100)
        }

        if query:
            payload['q_keywords'] = query
        if person_titles:
            payload['person_titles'] = person_titles
        if person_locations:
            payload['person_locations'] = person_locations
        if person_seniorities:
            payload['person_seniorities'] = person_seniorities
        if organization_ids:
            payload['organization_ids'] = organization_ids

        return self._make_request('POST', 'mixed_people/search', json=payload)

    def enrich_person(
        self,
        email: str = None,
        first_name: str = None,
        last_name: str = None,
        organization_name: str = None,
        domain: str = None
    ) -> Dict[str, Any]:
        """
        Enrich a person's information

        Args:
            email: Person's email address
            first_name: Person's first name
            last_name: Person's last name
            organization_name: Name of their organization
            domain: Domain of their organization

        Returns:
            Dictionary containing enriched person data
        """
        payload = {}

        if email:
            payload['email'] = email
        if first_name:
            payload['first_name'] = first_name
        if last_name:
            payload['last_name'] = last_name
        if organization_name:
            payload['organization_name'] = organization_name
        if domain:
            payload['domain'] = domain

        return self._make_request('POST', 'people/match', json=payload)

    # ==================== Company Search Operations ====================

    def search_companies(
        self,
        query: str = None,
        organization_locations: List[str] = None,
        organization_num_employees_ranges: List[str] = None,
        industry_tag_ids: List[str] = None,
        page: int = 1,
        per_page: int = 25
    ) -> Dict[str, Any]:
        """
        Search for companies in Apollo's database

        Args:
            query: General search query
            organization_locations: List of locations to filter by
            organization_num_employees_ranges: Employee count ranges (e.g., ['1,10', '11,50'])
            industry_tag_ids: List of industry tag IDs
            page: Page number (default: 1)
            per_page: Results per page (default: 25, max: 100)

        Returns:
            Dictionary containing company search results
        """
        payload = {
            'page': page,
            'per_page': min(per_page, 100)
        }

        if query:
            payload['q_organization_keyword_tags'] = [query]
        if organization_locations:
            payload['organization_locations'] = organization_locations
        if organization_num_employees_ranges:
            payload['organization_num_employees_ranges'] = organization_num_employees_ranges
        if industry_tag_ids:
            payload['q_organization_industry_tag_ids'] = industry_tag_ids

        return self._make_request('POST', 'mixed_companies/search', json=payload)

    def enrich_company(
        self,
        domain: str = None,
        organization_name: str = None
    ) -> Dict[str, Any]:
        """
        Enrich a company's information

        Args:
            domain: Company domain (e.g., 'google.com')
            organization_name: Company name

        Returns:
            Dictionary containing enriched company data
        """
        params = {}

        if domain:
            params['domain'] = domain
        if organization_name:
            params['name'] = organization_name

        return self._make_request('GET', 'organizations/enrich', params=params)

    # ==================== Email Operations ====================

    def search_outreach_emails(
        self,
        sequence_id: str = None,
        date_from: str = None,
        date_to: str = None,
        page: int = 1,
        per_page: int = 100
    ) -> Dict[str, Any]:
        """
        Search for outreach emails sent through sequences

        Args:
            sequence_id: Optional sequence ID to filter by
            date_from: Optional start date (YYYY-MM-DD)
            date_to: Optional end date (YYYY-MM-DD)
            page: Page number (default: 1)
            per_page: Results per page (default: 100, max: 100)

        Returns:
            Dictionary containing email search results
        """
        params = {
            'page': page,
            'per_page': min(per_page, 100)
        }

        if sequence_id:
            params['emailer_campaign_ids[]'] = sequence_id
        if date_from:
            params['sent_at_date_range[from]'] = date_from
        if date_to:
            params['sent_at_date_range[to]'] = date_to

        return self._make_request('GET', 'emailer_messages/search', params=params)

    def get_email_statistics(self, email_id: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific outreach email

        Args:
            email_id: ID of the email message

        Returns:
            Dictionary containing email statistics (opens, clicks, etc.)
        """
        return self._make_request('GET', f'emailer_messages/{email_id}/activities')

    # ==================== Helper Methods ====================

    def format_sequences(self, sequences_data: Dict[str, Any]) -> str:
        """Format sequences data for display"""
        if 'emailer_campaigns' not in sequences_data:
            return "No sequences found"

        sequences = sequences_data['emailer_campaigns']
        if not sequences:
            return "No sequences found"

        output = [f"\n{'='*80}"]
        output.append(f"Found {len(sequences)} sequence(s)")
        output.append(f"{'='*80}\n")

        for seq in sequences:
            output.append(f"ID: {seq.get('id', 'N/A')}")
            output.append(f"Name: {seq.get('name', 'N/A')}")
            output.append(f"Active: {seq.get('active', 'N/A')}")

            # Stats if available
            if 'num_steps' in seq:
                output.append(f"Steps: {seq['num_steps']}")
            if 'num_contacted' in seq:
                output.append(f"Contacted: {seq['num_contacted']}")
            if 'num_bounced' in seq:
                output.append(f"Bounced: {seq['num_bounced']}")
            if 'num_replied' in seq:
                output.append(f"Replied: {seq['num_replied']}")

            output.append(f"{'-'*80}\n")

        return "\n".join(output)

    def format_email_accounts(self, accounts_data: Dict[str, Any]) -> str:
        """Format email accounts data for display"""
        if 'email_accounts' not in accounts_data:
            return "No email accounts found"

        accounts = accounts_data['email_accounts']
        if not accounts:
            return "No email accounts found"

        output = [f"\n{'='*80}"]
        output.append(f"Found {len(accounts)} email account(s)")
        output.append(f"{'='*80}\n")

        for account in accounts:
            output.append(f"ID: {account.get('id', 'N/A')}")
            output.append(f"Email: {account.get('email', 'N/A')}")
            output.append(f"Active: {account.get('active', 'N/A')}")
            output.append(f"Type: {account.get('type', 'N/A')}")
            output.append(f"{'-'*80}\n")

        return "\n".join(output)

    def format_emails(self, emails_data: Dict[str, Any]) -> str:
        """Format outreach emails data for display"""
        if 'emailer_messages' not in emails_data:
            return "No emails found"

        emails = emails_data['emailer_messages']
        if not emails:
            return "No emails found"

        output = [f"\n{'='*80}"]
        output.append(f"Found {len(emails)} email(s)")
        output.append(f"{'='*80}\n")

        for email in emails:
            output.append(f"ID: {email.get('id', 'N/A')}")
            output.append(f"Subject: {email.get('subject', 'N/A')}")
            output.append(f"To: {email.get('to', 'N/A')}")
            output.append(f"Sent At: {email.get('sent_at', 'N/A')}")
            output.append(f"Status: {email.get('status', 'N/A')}")

            # Stats if available
            if 'opened_at' in email and email['opened_at']:
                output.append(f"Opened: Yes")
            if 'clicked_at' in email and email['clicked_at']:
                output.append(f"Clicked: Yes")
            if 'replied_at' in email and email['replied_at']:
                output.append(f"Replied: Yes")

            output.append(f"{'-'*80}\n")

        return "\n".join(output)

    def format_email_stats(self, stats_data: Dict[str, Any]) -> str:
        """Format email statistics for display"""
        output = [f"\n{'='*80}"]
        output.append("Email Statistics")
        output.append(f"{'='*80}\n")

        if 'emailer_message' in stats_data:
            msg = stats_data['emailer_message']
            output.append(f"Subject: {msg.get('subject', 'N/A')}")
            output.append(f"To: {msg.get('to', 'N/A')}")
            output.append(f"Sent At: {msg.get('sent_at', 'N/A')}")
            output.append(f"\n{'-'*80}\n")

        if 'activities' in stats_data:
            activities = stats_data['activities']
            output.append(f"Total Activities: {len(activities)}\n")

            for activity in activities:
                output.append(f"Type: {activity.get('activity_type', 'N/A')}")
                output.append(f"At: {activity.get('created_at', 'N/A')}")
                if 'link' in activity:
                    output.append(f"Link: {activity['link']}")
                output.append("")

        return "\n".join(output)

    def format_people(self, people_data: Dict[str, Any]) -> str:
        """Format people search results for display"""
        if 'people' not in people_data:
            return "No people found"

        people = people_data['people']
        if not people:
            return "No people found"

        output = [f"\n{'='*80}"]
        output.append(f"Found {len(people)} person(people)")
        output.append(f"{'='*80}\n")

        for person in people:
            output.append(f"ID: {person.get('id', 'N/A')}")
            output.append(f"Name: {person.get('first_name', '')} {person.get('last_name', '')}")
            output.append(f"Title: {person.get('title', 'N/A')}")
            output.append(f"Email: {person.get('email', 'N/A')}")

            if 'organization' in person and person['organization']:
                org = person['organization']
                output.append(f"Company: {org.get('name', 'N/A')}")

            output.append(f"LinkedIn: {person.get('linkedin_url', 'N/A')}")
            output.append(f"{'-'*80}\n")

        return "\n".join(output)

    def format_companies(self, companies_data: Dict[str, Any]) -> str:
        """Format company search results for display"""
        if 'organizations' not in companies_data:
            return "No companies found"

        companies = companies_data['organizations']
        if not companies:
            return "No companies found"

        output = [f"\n{'='*80}"]
        output.append(f"Found {len(companies)} compan{'y' if len(companies) == 1 else 'ies'}")
        output.append(f"{'='*80}\n")

        for company in companies:
            output.append(f"ID: {company.get('id', 'N/A')}")
            output.append(f"Name: {company.get('name', 'N/A')}")
            output.append(f"Domain: {company.get('primary_domain', 'N/A')}")
            output.append(f"Industry: {company.get('industry', 'N/A')}")
            output.append(f"Employees: {company.get('estimated_num_employees', 'N/A')}")
            output.append(f"Location: {company.get('city', '')}, {company.get('state', '')} {company.get('country', '')}")
            output.append(f"Website: {company.get('website_url', 'N/A')}")
            output.append(f"{'-'*80}\n")

        return "\n".join(output)


def main():
    """Command-line interface for Apollo Campaign Manager"""
    parser = argparse.ArgumentParser(
        description='Apollo Campaign Manager - Manage sequences and campaigns'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Search sequences
    search_seq = subparsers.add_parser('search-sequences', help='Search for sequences')
    search_seq.add_argument('--query', help='Search query')
    search_seq.add_argument('--page', type=int, default=1, help='Page number')

    # Add contacts to sequence
    add_contacts = subparsers.add_parser('add-to-sequence', help='Add contacts to sequence')
    add_contacts.add_argument('--sequence-id', required=True, help='Sequence ID')
    add_contacts.add_argument('--contact-ids', required=True, help='Comma-separated contact IDs')
    add_contacts.add_argument('--mailbox-id', help='Email account/mailbox ID')
    add_contacts.add_argument('--user-id', help='User ID to send from')

    # Update contact status
    update_status = subparsers.add_parser('update-status', help='Update contact status in sequence')
    update_status.add_argument('--sequence-id', required=True, help='Sequence ID')
    update_status.add_argument('--contact-ids', required=True, help='Comma-separated contact IDs')
    update_status.add_argument('--action', choices=['finish', 'remove'], default='finish',
                               help='Action: finish or remove')

    # List email accounts
    subparsers.add_parser('list-email-accounts', help='List email accounts')

    # Search emails
    search_emails = subparsers.add_parser('search-emails', help='Search outreach emails')
    search_emails.add_argument('--sequence-id', help='Filter by sequence ID')
    search_emails.add_argument('--date-from', help='Start date (YYYY-MM-DD)')
    search_emails.add_argument('--date-to', help='End date (YYYY-MM-DD)')
    search_emails.add_argument('--page', type=int, default=1, help='Page number')
    search_emails.add_argument('--per-page', type=int, default=100, help='Results per page')

    # Get email stats
    email_stats = subparsers.add_parser('email-stats', help='Get email statistics')
    email_stats.add_argument('--email-id', required=True, help='Email message ID')

    # Search people
    search_people = subparsers.add_parser('search-people', help='Search for people')
    search_people.add_argument('--query', help='Search query')
    search_people.add_argument('--titles', help='Comma-separated job titles')
    search_people.add_argument('--locations', help='Comma-separated locations')
    search_people.add_argument('--seniorities', help='Comma-separated seniority levels')
    search_people.add_argument('--page', type=int, default=1, help='Page number')
    search_people.add_argument('--per-page', type=int, default=25, help='Results per page')

    # Enrich person
    enrich_person = subparsers.add_parser('enrich-person', help='Enrich person information')
    enrich_person.add_argument('--email', help='Person email')
    enrich_person.add_argument('--first-name', help='Person first name')
    enrich_person.add_argument('--last-name', help='Person last name')
    enrich_person.add_argument('--organization', help='Organization name')
    enrich_person.add_argument('--domain', help='Organization domain')

    # Search companies
    search_companies = subparsers.add_parser('search-companies', help='Search for companies')
    search_companies.add_argument('--query', help='Search query')
    search_companies.add_argument('--locations', help='Comma-separated locations')
    search_companies.add_argument('--employee-ranges', help='Comma-separated employee ranges (e.g., "1,10" "11,50")')
    search_companies.add_argument('--page', type=int, default=1, help='Page number')
    search_companies.add_argument('--per-page', type=int, default=25, help='Results per page')

    # Enrich company
    enrich_company = subparsers.add_parser('enrich-company', help='Enrich company information')
    enrich_company.add_argument('--domain', help='Company domain')
    enrich_company.add_argument('--name', help='Company name')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        manager = ApolloCampaignManager()

        if args.command == 'search-sequences':
            result = manager.search_sequences(args.query, args.page)
            print(manager.format_sequences(result))

        elif args.command == 'add-to-sequence':
            contact_ids = [cid.strip() for cid in args.contact_ids.split(',')]
            result = manager.add_contacts_to_sequence(
                args.sequence_id,
                contact_ids,
                args.mailbox_id,
                args.user_id
            )
            print("\n✓ Successfully added contacts to sequence")
            print(json.dumps(result, indent=2))

        elif args.command == 'update-status':
            contact_ids = [cid.strip() for cid in args.contact_ids.split(',')]
            result = manager.update_contact_status_in_sequence(
                args.sequence_id,
                contact_ids,
                args.action
            )
            print(f"\n✓ Successfully {args.action}ed contacts in sequence")
            print(json.dumps(result, indent=2))

        elif args.command == 'list-email-accounts':
            result = manager.list_email_accounts()
            print(manager.format_email_accounts(result))

        elif args.command == 'search-emails':
            result = manager.search_outreach_emails(
                args.sequence_id,
                args.date_from,
                args.date_to,
                args.page,
                args.per_page
            )
            print(manager.format_emails(result))

        elif args.command == 'email-stats':
            result = manager.get_email_statistics(args.email_id)
            print(manager.format_email_stats(result))

        elif args.command == 'search-people':
            titles = [t.strip() for t in args.titles.split(',')] if args.titles else None
            locations = [l.strip() for l in args.locations.split(',')] if args.locations else None
            seniorities = [s.strip() for s in args.seniorities.split(',')] if args.seniorities else None

            result = manager.search_people(
                args.query,
                titles,
                locations,
                seniorities,
                None,
                args.page,
                args.per_page
            )
            print(manager.format_people(result))

        elif args.command == 'enrich-person':
            result = manager.enrich_person(
                args.email,
                args.first_name,
                args.last_name,
                args.organization,
                args.domain
            )
            print("\n✓ Person enrichment complete")
            print(json.dumps(result, indent=2))

        elif args.command == 'search-companies':
            locations = [l.strip() for l in args.locations.split(',')] if args.locations else None
            employee_ranges = [r.strip() for r in args.employee_ranges.split(' ')] if args.employee_ranges else None

            result = manager.search_companies(
                args.query,
                locations,
                employee_ranges,
                None,
                args.page,
                args.per_page
            )
            print(manager.format_companies(result))

        elif args.command == 'enrich-company':
            result = manager.enrich_company(
                args.domain,
                args.name
            )
            print("\n✓ Company enrichment complete")
            print(json.dumps(result, indent=2))

    except ApolloAPIError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
