# Email Intelligence Agent - UI Setup & Usage

## 🚀 Quick Start

### Run the UI

```bash
cd /Users/kajalpatel/HackWithDC-AGI/agi-desktop-agent

# Option 1: Run directly
streamlit run app.py

# Option 2: Use full path
/Users/kajalpatel/HackWithDC-AGI/agi-desktop-agent/venv/bin/streamlit run app.py
```

The app will open at: **http://localhost:8501**

## 🎯 UI Features

### Input Modes
- **Demo Emails**: Choose from 4 pre-loaded sample business emails
- **Custom Email**: Paste any email content for analysis

### Analysis Tabs

1. **🔍 Entities Tab**
   - Shows all extracted companies, people, and products
   - Color-coded by entity type
   - Displays context for each entity

2. **📚 Research Tab**
   - Shows research findings for each entity
   - **Green**: Using existing knowledge (no API call)
   - **Blue**: From Linkup web search
   - Top 3 sources by default (toggle to see all)

3. **✍️ Reply Tab**
   - Displays the AI-generated reply
   - Professional, contextually-aware response
   - Uses both research and existing knowledge

4. **🧠 Reasoning Tab**
   - Shows all decision-making steps
   - Timestamps for each action
   - Helps understand what the agent did

5. **📈 Stats Tab**
   - Efficiency percentage
   - Cost savings estimate
   - API call breakdown

### Dashboard Metrics
- **Total Entities**: Number of companies/people found
- **Searched (Linkup)**: How many required external search
- **Using Knowledge**: How many used existing knowledge
- **Efficiency**: % of entities that avoided API calls

### Options (Sidebar)
- ✅ Show reasoning steps (detailed decision logs)
- ✅ Show all sources (vs just top 3 per entity)

### Export Results
- 📄 **JSON**: Download full analysis as JSON
- 📝 **Text**: Download summary as plain text

## 📊 Example Workflow

### Step 1: Select Email
- Choose "Acme Ventures" demo email (or paste custom)

### Step 2: Click "Analyze Email"
- Agent extracts entities
- Assesses which need research
- Performs smart Linkup searches
- Generates professional reply

### Step 3: Review Results
- Check extracted entities
- Review research findings (see which used knowledge vs search)
- Read the drafted reply
- View efficiency metrics

### Step 4: Export
- Download JSON for further processing
- Download text for sharing

## 🧠 Smart Linkup Usage Visualization

The UI clearly shows:
- **✓ Existing Knowledge** entries (green badges) = Free, fast
- **🔍 Linkup Search** entries (blue badges) = Current, comprehensive
- **Efficiency %** = How many searches were avoided

**Example**: 
- Google (known) → Uses existing knowledge ✓
- DataFlow AI (unknown) → Searches Linkup 🔍
- Result: 50% efficiency (1 of 2 avoided search)

## 🔧 Configuration

### Environment Variables
Make sure `.env` is set up in `config/` folder:
```
GROQ_API_KEY=your_groq_key
LINKUP_API_KEY=your_linkup_key
```

### Customize Demo Emails
Edit `tests/demo_data/sample_emails.py` to add more examples

## 🎨 UI Styling

- **Color-coded entities**: Companies (blue), People (purple), Products (green)
- **Responsive layout**: Adapts to screen size
- **Real-time metrics**: Updates as analysis progresses
- **Professional styling**: Clean, modern interface

## ⚡ Performance

- Small emails: 2-3 seconds
- Medium emails (5-7 entities): 5-8 seconds
- Large emails: 10-15 seconds
- Well-known entities: ~1 second (no search)
- Unknown entities: ~3-4 seconds (with search)

## 📱 Browser Compatibility

- Chrome/Edge/Firefox: Full support
- Safari: Full support
- Mobile browsers: Works but best on desktop

## 🐛 Troubleshooting

### Port already in use?
```bash
streamlit run app.py --server.port=8502
```

### Need to restart?
```bash
pkill -f "streamlit run"
```

### Check logs?
```bash
streamlit run app.py --logger.level=debug
```

## 📚 What's Behind the Scenes?

```
User Input (Email)
    ↓
Email Intelligence Agent
    ├─ Step 1: Extract entities (Groq LLM)
    ├─ Step 2: Assess knowledge for each entity
    │   ├─ Known entity? → Use existing knowledge (fast, free)
    │   └─ Unknown? → Search Linkup (comprehensive)
    └─ Step 3: Draft reply (Groq LLM)
    ↓
UI Display
    ├─ Entities extracted
    ├─ Research findings (with source type)
    ├─ Smart Linkup stats
    ├─ Professional reply
    └─ Export options
```

## 🚀 Next Steps

1. **Try demo emails** to understand the system
2. **Paste custom emails** to test on real data
3. **Review reasoning steps** to see decision-making
4. **Export results** for further use
5. **Integrate with email provider** (Gmail/Outlook - future)

## 📞 Getting Help

- Check the reasoning tab to understand decisions
- Review source types to see research approach
- Check metrics to see efficiency gains
- Export and review JSON for debugging
