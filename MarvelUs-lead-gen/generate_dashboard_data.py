import json

# Load all leads
with open('data/processed/leads_master.json') as f:
    leads = json.load(f)

# Convert to dashboard format
dashboard_leads = []
for i, lead in enumerate(leads, 1):
    # Extract location short
    location = lead.get('location', 'Melbourne')
    if ',' in location:
        location = location.split(',')[0]
    
    # Get scores
    seo = lead.get('tech_sophistication_score', 50) or 50
    overall = lead.get('lead_score', 50) or 50
    
    # Determine priority - use raw priority value
    priority = lead.get('priority', 'low').lower()
    if priority not in ['high', 'medium', 'low']:
        priority = 'low'
    
    # Get recommended service from outreach_recommended_key
    recommended = lead.get('outreach_recommended_key', 'AI Voice')
    
    # Map to display names
    recommended_display = {
        'ai_voice': 'AI Voice',
        'ai_chatbot': 'AI Chatbot',
        'seo_optimization': 'SEO',
        'web_presence': 'Web/SEO',
        'reputation_management': 'Reputation',
        'online_booking': 'Booking'
    }.get(recommended, 'AI Voice')
    
    # Check multi-opportunity from outreach_is_multi
    multi = lead.get('outreach_is_multi', False)
    
    # Get outreach drafts
    sms = lead.get('outreach_sms', '')
    email_subject = lead.get('outreach_email_subject', '')
    email_body = lead.get('outreach_email_body', '')
    
    # Clean up SMS if too long
    if len(sms) > 160:
        sms = sms[:157] + '...'
    
    dashboard_leads.append({
        'id': i,
        'name': lead.get('name', 'Unknown'),
        'category': lead.get('category', 'business'),
        'location': location,
        'website': lead.get('website', ''),
        'seo': min(100, max(0, int(seo))),
        'overall': min(100, max(0, int(overall))),
        'recommended': recommended_display,
        'priority': priority,
        'multi': multi,
        'phone': lead.get('phone', ''),
        'email': lead.get('email', ''),
        'sms': sms,
        'email_subject': email_subject,
        'email_body': email_body,
        'score_reasons': lead.get('score_reasons', '')
    })

# Save dashboard data
with open('output/dashboard_data.json', 'w') as f:
    json.dump(dashboard_leads, f, indent=2)

print(f'✅ Dashboard data saved: {len(dashboard_leads)} leads')
categories = set(l['category'] for l in dashboard_leads)
print(f'Categories: {categories}')
high = sum(1 for l in dashboard_leads if l['priority']=='high')
medium = sum(1 for l in dashboard_leads if l['priority']=='medium')
low = sum(1 for l in dashboard_leads if l['priority']=='low')
print(f'Priorities: high={high}, medium={medium}, low={low}')
print(f'Multi-opportunity: {sum(1 for l in dashboard_leads if l["multi"])}')
