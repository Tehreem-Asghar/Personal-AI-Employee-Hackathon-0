import sys
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.odoo_client import OdooClient
from src.utils.credentials import get_odoo_credentials

# Initialize FastMCP server
mcp = FastMCP("OdooServer")
client = OdooClient()

@mcp.tool()
def get_revenue(days: int = 30) -> str:
    """
    Fetches total revenue from Odoo for the last X days.
    :param days: Number of days to look back (default 30).
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    total = client.get_revenue(start_date, end_date)
    if total == 0.0 and not client.odoo:
        return "Error: Could not connect to Odoo server. Ensure Odoo is running at http://localhost:8069"
        
    return f"Total Revenue from {start_date} to {end_date}: ${total:,.2f}"

@mcp.tool()
def log_invoice(partner_name: str, amount: float, reference: str) -> str:
    """
    Creates a new draft invoice in Odoo.
    :param partner_name: Name of the client/partner.
    :param amount: Total amount of the invoice.
    :param reference: Unique reference or project name.
    """
    invoice_id = client.log_transaction(partner_name, amount, reference)
    if not invoice_id:
        return "Error: Failed to create invoice. Ensure Odoo is connected and partner name is valid."
    
    return f"Draft invoice created successfully. Odoo ID: {invoice_id}. Reference: {reference}"

@mcp.tool()
def post_invoice(invoice_id: int) -> str:
    """
    Confirms/Posts a draft invoice in Odoo. This is a sensitive action.
    :param invoice_id: The Odoo database ID of the invoice.
    """
    success = client.post_invoice(invoice_id)
    if not success:
        return f"Error: Failed to post invoice {invoice_id}."
    
    return f"Invoice {invoice_id} successfully posted to Odoo."

@mcp.tool()
def audit_subscriptions() -> str:
    """
    Audits recent transactions to identify potential recurring subscriptions.
    """
    subscriptions = client.audit_subscriptions()
    if not subscriptions:
        if not client.odoo:
            return "Error: Could not connect to Odoo server."
        return "No recurring subscriptions identified in the last 90 days."
    
    report = ["### Recurring Subscriptions Identified:"]
    for sub in subscriptions:
        report.append(f"- **{sub['name']}**: ${sub['avg_amount']:,.2f} ({sub['count']} occurrences)")
    
    return "
".join(report)

if __name__ == "__main__":
    mcp.run()
