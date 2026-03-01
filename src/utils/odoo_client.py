import odoorpc
import os
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class OdooClient:
    """
    Wrapper for Odoo JSON-RPC API using odoorpc.
    """
    def __init__(self):
        self.url = os.getenv("ODOO_URL", "http://localhost:8069")
        self.db = os.getenv("ODOO_DB", "ai_employee")
        self.user = os.getenv("ODOO_USER")
        self.password = os.getenv("ODOO_PASS")
        self.odoo = None

    def connect(self) -> bool:
        """Establishes connection to the Odoo server."""
        try:
            self.odoo = odoorpc.ODOO(self.url.split("//")[-1].split(":")[0], port=int(self.url.split(":")[-1]))
            self.odoo.login(self.db, self.user, self.password)
            logger.info(f"Successfully connected to Odoo DB: {self.db}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}")
            return False

    def get_revenue(self, start_date: str, end_date: str) -> float:
        """Fetches total revenue for a given period."""
        if not self.odoo:
            if not self.connect():
                return 0.0
        
        # Mapping to account.move (Invoices)
        move_obj = self.odoo.env['account.move']
        moves = move_obj.search([
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted')
        ])
        
        # Use direct read to avoid frozendict errors
        data = move_obj.read(moves, ['amount_total'])
        total = sum(d.get('amount_total', 0.0) for d in data)
        return total

    def log_transaction(self, partner_name: str, amount: float, ref: str) -> Optional[int]:
        """Logs a new draft invoice/transaction in Odoo."""
        if not self.odoo:
            if not self.connect():
                return None
        
        try:
            partner_obj = self.odoo.env['res.partner']
            partner_ids = partner_obj.search([('name', '=', partner_name)])
            
            if not partner_ids:
                partner_id = partner_obj.create({'name': partner_name})
            else:
                partner_id = partner_ids[0]

            move_obj = self.odoo.env['account.move']
            
            # Find the sales journal ID
            journal_obj = self.odoo.env['account.journal']
            journal_ids = journal_obj.search([('type', '=', 'sale')])
            journal_id = journal_ids[0] if journal_ids else None

            invoice_id = move_obj.create({
                'partner_id': partner_id,
                'move_type': 'out_invoice',
                'journal_id': journal_id,
                'ref': ref,
                'invoice_line_ids': [(0, 0, {
                    'name': f'Service for {ref}',
                    'price_unit': amount,
                    'quantity': 1,
                })]
            })
            return invoice_id
        except Exception as e:
            logger.error(f"Error logging transaction to Odoo: {e}")
            return None

    def post_invoice(self, invoice_id: int) -> bool:
        """Posts (confirms) a draft invoice in Odoo."""
        if not self.odoo:
            if not self.connect():
                return False
        
        try:
            move_obj = self.odoo.env['account.move']
            move_obj.action_post([invoice_id])
            return True
        except Exception as e:
            logger.error(f"Error posting invoice {invoice_id}: {e}")
            return False

    def audit_subscriptions(self) -> List[Dict]:
        """
        Identifies potential recurring subscriptions in Odoo.
        Returns a list of unique recurring transaction descriptions and their average amounts.
        """
        if not self.odoo:
            if not self.connect():
                return []
        
        try:
            # Search for posted invoices/bills in the last 90 days
            move_obj = self.odoo.env['account.move']
            three_months_ago = (odoorpc.fields.Date.today() - odoorpc.fields.timedelta(days=90)).strftime('%Y-%m-%d')
            
            moves = move_obj.search([
                ('date', '>=', three_months_ago),
                ('state', '=', 'posted')
            ])
            
            # Simple pattern matching for recurring items
            # In a real Odoo setup, we might look at 'recurring_next_date' in subscriptions module
            # but for a general audit, we check for repetition in references/lines
            data = move_obj.read(moves, ['ref', 'amount_total', 'date'])
            
            # Group by reference to find patterns
            patterns = {}
            for item in data:
                ref = item.get('ref', 'Unknown')
                if not ref: continue
                
                if ref not in patterns:
                    patterns[ref] = []
                patterns[ref].append(item['amount_total'])
            
            recurring = []
            for ref, amounts in patterns.items():
                if len(amounts) >= 2: # Appears more than once in 90 days
                    recurring.append({
                        "name": ref,
                        "count": len(amounts),
                        "avg_amount": sum(amounts) / len(amounts),
                        "frequency": "recurring"
                    })
            
            return recurring
        except Exception as e:
            logger.error(f"Error auditing subscriptions: {e}")
            return []
