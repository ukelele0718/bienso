from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from app.db import engine


def run() -> None:
    migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("No migration files found.")
        return

    with engine.begin() as conn:
        for migration in migration_files:
            sql = migration.read_text(encoding="utf-8")
            if not sql.strip():
                continue
            conn.execute(text(sql))
            print(f"Applied {migration.name}")


if __name__ == "__main__":
    run()
