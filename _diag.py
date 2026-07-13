import os, sqlite3, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital.settings")
django.setup()

p = "db.sqlite3"
print("DB exists:", os.path.exists(p))
if os.path.exists(p):
    c = sqlite3.connect(p)
    cur = c.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tabs = [r[0] for r in cur.fetchall()]
    print("TABLE COUNT:", len(tabs))
    for t in tabs:
        if any(k in t for k in ("admin", "patient", "doctor", "auth")):
            print("  ", t)

from django.db.migrations.executor import MigrationExecutor
from django.db import connection

try:
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    print("UNNAPPLIED MIGRATIONS:", len(plan))
    for app, name in plan:
        print("   ", app, name)
except Exception as e:
    print("MIGRATION CHECK ERROR:", repr(e))
