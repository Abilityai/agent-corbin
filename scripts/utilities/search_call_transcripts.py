#!/usr/bin/env python3
"""
Vertex AI Search - Call Transcripts Query Tool
Provides semantic search over call transcripts stored in Google Drive
"""

import json
import subprocess
import sys
import argparse
from typing import Dict, List

def get_access_token() -> str:
    """Get Google Cloud access token using gcloud CLI"""
    result = subprocess.run(
        ['gcloud', 'auth', 'print-access-token'],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()

def search_transcripts(query: str, page_size: int = 10) -> Dict:
    """Search call transcripts using Vertex AI Search API"""
    endpoint = (
        "https://discoveryengine.googleapis.com/v1alpha/projects/664255702042/"
        "locations/global/collections/default_collection/engines/"
        "transcript-rag_1762512457762/servingConfigs/default_search:search"
    )

    access_token = get_access_token()

    payload = {
        "query": query,
        "pageSize": page_size,
        "queryExpansionSpec": {"condition": "AUTO"},
        "spellCorrectionSpec": {"mode": "AUTO"},
        "languageCode": "en-US",
        "contentSearchSpec": {
            "extractiveContentSpec": {"maxExtractiveAnswerCount": 1}
        },
        "userInfo": {"timeZone": "Europe/Lisbon"}
    }

    result = subprocess.run(
        [
            'curl', '-s', '-X', 'POST',
            '-H', f'Authorization: Bearer {access_token}',
            '-H', 'Content-Type: application/json',
            endpoint,
            '-d', json.dumps(payload)
        ],
        capture_output=True,
        text=True,
        check=True
    )

    return json.loads(result.stdout)

def format_results(response: Dict, verbose: bool = False) -> str:
    """Format search results for display"""
    output = []

    if 'results' not in response or not response['results']:
        return "No results found."

    output.append(f"\n{'='*80}")
    output.append(f"Found {response.get('totalSize', 0)} results")
    output.append(f"{'='*80}\n")

    for idx, result in enumerate(response['results'], 1):
        doc = result['document']['derivedStructData']

        output.append(f"[{idx}] {doc.get('title', 'Untitled')}")
        output.append(f"    Owner: {doc.get('owner', 'Unknown')}")
        output.append(f"    Link: {doc.get('link', 'N/A')}")

        # Extract and display the answer
        if 'extractive_answers' in doc and doc['extractive_answers']:
            answer = doc['extractive_answers'][0]['content']
            # Remove HTML tags for cleaner display
            answer = answer.replace('&lt;b&gt;', '').replace('&lt;/b&gt;', '')
            answer = answer.replace('&amp;#39;', "'").replace('&amp;nbsp;', ' ')
            output.append(f"    Answer: {answer}")

        # Display snippet if verbose
        if verbose and 'snippets' in doc and doc['snippets']:
            snippet = doc['snippets'][0]['snippet']
            snippet = snippet.replace('<b>', '**').replace('</b>', '**')
            snippet = snippet.replace('&#39;', "'").replace('&nbsp;', ' ')
            output.append(f"    Snippet: {snippet}")

        output.append("")

    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(
        description='Search call transcripts using Vertex AI Search'
    )
    parser.add_argument('query', help='Search query')
    parser.add_argument(
        '-n', '--num-results',
        type=int,
        default=10,
        help='Number of results to return (default: 10)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed snippets'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON response'
    )

    args = parser.parse_args()

    try:
        response = search_transcripts(args.query, args.num_results)

        if args.json:
            print(json.dumps(response, indent=2))
        else:
            print(format_results(response, args.verbose))

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
