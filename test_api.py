#!/usr/bin/env python3
"""
Test script to verify clist.by API authentication
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv


async def test_api():
    # Load environment variables
    load_dotenv()

    username = os.getenv('CLIST_API_USERNAME')
    api_key = os.getenv('CLIST_API_KEY')

    print(f"Testing clist.by API authentication...")
    print(f"Username: {username}")
    print(
        f"API Key: {'*' * (len(api_key) - 4) + api_key[-4:] if api_key else 'None'}")

    if not username or not api_key:
        print("❌ Missing API credentials!")
        return

    # Test API call
    headers = {'Authorization': f'ApiKey {username}:{api_key}'}

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            url = "https://clist.by/api/v4/contest/"
            params = {
                'resource__in': 'codeforces.com',
                'limit': 1,
                'format': 'json'
            }

            print(f"\nTesting API call to: {url}")

            async with session.get(url, params=params) as response:
                print(f"Response status: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    print("✅ API authentication successful!")
                    print(
                        f"Total contests available: {data.get('meta', {}).get('total_count', 'Unknown')}")
                elif response.status == 401:
                    print("❌ API authentication failed - Invalid credentials")
                elif response.status == 429:
                    print("⚠️  Rate limited - too many requests")
                else:
                    text = await response.text()
                    print(f"❌ API error {response.status}: {text}")

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
