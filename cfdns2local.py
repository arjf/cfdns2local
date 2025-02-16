#!/usr/bin/env python3
import os
import sys
import time
import json
import requests

class DnsSync:
    def __init__(self):
        """
            Setup the variables and make sure they are declared.
        """
        self.cf_api_token = os.getenv("CF_API_TOKEN")
        self.cf_zone_id = os.getenv("CF_ZONE_ID")
        self.tech_token = os.getenv("TECHNITIUM_TOKEN")
        self.tech_url = os.getenv("TECHNITIUM_URL")
        
        try:
            self.poll_interval = int(os.getenv("POLL_INTERVAL", "300"))
        except ValueError:
            self.poll_interval = 300

        missing = []
        if not self.cf_api_token:
            missing.append("CF_API_TOKEN")
        if not self.cf_zone_id:
            missing.append("CF_ZONE_ID")
        if not self.tech_token:
            missing.append("TECH_TOKEN")
        if missing:
            print("Missing required environment variables: " + ", ".join(missing))
            sys.exit(1)

    def fetch_cf_records(self):
        """
            Query Cloudflare and return the list of DNS records.
        """
        url = f"https://api.cloudflare.com/client/v4/zones/{self.cf_zone_id}/dns_records"
        headers = {
            "Authorization": f"Bearer {self.cf_api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error fetching Cloudflare records: {response.status_code} {response.text}")
        data = response.json()
        return data.get("result", [])

    def update_technitium(self, record):
        """
            Update a single record on the Technitium DNS server.
        """
        name = record.get("name")
        rec_type = record.get("type")
        content = record.get("content")
        ttl = record.get("ttl", 1)
        
        # Skip wildcard records.
        if name.startswith("*."):
            print(f"Skipping wildcard record: {name}")
            return

        endpoint = f"{self.tech_url}/api/zones/records/add"
        params = {
            "token": self.tech_token,
            "domain": name,
            "type": rec_type,
            "ttl": ttl,
            "overwrite": "true"
        }
        if rec_type in ["A", "AAAA"]:
            params["IPAddress"] = content
        elif rec_type == "CNAME":
            params["cname"] = content
        elif rec_type == "TXT":
            params["text"] = content
        else:
            print(f"Record type {rec_type} for {name} not supported; skipping.")
            return

        try:
            r = requests.post(endpoint, params=params)
            if r.status_code == 200:
                print(f"Updated record: {name} ({rec_type}) -> {content}")
            else:
                print(f"Error updating {name}: {r.status_code} {r.text}")
        except Exception as e:
            print(f"Exception updating {name}: {e}")

    def sync(self):
        """
            Sync with Technitium.
        """
        try:
            records = self.fetch_cf_records()
            with open("cf_records.json", "w") as f:
                json.dump(records, f, indent=2)
            print(f"Fetched {len(records)} records from Cloudflare.")
            for rec in records:
                self.update_technitium(rec)
        except Exception as e:
            print(f"Error during sync cycle: {e}")

    def run(self):
        """
            Continuously poll and sync DNS records.
        """
        print("Starting DNS synchronization service...")
        while True:
            self.sync()
            print(f"Waiting for {self.poll_interval}\n")
            time.sleep(self.poll_interval)

def main():
    syncer = DnsSync()
    syncer.run()

if __name__ == "__main__":
    main()
