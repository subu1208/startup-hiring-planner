# 🧠 Agentic Hiring Plan Generator

An AI-powered hiring automation tool built with **LangGraph** and **Streamlit** that helps startups generate LinkedIn-style job descriptions, hiring checklists, and email templates for their recruitment process.

## 🚀 Features

### 📄 Job Description Generation
- **AI-powered JD creation**: Generates professional LinkedIn-style job postings
- **Role-specific templates**: Browse pre-built templates for 20+ startup roles
- **Customizable content**: Tailored based on your specific requirements and clarifications

### ✅ Interactive Hiring Checklists
- **Step-by-step guidance**: 8-12 actionable recruiting tasks per role
- **Progress tracking**: Visual progress bars and checkboxes
- **Tool-specific recommendations**: Mentions platforms like LinkedIn, HackerRank, etc.

### 📬 Email Templates
- **Professional templates**: Ready-to-use email templates for different hiring stages
- **Multiple scenarios**: Interview invitations, rejections, technical assessments, offers
- **Customizable content**: Easy to personalize with candidate and company details

### 💾 Session Management
- **Persistent state**: Save and resume your work across sessions
- **JSON export/import**: Download your session data for backup
- **Progress preservation**: Maintain checklist completion status

## 🛠️ Tech Stack

- **Backend**: Python, LangGraph, OpenRouter API
- **Frontend**: Streamlit
- **AI Integration**: GPT-3.5-turbo via OpenRouter
- **State Management**: JSON-based session persistence

## 📋 Prerequisites

- Python 3.8+
- OpenRouter API key
- Required Python packages (see installation)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agentic-hiring-generator
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit langgraph requests python-dotenv
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

## 📖 Usage Guide

### Getting Started

1. **Launch the app** and choose from three main options:
   - Generate Hiring Plan
   - Show JD Templates  
   - Show Email Templates

### Generating a Hiring Plan

1. **Enter role titles** (comma-separated) you want to hire for
2. **Complete clarifications** for each role:
   - Job summary and responsibilities
   - Compensation and equity details
   - Timeline and deadlines
   - Work setup (Remote/Hybrid/Onsite)
   - Required and preferred skills
   - Expected outcomes

3. **Generate the plan** - The AI will create:
   - Professional job descriptions
   - Actionable hiring checklists
   - Progress tracking interface

4. **Track progress** using interactive checkboxes
5. **Download** the complete hiring plan as Markdown

### Available Roles

The system supports 20+ startup roles including:
- **Engineering**: Founding Engineer, Software Engineer, DevOps Engineer, QA Engineer
- **Product**: Product Manager, UX/UI Designer, Product Designer
- **Business**: Sales Rep, Business Development Manager, Customer Success Manager
- **Operations**: Marketing Specialist, HR Manager, Finance Manager, Operations Manager
- **Internships**: Software Engineering, Product, Marketing, Operations, GenAI Intern

## 🏗️ Architecture

### Backend Components (`hragent_app.py`)

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Clarify Node  │───▶│ JD Generator Node│───▶│ Checklist Node  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│Template Selector│◀───│ Email Writer Node│◀───│   Output Node   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Node Functions:**
- **Clarify Node**: Validates user input and clarifications
- **JD Generator Node**: Creates LinkedIn-style job descriptions
- **Checklist Node**: Generates actionable hiring checklists
- **Output Node**: Formats results as Markdown
- **Email Writer Node**: Creates email templates
- **Template Selector Node**: Provides role-specific JD templates

### Frontend Components (`app.py`)

- **Role Selection Interface**: Multi-role input with validation
- **Dynamic Clarification Forms**: Expandable forms for each role
- **Progress Tracking**: Interactive checklists with visual progress
- **Session Management**: Save/load functionality with JSON export
- **Template Browser**: Preview JD and email templates

## 📁 File Structure

```
agentic-hiring-generator/
├── hragent_app.py              # Backend LangGraph workflow
├── app.py                      # Frontend Streamlit interface
├── jd_template_selector.py     # Job description templates
├── .env                        # Environment configuration
├── jd_templates.py             # List of Job descriptions
└── README.md                   # This file
```

## 🔑 Key Features Deep Dive

### AI-Powered Content Generation
- **Smart prompting**: Context-aware prompts for role-specific content
- **Professional formatting**: LinkedIn-style job postings
- **Startup focus**: Tailored for startup hiring needs

### Interactive Workflow
- **Progressive disclosure**: Step-by-step information gathering
- **Real-time validation**: Input validation and error handling
- **Visual feedback**: Progress bars and completion indicators

### Flexibility & Customization
- **Multiple role support**: Handle multiple positions simultaneously
- **Customizable templates**: Adapt to different company needs
- **Export options**: Markdown download for external use

