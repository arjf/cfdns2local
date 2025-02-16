# Cloudflare DNS 2 Local

A docker container running a python script meant to sync the records between your cloudflare zone and technitium zone.

It will ignore all wild card records by default.

Set the following variables to make the container work. Make sure you Cloudflare token has the permissions to the zone you want to sync.

```
CF_API_TOKEN=
CF_ZONE_ID=
TECHNITIUM_TOKEN=
TECHNITIUM_URL=
```