# Incident Runbook: Endpoint DOWN or SLOW

## Detect
- The dashboard shows DOWN or SLOW, or the CI run fails.
- Note the time, service name, HTTP status and error message.

## Triage
1. Is it one service or several? Several at once points to network or DNS.
2. Does the URL load in a browser? Does it work from another network?
3. Check the provider's status page.
4. Check for a recent deployment or change.

## Common causes
| Symptom | Likely cause | First action |
|---------|--------------|--------------|
| Name resolution error | DNS failure | Check DNS records and resolver |
| Timeout | Network, firewall or overloaded service | Check connectivity and load |
| HTTP 5xx | Application or server fault | Check application logs |
| HTTP 4xx | Moved page, auth or config issue | Check the URL and credentials |
| SLOW but UP | Load or resource exhaustion | Check CPU, memory and recent traffic |

## Escalate if
- A production service is DOWN for more than 5 minutes.
- Multiple services are affected.
- You cannot identify a cause within 15 minutes.

## Record
Timeline, impact, cause, fix and follow-up actions. Add them to the incident record.
