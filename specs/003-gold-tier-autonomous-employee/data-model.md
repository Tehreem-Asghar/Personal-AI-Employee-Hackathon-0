# Data Model: Gold Tier - Autonomous Employee

## 1. Odoo Entities (Financial Integration)
These entities are mapped to Odoo Community models using `odoorpc`.

### 1.1 Business Transaction (`account.move`)
| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `ref` | String | Unique transaction reference (e.g., "WHATSAPP-INV-101") | Required |
| `date` | Date | Transaction date | Required |
| `partner_id` | Integer | Odoo Partner ID (Client/Vendor) | Required |
| `line_ids` | List | Journal items (Debit/Credit lines) | Minimum 2 lines |
| `amount_total` | Decimal | Total transaction amount | Positive decimal |
| `state` | Enum | `draft`, `posted`, `cancel` | HITL required for `posted` |

### 1.2 Business Goal (`AI_Employee_Vault/Business_Goals.md`)
| Field | Type | Description |
|-------|------|-------------|
| `revenue_target` | Decimal | Monthly income goal |
| `alert_thresholds` | Map | JSON-like mapping for metric alerts |
| `active_projects` | List | Current open business initiatives |

## 2. Social Media Model
A unified schema for multi-channel posting.

### 2.1 Social Post Concept
| Field | Type | Description | Platform Mapping |
|-------|------|-------------|------------------|
| `content` | Text | The primary body text | Twitter (max 280), FB/LI (Long-form) |
| `channels` | List | Targeted platforms | `linkedin`, `twitter`, `facebook`, `instagram` |
| `hashtags` | List | SEO tags | Max 5 per platform |
| `media_paths` | List | Paths to local image/video assets | IG/FB/LI only |
| `status` | Enum | `draft`, `pending_approval`, `published` | HITL gate on `published` |

## 3. Ralph Wiggum Loop State
Persisted in `AI_Employee_Vault/.system/state.json`.

### 3.1 Task State Machine
| Field | Type | Description |
|-------|------|-------------|
| `task_id` | UUID | Unique task identifier |
| `source_file` | Path | Path to `/Needs_Action` trigger file |
| `iteration_count` | Integer | Current loop count (Max 10) |
| `current_step` | Integer | Current step index in `Plan.md` |
| `history` | List | Log of Claude's previous outputs/errors |
| `status` | Enum | `active`, `stalled`, `completed`, `failed` |

## 4. CEO Briefing Logic
Synthesized daily from Odoo and Obsidian logs.

### 4.1 Briefing Data Points
| Source | Metric | Description |
|--------|--------|-------------|
| Odoo | `weekly_revenue` | Sum of `posted` account moves this week |
| Logs | `avg_cycle_time` | Time from `/Needs_Action` to `/Done` |
| Logs | `iteration_density` | Average Ralph Wiggum iterations per task |
| Goals | `target_variance` | Delta between current revenue and goal |
