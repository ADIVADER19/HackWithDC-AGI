# 🚀 Email Intelligence Agent - UI Ready!

## Launch the UI

```bash
cd /Users/kajalpatel/HackWithDC-AGI/agi-desktop-agent
streamlit run app.py
```

**UI opens at:** http://localhost:8501

---

## What You Can Do

### 1️⃣ **Choose an Email**
   - **Demo Mode**: Select from 4 realistic business email samples
   - **Custom Mode**: Paste any email content

### 2️⃣ **Click "Analyze Email"**
   - Agent extracts entities (companies, people)
   - Assesses which need research (Smart Linkup)
   - Searches only for unknowns
   - Generates professional reply

### 3️⃣ **View Results** (5 tabs)
   - **🔍 Entities**: Companies, people, products found
   - **📚 Research**: Sources (shows if from knowledge ✓ or search 🔍)
   - **✍️ Reply**: AI-generated response
   - **🧠 Reasoning**: Decision-making steps
   - **📈 Stats**: Efficiency & cost savings

### 4️⃣ **Export**
   - Download as JSON (machine-readable)
   - Download as text (human-readable)

---

## Smart Linkup in the UI

### How to Spot It

**Green Badge "✓ Source: Existing Knowledge"**
- Used existing knowledge (no API call)
- Fast, free, already available
- Example: Google, Microsoft, Amazon

**Blue Badge "🔍 Found X sources from Linkup"**
- Searched external sources
- Current, comprehensive information
- Example: New startup, specific funding info

### Impact Shown
```
Efficiency: 50%
(Shows that 50% of entities avoided searching)

💰 Cost Saved: $0.01
(Shows estimated savings from skipped searches)
```

---

## Test Scenarios (Built-in)

### Demo Email 1: Acme Ventures
- Large VC firm (series B discussion)
- Portfolio companies
- Managing director contact
- **Result**: Mix of known and unknown entities

### Demo Email 2: Startup Inquiry
- New startup reaching out
- Specific product focus
- Investment question
- **Result**: Unknown entity = triggers search

### Demo Email 3: Investor Follow-up
- Existing investor
- Series A round discussion
- Market opportunity
- **Result**: Known investor = uses knowledge

### Demo Email 4: Partnership Proposal
- Multiple companies mentioned
- Collaboration opportunity
- Funding involvement
- **Result**: Hybrid approach

---

## Key Metrics Dashboard

At the top, you'll see:

| Metric | Meaning |
|--------|---------|
| **Total Entities** | How many companies/people found |
| **Searched (Linkup)** | How many needed web search |
| **Using Knowledge** | How many used existing knowledge |
| **Efficiency** | % that avoided searching |

**Goal**: High efficiency % = lower costs + faster responses

---

## Example Walkthrough

1. ✅ Open: http://localhost:8501
2. ✅ Select: "Acme Ventures" demo
3. ✅ Click: "Analyze Email"
4. ✅ Wait: ~8-10 seconds (includes web searches)
5. ✅ View: Results in 5 tabs
6. ✅ See: 
   - Some entities with "✓ Existing Knowledge"
   - Some with "🔍 Linkup Search"
   - Efficiency metric showing % avoided
   - Cost savings estimate

---

## Pro Tips

### Speed Up Testing
- Click "Show reasoning steps" OFF to hide verbose logs
- Use "Show all sources" OFF to see summary

### See Everything
- Click "Show reasoning steps" ON to see every decision
- Click "Show all sources" ON to see all findings

### Debug Issues
- Check "Reasoning" tab for decision explanations
- Look at entity extraction first (may be empty)
- Check Stats tab for API/cost info

---

## What's Running Behind Scenes

```
Your Email
    ↓
[Groq LLM] Extract Entities
    ↓
[Smart Decision] For each entity:
    ├─ Is it well-known? → Use existing knowledge ✓
    └─ Unknown? → Search Linkup 🔍
    ↓
[Groq LLM] Generate Reply (using both sources)
    ↓
UI Display (5 tabs + metrics)
    ↓
Export Options (JSON/Text)
```

---

## Next Steps

1. ✅ **Try the UI** with demo emails
2. ✅ **Test with custom emails** (paste your own)
3. ✅ **Export results** for sharing
4. ✅ **Run tests** (see how it performs)
5. 🔜 **Integrate with Gmail** (future enhancement)

---

## Commands Reference

```bash
# Run the UI
streamlit run app.py

# Run with custom port (if 8501 is taken)
streamlit run app.py --server.port=8502

# Run tests
python tests/test_smart_linkup.py          # 3 scenarios
python tests/test_email_intelligence_agent.py  # Integration

# Kill the app (if needed)
pkill -f "streamlit run"
```

---

## 📊 Expected Performance

- **Known entities**: ~2 seconds (just LLM, no search)
- **Unknown entities**: ~6-8 seconds (includes Linkup search)
- **Mixed emails**: ~5-8 seconds average
- **Full analysis**: ~10 seconds total

---

**Ready to test? Launch the UI now! 🚀**

```bash
streamlit run app.py
```
