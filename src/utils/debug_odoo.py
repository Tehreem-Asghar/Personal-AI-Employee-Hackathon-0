import odoorpc
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))
load_dotenv(ROOT_DIR / ".env")

def check_invoice():
    try:
        odoo = odoorpc.ODOO(os.getenv("ODOO_URL").split("//")[-1].split(":")[0], port=int(os.getenv("ODOO_URL").split(":")[-1]))
        odoo.login(os.getenv("ODOO_DB"), os.getenv("ODOO_USER"), os.getenv("ODOO_PASS"))
        
        move_obj = odoo.env['account.move']
        # Search for the invoice ID 65 or the reference
        invoice = move_obj.browse(65)
        
        if invoice.exists():
            print(f"✅ Invoice Found!")
            print(f"   - Name: {invoice.name}")
            print(f"   - Partner: {invoice.partner_id.name}")
            print(f"   - Amount: {invoice.amount_total}")
            print(f"   - State: {invoice.state}")
            print(f"   - Move Type: {invoice.move_type}")
        else:
            print("❌ Invoice ID 65 does not exist in the current DB.")
            
            # Search by reference as backup
            ref_ids = move_obj.search([('ref', '=', 'GOLD-INV-001')])
            if ref_ids:
                print(f"Found by reference! ID is: {ref_ids}")
            else:
                print("No invoice found with reference GOLD-INV-001 either.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_invoice()
