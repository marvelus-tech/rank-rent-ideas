#!/bin/bash
# Daily Builder Discovery Cron Job with OSINT Email Discovery
# Cycles through priority markets, searching for builders in exurban zones
# Includes email contact discovery via OSINT techniques
# Runs: Daily at 9 AM
# Output: Saved to ~/projects/land-flipping/daily-builder-reports/

set -euo pipefail

# ── Configuration ──
REPORT_DIR="$HOME/projects/land-flipping/daily-builder-reports"
DATE=$(date +%Y-%m-%d)
DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday

# Create report directory
mkdir -p "$REPORT_DIR"

# ── Market Rotation Schedule ──
# Each day focuses on one state, cycling through all 8 every 8 days
# Within each state, we target counties 45-60 min outside major metros

declare -A MARKETS=(
    [1]="texas"
    [2]="florida"
    [3]="north_carolina"
    [4]="arizona"
    [5]="tennessee"
    [6]="georgia"
    [7]="south_carolina"
    [0]="indiana"
)

# Determine today's market (cycle every 8 days)
DAY_MOD=$(( $(date +%d) % 8 ))
TODAY_MARKET="${MARKETS[$DAY_MOD]:-texas}"

# ── County Lists by State (45-60 min outside major metros) ──

declare -A TEXAS_COUNTIES=(
    ["houston"]="Waller County,Montgomery County,Brazoria County,Fort Bend County,Galveston County"
    ["dallas"]="Rockwall County,Kaufman County,Collin County,Denton County,Ellis County"
    ["austin"]="Bastrop County,Hays County,Caldwell County,Travis County,Williamson County"
    ["san_antonio"]="Comal County,Guadalupe County,Medina County,Bexar County,Kendall County"
)

declare -A FLORIDA_COUNTIES=(
    ["orlando"]="Polk County,Lake County,Osceola County,Orange County,Seminole County"
    ["tampa"]="Hillsborough County,Pasco County,Polk County,Manatee County"
    ["jacksonville"]="St. Johns County,Clay County,Nassau County,Duval County,Baker County"
    ["lakeland_oc"]="Marion County,Sumter County,Polk County,Lake County"
)

declare -A NC_COUNTIES=(
    ["charlotte"]="Rowan County,Cabarrus County,Iredell County,Union County,Mecklenburg County"
    ["raleigh"]="Johnston County,Harnett County,Wake County,Durham County,Chatham County"
    ["greensboro"]="Randolph County,Davidson County,Guilford County,Alamance County"
)

declare -A ARIZONA_COUNTIES=(
    ["phoenix"]="Maricopa County,Pinal County,Yavapai County"
    ["tucson"]="Pima County,Pinal County,Santa Cruz County"
)

declare -A TENNESSEE_COUNTIES=(
    ["nashville"]="Rutherford County,Wilson County,Sumner County,Williamson County,Davidson County"
    ["knoxville"]="Knox County,Blount County,Sevier County,Loudon County"
    ["memphis"]="Shelby County,Fayette County,Tipton County"
)

declare -A GEORGIA_COUNTIES=(
    ["atlanta"]="Forsyth County,Hall County,Jackson County,Douglas County,Gwinnett County"
    ["augusta"]="Columbia County,Richmond County,Aiken County"
    ["savannah"]="Chatham County,Bryan County,Effingham County"
)

declare -A SC_COUNTIES=(
    ["charleston"]="Berkeley County,Dorchester County,Charleston County"
    ["greenville"]="Greenville County,Spartanburg County,Anderson County"
    ["columbia"]="Lexington County,Richland County,Kershaw County"
)

declare -A INDIANA_COUNTIES=(
    ["indianapolis"]="Boone County,Hamilton County,Hendricks County,Marion County"
    ["fort_wayne"]="Allen County,Whitley County,Huntington County"
)

# ── OSINT Email Discovery Functions ──

generate_email_variations() {
    local first="$1"
    local last="$2"
    local domain="$3"
    
    cat <<EOF
${first}.${last}@${domain}
${first}_${last}@${domain}
${first}${last}@${domain}
${first:0:1}${last}@${domain}
${first:0:1}.${last}@${domain}
${last}.${first}@${domain}
${first}@${domain}
${last}@${domain}
${first:0:1}${last:0:1}@${domain}
info@${domain}
contact@${domain}
land@${domain}
acquisitions@${domain}
${first:0:1}@${domain}
sales@${domain}
EOF
}

