"""
Demo email data for testing Email Intelligence Agent
"""

from typing import Dict, Any

DEMO_EMAILS = {
    "acme_ventures": {
        "from": "alex.chen@acmeventures.com",
        "subject": "Series B Partnership Discussion - DataFlow AI",
        "date": "2026-02-09",
        "metadata": {
            "from": "Alex Chen",
            "company": "Acme Ventures",
            "position": "Managing Director",
            "email": "alex.chen@acmeventures.com",
        },
        "content": """Hi there,

I hope this email finds you well. I'm reaching out because Acme Ventures has been impressed with DataFlow AI's recent product developments and market traction.

We're currently looking at Series B opportunities in the AI/ML space, and DataFlow AI's approach to real-time data processing caught our attention. I saw your recent announcement about the Enterprise partnership and the 40% growth in Q4 2025.

Our portfolio includes companies like Quantum Labs, NeuralNet Systems, and CloudScale AI. We've helped them scale to $100M+ ARR and expand into enterprise markets.

I'd love to have a conversation about potential partnership opportunities. Would you be available for a call next week?

Also, I noticed you're based in SF - we're opening our West Coast office next month and would love to have strategic partners in the area.

Looking forward to connecting!

Best regards,
Alex Chen
Managing Director, Acme Ventures
www.acmeventures.com
""",
    },
    "startup_inquiry": {
        "from": "sarah.patel@techstartup.io",
        "subject": "Technical Partnership Opportunity",
        "date": "2026-02-08",
        "metadata": {
            "from": "Sarah Patel",
            "company": "TechStartup Inc",
            "position": "CEO & Co-founder",
            "email": "sarah.patel@techstartup.io",
        },
        "content": """Hi,

My name is Sarah Patel, and I'm the CEO of TechStartup Inc, a Series A-funded startup focused on autonomous systems for manufacturing.

We're currently evaluating vendors for our core ML infrastructure and came across your platform. The benchmarks look impressive - particularly the 99.99% uptime SLA and sub-100ms latency.

We're processing 2TB+ of sensor data daily and need a solution that can scale with us. I have a few technical questions:

1. How do you handle model versioning and rollback in production?
2. What's your typical onboarding timeline for enterprise customers?
3. Can you support custom GPU configurations for our specific model architecture?

We're making a decision this quarter and would love to schedule a technical deep-dive with your team.

Also, if you know any other founders in the autonomous systems space, I'd love to network - we're building a small community around this.

Best,
Sarah

---
Sarah Patel
CEO & Co-founder, TechStartup Inc
https://techstartup.io
""",
    },
    "investor_follow_up": {
        "from": "michael.ko@capitalfund.io",
        "subject": "Re: Investment Discussion - Follow-up Questions",
        "date": "2026-02-07",
        "metadata": {
            "from": "Michael Ko",
            "company": "Capital Fund",
            "position": "Senior Investor",
            "email": "michael.ko@capitalfund.io",
        },
        "content": """Hi there,

Thanks for the great pitch meeting last week. Our team at Capital Fund was impressed with your market analysis and go-to-market strategy.

Before we move forward with next steps, I had a few follow-ups:

1. I noticed your main competitors are CurveAI and DataWorks - how are you differentiating beyond pricing?
2. Your TAM calculation of $50B seems conservative. Can you break down how you got that number?
3. What's your plan for enterprise sales when you only have 2 enterprise customers currently?

I also want to introduce you to Emma Rodriguez, our VP of Growth - she's worked with 50+ startups and could provide valuable insights for scaling.

We're looking to close our Series A fund this quarter, so timing is tight.

Let me know your thoughts!

Best regards,
Michael Ko
Senior Investor, Capital Fund
""",
    },
    "partnership_proposal": {
        "from": "james.wilson@integrations.com",
        "subject": "Strategic Partnership - Integration Opportunity",
        "date": "2026-02-06",
        "metadata": {
            "from": "James Wilson",
            "company": "Integrations Plus",
            "position": "Head of Partnerships",
            "email": "james.wilson@integrations.com",
        },
        "content": """Hello,

I'm James Wilson, Head of Partnerships at Integrations Plus. We work with 500+ SaaS companies to provide native integrations and APIs.

After reviewing your platform, I believe there's a strong partnership opportunity. Our customers are constantly asking for integrations with solutions like yours, and we've noticed increasing demand in the data processing space.

Here's what we're proposing:
- Joint go-to-market for our shared customer base
- White-label API access for our enterprise partners
- Revenue sharing model (70/30 split favoring you)

We've successfully done this with companies like DataSync and MetricsFlow, generating $2-3M additional revenue per year for partners.

Would you be interested in exploring this further? I can schedule a 30-minute call to go over the details.

Our platform serves enterprises in Finance, Healthcare, and E-commerce - sectors where your offering would be valuable.

Looking forward to your response!

Best,
James Wilson
Head of Partnerships, Integrations Plus
""",
    },
}


def get_demo_email(key: str) -> Dict[str, Any]:
    """Get a specific demo email"""
    return DEMO_EMAILS.get(key)


def get_all_demo_emails() -> Dict[str, Any]:
    """Get all demo emails"""
    return DEMO_EMAILS


def list_demo_emails() -> list:
    """List all available demo email keys"""
    return list(DEMO_EMAILS.keys())


if __name__ == "__main__":
    print("📧 Available Demo Emails:\n")
    for key in list_demo_emails():
        email = DEMO_EMAILS[key]
        print(f"• {key}")
        print(f"  From: {email['metadata']['from']} ({email['metadata']['company']})")
        print(f"  Subject: {email['subject']}\n")
