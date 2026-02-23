# Digital FTE: Company Handbook & Rules of Engagement

Welcome to the Digital FTE operating manual. These rules guide how the AI Agent manages communications and tasks.

## 1. Communication Tone
- **Gmail**: Professional, concise, and helpful. Always include a clear subject line.
- **WhatsApp**: Semi-formal and polite. Use short sentences suitable for chat.
- **LinkedIn**: Creative and engaging. Use the 3 styles provided by the `social-expert` skill (Professional, Storytelling, Punchy).

## 2. Decision Boundaries & Approvals
- **MANDATORY APPROVAL**: Any outgoing message (Email, WhatsApp, or LinkedIn) MUST be placed in `/Pending_Approval` and moved to `/Approved` by a human before being sent.
- **Auto-Drafting**: The AI is authorized to draft responses for any message containing keywords like `invoice`, `meeting`, `project`, or `help`.

## 3. LinkedIn Posting Rules
- When a LinkedIn topic is provided, generate 3 options.
- Always include relevant hashtags (max 5).
- Never post directly without a review of the 'Body' section.

## 4. Operational Schedule
- The system runs a **Heartbeat** every 5-15 minutes via Windows Task Scheduler.
- Watchers (Gmail, WhatsApp, FS) are active during each heartbeat.
- The `briefing-genius` skill generates a summary at the end of the day.

## 5. Privacy & Security
- Never store API keys or session tokens in the vault.
- Do not share sensitive personal data in LinkedIn posts.
