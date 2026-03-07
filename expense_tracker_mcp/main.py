from fastmcp import FastMCP
import os
import aiosqlite
import sqlite3
import tempfile
import json

# Temporary directory for writable database
TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "expenses.db")

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

print(f"Database path: {DB_PATH}")

mcp = FastMCP("ExpenseTracker")


# -------------------------------
# Initialize database
# -------------------------------
def init_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA journal_mode=WAL")

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
                """
            )

            # Write test
            conn.execute(
                "INSERT OR IGNORE INTO expenses(date, amount, category) VALUES ('2000-01-01', 0, 'test')"
            )
            conn.execute("DELETE FROM expenses WHERE category='test'")

            print("Database initialized successfully")

    except Exception as e:
        print("Database initialization error:", e)
        raise


# Initialize DB on startup
init_db()


# -------------------------------
# Add Expense Tool
# -------------------------------
@mcp.tool()
async def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = "",
) -> dict:
    """Add a new expense entry to the database."""

    try:
        async with aiosqlite.connect(DB_PATH) as conn:

            cursor = await conn.execute(
                """
                INSERT INTO expenses(date, amount, category, subcategory, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (date, amount, category, subcategory, note),
            )

            await conn.commit()

            expense_id = cursor.lastrowid

            return {
                "status": "success",
                "id": expense_id,
                "message": "Expense added successfully",
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# -------------------------------
# List Expenses Tool
# -------------------------------
@mcp.tool()
async def list_expenses(
    start_date: str,
    end_date: str,
) -> list[dict]:
    """List expenses within an inclusive date range."""

    try:
        async with aiosqlite.connect(DB_PATH) as conn:

            cursor = await conn.execute(
                """
                SELECT id, date, amount, category, subcategory, note
                FROM expenses
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
                """,
                (start_date, end_date),
            )

            rows = await cursor.fetchall()

            cols = [d[0] for d in cursor.description]

            return [dict(zip(cols, row)) for row in rows]

    except Exception as e:
        return [{"error": str(e)}]


# -------------------------------
# Summarize Expenses Tool
# -------------------------------
@mcp.tool()
async def summarize(
    start_date: str,
    end_date: str,
    category: str | None = None,
) -> list[dict]:
    """Summarize expenses by category."""

    try:
        async with aiosqlite.connect(DB_PATH) as conn:

            query = """
            SELECT category,
                   SUM(amount) as total_amount,
                   COUNT(*) as count
            FROM expenses
            WHERE date BETWEEN ? AND ?
            """

            params = [start_date, end_date]

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " GROUP BY category ORDER BY total_amount DESC"

            cursor = await conn.execute(query, params)

            rows = await cursor.fetchall()

            cols = [d[0] for d in cursor.description]

            return [dict(zip(cols, row)) for row in rows]

    except Exception as e:
        return [{"error": str(e)}]


# -------------------------------
# Categories Resource
# -------------------------------
@mcp.resource("expense:///categories", mime_type="application/json")
def categories() -> str:

    default_categories = {
        "categories": [
            "Food & Dining",
            "Transportation",
            "Shopping",
            "Entertainment",
            "Bills & Utilities",
            "Healthcare",
            "Travel",
            "Education",
            "Business",
            "Other",
        ]
    }

    try:
        with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
            return f.read()

    except FileNotFoundError:
        return json.dumps(default_categories, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


# -------------------------------
# Start MCP Server
# -------------------------------
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
    )