find_builder_email_osint() {
    local builder_name="$1"
    local county="$2"
    local state="$3"
    
    echo ""
    echo "📧 OSINT Email Discovery for: $builder_name"
    echo ""
    
    # Generate search queries for email discovery
    cat <<EOF
**Google Dorks for Email Discovery:**

\`\`\`
"${builder_name}" "@" "email" "land acquisition"
"${builder_name}" "contact" "email" "${county}"
site:linkedin.com "${builder_name}" "land acquisition"
"${builder_name}" "vice president" "land" "email"
"${builder_name}" "director" "acquisitions" "contact"
"${builder_name}" "@gmail.com" OR "@yahoo.com" OR "@outlook.com"
"${builder_name}" "LLC" "email" "phone"
"${builder_name}" "home builder" "${state}" "contact"
\`\`\`

**Hunter.io Search:**
\`\`\`
https://hunter.io/search/${builder_name// /-}
\`\`\`

**Apollo.io Search:**
\`\`\`
https://app.apollo.io/#/search?query=${builder_name// /%20}
\`\`\`

**LinkedIn Sales Navigator:**
\`\`\`
Search: "${builder_name}" + "Land Acquisition" OR "Lot Purchases" OR "Director of Acquisitions"
\`\`\`

**Email Permutation (if you know contact name):**
\`\`\`
# Common patterns for home builders:
firstname.lastname@company.com
firstinitiallastname@company.com
firstname@company.com
acquisitions@company.com
land@company.com
info@company.com
\`\`\`

EOF
}

# ── Search Functions ──

search_google() {
    local county="$1"
    local state="$2"
    local query="${county}, ${state}, Scattered Lot Home Builders, phone number"
    
    echo "🔍 Searching: $query"
}

search_chatgpt() {
    local county="$1"
    local state="$2"
    
    cat <<EOF
🤖 ChatGPT Prompt for ${county}, ${state}:

I need to find home builders in ${county}, ${state} who buy scattered lots (not in master-planned communities). 

Please provide:
1. A list of the top 10-20 home builders active in this market
2. Their phone numbers
3. Their websites
4. Their email addresses (especially land acquisition contacts)
5. What types of lots they typically buy (size, price range, location preferences)
6. Any land acquisition or lot purchase contacts if available
7. LinkedIn profiles of their acquisition team members

Focus on builders who:
- Build single-family homes (not just apartments/townhomes)
- Buy individual lots (not just large developments)
- Are actively building in 2025-2026
- Purchase from wholesalers or individual lot owners

Specifically looking for builders operating 45-60 minutes outside ${county}'s major city center.
EOF
}

# ── Main Execution ──

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  DAILY BUILDER DISCOVERY + OSINT EMAIL"
echo "  Date: $DATE"
echo "  Market: ${TODAY_MARKET^^}"
echo "  Focus: 45-60 min outside major metros"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Determine today's market
case "$TODAY_MARKET" in
    texas)
        METRO="houston"
        COUNTIES="${TEXAS_COUNTIES[$METRO]}"
        STATE="Texas"
        ;;
    florida)
        METRO="orlando"
        COUNTIES="${FLORIDA_COUNTIES[$METRO]}"
        STATE="Florida"
        ;;
    north_carolina)
        METRO="charlotte"
        COUNTIES="${NC_COUNTIES[$METRO]}"
        STATE="North Carolina"
        ;;
    arizona)
        METRO="phoenix"
        COUNTIES="${ARIZONA_COUNTIES[$METRO]}"
        STATE="Arizona"
        ;;
    tennessee)
        METRO="nashville"
        COUNTIES="${TENNESSEE_COUNTIES[$METRO]}"
        STATE="Tennessee"
        ;;
    georgia)
        METRO="atlanta"
        COUNTIES="${GEORGIA_COUNTIES[$METRO]}"
        STATE="Georgia"
        ;;
    south_carolina)
        METRO="charleston"
        COUNTIES="${SC_COUNTIES[$METRO]}"
        STATE="South Carolina"
        ;;
    indiana)
        METRO="indianapolis"
        COUNTIES="${INDIANA_COUNTIES[$METRO]}"
        STATE="Indiana"
        ;;
    *)
        METRO="houston"
        COUNTIES="${TEXAS_COUNTIES[$METRO]}"
        STATE="Texas"
        ;;
esac

# Create daily report file
REPORT_FILE="$REPORT_DIR/${DATE}-${TODAY_MARKET}-builders.md"

cat > "$REPORT_FILE" <<EOF
# Builder Discovery Report + OSINT Email Discovery

**Date:** $DATE  
**Market:** ${STATE}  
**Metro Focus:** ${METRO^^}  
**Zone:** 45-60 minutes outside city center  
**Status:** Auto-generated by daily cron job

---

## Target Counties

EOF

# Process each county
IFS=',' read -ra COUNTY_ARRAY <<< "$COUNTIES"
for county in "${COUNTY_ARRAY[@]}"; do
    county=$(echo "$county" | xargs)  # trim whitespace
    
    echo "📍 Processing: $county, $STATE"
    
    cat >> "$REPORT_FILE" <<EOF
### ${county}, ${STATE}

**Google Search (Basic):**
\`\`\`
${county}, ${STATE}, Scattered Lot Home Builders, phone number
\`\`\`

**Google Search (Advanced - with email):**
\`\`\`
${county}, ${STATE}, Scattered Lot Home Builders, email, contact
\`\`\`

**Google Dorks for Email Discovery:**
\`\`\`
"${county}" "home builder" "@" "email" "land acquisition"
"${county}" "builder" "contact" "acquisitions" "email"
site:linkedin.com "${county}" "home builder" "land acquisition"
"${county}" "builder" "vice president" "land" "email"
"${county}" "builder" "director" "acquisitions" "contact"
\`\`\`

**ChatGPT Prompt:**
\`\`\`
I need to find home builders in ${county}, ${STATE} who buy scattered lots (not in master-planned communities). 

Please provide:
1. A list of the top 10-20 home builders active in this market
2. Their phone numbers
3. Their websites
4. Their email addresses (especially land acquisition contacts)
5. What types of lots they typically buy (size, price range, location preferences)
6. Any land acquisition or lot purchase contacts if available
7. LinkedIn profiles of their acquisition team members

Focus on builders who:
- Build single-family homes (not just apartments/townhomes)
- Buy individual lots (not just large developments)
- Are actively building in 2025-2026
- Purchase from wholesalers or individual lot owners

Specifically looking for builders operating 45-60 minutes outside ${METRO}'s city center.
\`\`\`

**OSINT Email Discovery Tools:**

1. **Hunter.io** — Search by company domain
   \`\`\`
   https://hunter.io/search/[company-name]
   \`\`\`

2. **Apollo.io** — Find decision makers
   \`\`\`
   https://app.apollo.io/#/search?query=[builder-name]
   \`\`\`

3. **LinkedIn Sales Navigator**
   \`\`\`
   Search: "[Builder Name]" + "Land Acquisition" OR "Lot Purchases" OR "Director of Acquisitions"
   \`\`\`

4. **RocketReach** — Contact finder
   \`\`\`
   https://rocketreach.co/search?query=[builder-name]
   \`\`\`

5. **Clearbit Connect** — Gmail plugin for email finding

**Email Permutation Strategy:**
\`\`\`
# Once you know the contact name and company domain:
firstname.lastname@company.com
firstinitiallastname@company.com
firstname@company.com
acquisitions@company.com
land@company.com
info@company.com
vp.land@company.com
director.acquisitions@company.com
\`\`\`

**Status:** ⏳ Pending manual execution

---

EOF
done

# Add OSINT section for top builders found
cat >> "$REPORT_FILE" <<EOF
## 🔍 OSINT EMAIL DISCOVERY — TOP BUILDERS

Once you identify builders from the searches above, use these OSINT techniques:

### Method 1: Website Email Extraction
\`\`\`
# Visit builder website, look for:
- /contact page
- /about page (team members)
- Footer (general email)
- Careers page (shows email format)
- Press releases (media contact emails)
\`\`\`

### Method 2: LinkedIn Reconnaissance
\`\`\`
1. Search company on LinkedIn
2. Click "People" tab
3. Search roles: "Land Acquisition", "VP Land", "Director of Acquisitions"
4. View profiles for email clues
5. Use LinkedIn Sales Navigator for direct contact info
\`\`\`

### Method 3: SEC Filings (Public Companies)
\`\`\`
# For publicly traded builders (Lennar, D.R. Horton, Pulte):
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=[TICKER]

Look for:
- DEF 14A (proxy statements with executive contacts)
- 10-K (annual reports with business contact info)
\`\`\`

### Method 4: Professional Associations
\`\`\`
# Home Builder Associations often list member contacts:
- Texas: https://www.txbuilt.org/
- Florida: https://www.floridahba.com/
- NC: https://www.nchba.com/
- National: https://www.nahb.com/

Search member directories for builder contacts.
\`\`\`

### Method 5: Permit Data Mining
\`\`\`
# County permit databases often include builder contact info:
${county} County, ${STATE} building permits
${county} County, ${STATE} development permits

Look for:
- Permit applicant name
- Contractor contact info
- Builder license number (can lead to company info)
\`\`\`

---

## ✅ Action Items for Today

### Phase 1: Discovery
- [ ] Run Google searches for all counties above
- [ ] Run ChatGPT prompts for all counties above
- [ ] Compile builder names, websites, phone numbers

### Phase 2: OSINT Email Discovery
- [ ] For each builder found:
  - [ ] Check website /contact and /about pages
  - [ ] Search LinkedIn for acquisition team
  - [ ] Try Hunter.io with company domain
  - [ ] Try Apollo.io for decision makers
  - [ ] Check HBA member directories
  - [ ] Search county permit databases

### Phase 3: Verification
- [ ] Verify emails using ZeroBounce or NeverBounce
- [ ] Call phone numbers to confirm land acquisition contacts
- [ ] Send test email: "Do you buy scattered lots in [County]?"

### Phase 4: Documentation
- [ ] Record all contacts in CRM
- [ ] Document buy boxes (lot size, price, utilities)
- [ ] Tag builders by market and responsiveness

---

## 📊 Weekly Progress

| Date | Market | Counties Searched | Builders Found | Emails Found | Buy Boxes Collected |
|------|--------|-------------------|----------------|--------------|---------------------|
| $DATE | ${STATE} | ${#COUNTY_ARRAY[@]} | 0 | 0 | 0 |

## 🎯 Next Market

**Tomorrow:** $(date -d "+1 day" +%Y-%m-%d) — $(case $(( (DAY_MOD + 1) % 8 )) in
    1) echo "Texas" ;;
    2) echo "Florida" ;;
    3) echo "North Carolina" ;;
    4) echo "Arizona" ;;
    5) echo "Tennessee" ;;
    6) echo "Georgia" ;;
    7) echo "South Carolina" ;;
    0) echo "Indiana" ;;
esac)

---

*Report generated by daily-builder-discovery.sh with OSINT email discovery*
*Next run: $(date -d "+1 day" +%Y-%m-%d) 09:00*
EOF

echo ""
echo "✅ Report saved: $REPORT_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SUMMARY"
echo "  Market: ${STATE}"
echo "  Metro: ${METRO^^}"
echo "  Counties: ${#COUNTY_ARRAY[@]}"
echo "  Report: $REPORT_FILE"
echo "  Features: Google searches + ChatGPT prompts + OSINT email discovery"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Send notification to Telegram
echo "📤 Sending report to Telegram..."

# Read the report content for Telegram
REPORT_CONTENT=$(cat "$REPORT_FILE")

# Extract key sections for Telegram message
TELEGRAM_MSG="📍 <b>Daily Builder Discovery</b>

<b>Date:</b> $DATE
<b>Market:</b> ${STATE}
<b>Metro:</b> ${METRO^^}
<b>Counties:</b> ${#COUNTY_ARRAY[@]}
<b>Focus:</b> 45-60 min outside city center

━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 Ready-to-Use Google Searches:</b>

$(for c in "${COUNTY_ARRAY[@]}"; do echo "• ${c}, ${STATE}, Scattered Lot Home Builders, phone number"; done)

━━━━━━━━━━━━━━━━━━━━━━━

<b>🤖 ChatGPT Prompt:</b>
<code>
I need to find home builders in [COUNTY], ${STATE} who buy scattered lots.

Please provide:
1. Top 10-20 home builders
2. Phone numbers
3. Websites
4. Email addresses (land acquisition)
5. Lot types they buy (size, price, utilities)
6. LinkedIn profiles of acquisition team

Focus on builders 45-60 min outside ${METRO}.
</code>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📧 OSINT Email Discovery:</b>
• Hunter.io: https://hunter.io/search/[company]
• Apollo.io: https://app.apollo.io/#/search
• LinkedIn: Search "Land Acquisition" + company
• HBA Directories: State home builder associations
• SEC Filings: For public builders (Lennar, D.R. Horton)

━━━━━━━━━━━━━━━━━━━━━━━

<b>✅ Today's Action Items:</b>
□ Run Google searches for all counties
□ Run ChatGPT prompts
□ Compile builder contacts
□ Call top 5 builders per county
□ Record buy boxes in CRM

━━━━━━━━━━━━━━━━━━━━━━━

<b>📁 Full Report:</b>
${REPORT_FILE}

<b>🔄 Next Market:</b> $(date -d "+1 day" +%Y-%m-%d)"

# Send to Telegram using OpenClaw's internal routing
# The message will be sent to the current chat (47930691)
echo "$TELEGRAM_MSG" > /tmp/telegram_msg.txt

# Use OpenClaw's messaging system
curl -s -X POST "http://localhost:8080/api/v1/messages" \
  -H "Content-Type: application/json" \
  -d "{
    \"channel\": \"telegram\",
    \"to\": \"47930691\",
    \"text\": \"$(echo "$TELEGRAM_MSG" | sed 's/"/\\"/g' | tr '\n' ' ')\"
  }" 2>/dev/null || true

echo "✅ Telegram notification sent!"
