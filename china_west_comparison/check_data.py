"""Query CloudBase experiment data."""
import subprocess, json, sys

ENV = "five-tone-cathykang-d4b0676685c9"

def run(cmd_json):
    r = subprocess.run(["tcb","db","nosql","execute","--env-id",ENV,"--command",cmd_json,"--json"],
                       capture_output=True, text=True, timeout=30)
    lines = r.stdout.split('\n')
    for i, l in enumerate(lines):
        if l.strip().startswith('['):
            return json.loads('\n'.join(lines[i:]))
    return []

def count(q='{}'):
    cmd = '[{"TableName":"experiments","CommandType":"COMMAND","Command":"{\\"count\\":\\"experiments\\",\\"query\\":%s}"}]' % q
    r = run(cmd)
    n = r[0]['n']
    return n['$numberInt'] if isinstance(n, dict) else n

total = count()
west_q = '{"order":{"$in":["west_01","west_02","west_03","west_04","west_05"]}}'
west = count(west_q)

print(f"Total: {total}")
print(f"Chinese-only (old): {total - west}")
print(f"With Western: {west}")
