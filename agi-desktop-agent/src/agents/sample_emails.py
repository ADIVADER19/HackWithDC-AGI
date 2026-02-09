"""Sample emails for testing the email agent"""

SAMPLE_EMAILS = [
    {
        "id": 1,
        "sender": "john.smith@techcorp.com",
        "subject": "Project Alpha - Budget Review and Timeline",
        "body": """Hi Team,

I hope this email finds you well. I'm writing to discuss the budget allocation for Project Alpha.

Currently, we've allocated $500,000 for Q1 development, but based on recent market analysis and 
competitive pressure from CompetitorX, I'm concerned we may need to increase this to $650,000 to 
stay competitive.

Key concerns:
- CompetitorX launched their AI solution last month
- Our timeline is 8 weeks, theirs was 6 weeks
- We need senior engineers at $150/hr rates

Can you please research current market trends for AI-powered solutions and get back to me by Friday?

Also, please confirm the current team size and available resources.

Thanks,
John Smith
CTO, TechCorp""",
        "date": "2026-02-09",
        "priority": "high"
    },
    {
        "id": 2,
        "sender": "sarah.johnson@marketing.com",
        "subject": "Campaign Strategy - Need Market Research ASAP",
        "body": """Hi,

We're planning our Q2 marketing campaign and need competitive intelligence on the following:
- Current pricing strategies in the SaaS market
- Top 5 marketing channels for B2B software companies
- Case studies on successful product launches

I need this by Monday to present to the executive team. Can you help research these topics 
and provide a summary with sources?

Our target audience is enterprise companies with 1000+ employees.
Budget: $2M for the campaign

Looking forward to your insights!

Best,
Sarah""",
        "date": "2026-02-08",
        "priority": "high"
    },
    {
        "id": 3,
        "sender": "michael.chen@operations.com",
        "subject": "Process Improvement Initiative",
        "body": """Hello,

As part of our continuous improvement program, I'd like to evaluate workflow automation tools.

Specifically, we need information on:
1. Best practices for implementing RPA (Robotic Process Automation)
2. Cost-benefit analysis of popular RPA tools
3. Implementation timeline for mid-size organizations

We're looking to reduce manual processing time by 40% in our finance department.

Can you research and compile this information? Timeline: 1 week.

Thanks,
Michael Chen
VP Operations""",
        "date": "2026-02-07",
        "priority": "medium"
    },
    {
        "id": 4,
        "sender": "emma.watson@hr.com",
        "subject": "Talent Acquisition - Market Analysis",
        "body": """Hi there,

We're expanding our engineering team and need market insights:

- Average salary ranges for Senior ML Engineers in major tech hubs (SF, NYC, Austin, Seattle)
- Top companies actively hiring for ML roles
- Popular platforms for recruiting AI/ML talent
- Current trends in remote work policies

We're planning to hire 5 senior engineers in the next quarter.

Please provide recommendations by next Friday.

Thanks,
Emma Watson
Head of Talent Acquisition""",
        "date": "2026-02-06",
        "priority": "medium"
    },
    {
        "id": 5,
        "sender": "david.lee@product.com",
        "subject": "Feature Roadmap - Customer Feedback Analysis",
        "body": """Team,

For our upcoming product launch, I need analysis on:

1. What are customers asking for most in project management tools?
2. Feature comparison: Monday.com vs Asana vs Jira
3. Latest trends in AI-assisted project management
4. Customer pain points in current solutions

This will help prioritize our feature development.

Can you research and send a report with key findings and sources?

Timeline: This week ideally.

Thanks,
David""",
        "date": "2026-02-05",
        "priority": "high"
    }
]

def get_sample_emails():
    """Get all sample emails"""
    return SAMPLE_EMAILS

def get_email_by_id(email_id: int):
    """Get a specific email by ID"""
    for email in SAMPLE_EMAILS:
        if email['id'] == email_id:
            return email
    return None

def print_email(email: dict):
    """Pretty print an email"""
    print(f"\n{'='*70}")
    print(f"FROM: {email['sender']}")
    print(f"SUBJECT: {email['subject']}")
    print(f"DATE: {email['date']}")
    print(f"PRIORITY: {email['priority']}")
    print(f"{'='*70}")
    print(email['body'])
    print(f"{'='*70}\n")

if __name__ == "__main__":
    # Example usage
    print("📧 Sample Emails for Testing Email Agent\n")
    for email in SAMPLE_EMAILS:
        print_email(email)
