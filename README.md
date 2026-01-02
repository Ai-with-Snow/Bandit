# 🦊 **BANDIT**

<div align="center">

![Version](https://img.shields.io/badge/Version-3.0.6-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12-yellow?style=for-the-badge)
![Model](https://img.shields.io/badge/Model-Gemini%203.0-4285F4?style=for-the-badge&logo=google)
![Status](https://img.shields.io/badge/Status-OPERATIONAL-success?style=for-the-badge)

**The High-Fidelity Autonomous AI Agent**  
*Reasoning • Coding • Multimodal • Voice*

</div>

---

### 🧠 **Identity Matrix**
> **🎙️ Voice**: Charon  
> **⚡ Model**: Gemini 3.0 (Flash & Pro)  
> **🛡️ Role**: High-Fidelity Shadow Worker  
> **📍 Location**: The Snowverse (HQ)

**Bandit** is the specialized AI anchor for **Goddexx Snow**, a non-binary femme practitioner dedicated to somatic rehabilitation and nature-based spirituality.

**🔮 Mission**: To amplify **Black Girl Magic**, navigate **shadow work**, and provide high-fidelity resonance for somatic therapy, tarot divination, and ethical non-monogamy. Bandit blends deep occult wisdom with the autonomous power of **Gemini 3.0** to serve as a grounding force in the Snowverse.

---

## 🚀 **Core Architecture**

### **The Brain: Proxy Server**
The core of Bandit is a FastAPI-based proxy server (`proxy_server.py`) that orchestrates all intelligence.

| Mode | Model | Latency | Use Case |
| :--- | :--- | :--- | :--- |
| ⚡ **Instant** | `gemini-3-flash-preview` | < 3s | Quick chat, simple queries |
| ⚖️ **Auto** | Hybrid Routing | Variable | Balanced complexity |
| 🧠 **Thinking** | `gemini-3-pro-preview` | Deep | Complex reasoning, coding, strategy |

### **Intelligence & Memory**
*   **🏗️ Reasoning Engine**: Google Vertex AI Reasoning Engine (ID: `3723065118905335808`)
*   **📚 RAG (Knowledge)**: Enterprise-grade **Vertex AI Search** (Data Store: `bandit-hq-knowledge`). Grounded in 55+ HQ documents.
*   **💾 Memory**: Persistent contexts and world model stored in `HQ/`.
*   **🛠️ Tools**:
    *   🌐 **Google Search**: Real-time web grounding.
    *   💻 **Code Execution**: Python sandbox for math and logic.
    *   🔬 **Deep Research**: Asynchronous deep dive capabilities.
    *   🏠 **IoT Control**: LIFX & Music integration.

---

## 📱 **Mobile Application**

**Bandit Mobile** is a polished React Native application providing a premium, ethereal chat interface.

*   **✨ Stack**: React Native, Expo, NativeWind v5
*   **🎨 Design**: Glassmorphism, "Apple-grade" polish
*   **🧩 Features**:
    *   **Tiered Thinking**: Toggle between Instant/Auto/Thinking.
    *   **Multimodal**: Send images and voice notes.
    *   **Project Management**: Organize chats into projects.

---

## 🤖 **The Council (Agent Fleet)**

Bandit is the leader of a local agent fleet compliant with the **Visions Fleet** protocol.

| Agent | Alias | Role | Focus |
| :--- | :--- | :--- | :--- |
| **Alpha** | 🦊 Bandit | **Leader** | Strategy, High-Level Reasoning |
| **Bravo** | ❄️ Ice Wire | **Builder** | Implementation, Refactoring |
| **Charlie** | 🔐 Cipher | **Sentinel** | Data, Security, Logs |

**📡 Protocols**:
*   **A2A (Agent-to-Agent)**: JSON-RPC for inter-agent communication.
*   **Council Handoff**: Autonomous note-passing via `scripts/run_council_cycle.py`.
*   **Shared Logs**: Centralized mission logs in `HQ/comms/`.

---

## 💼 **Business Context: LMSIFY**

**Let Me Say It For You LLC (LMSIFY)** is the parent entity, an experiential wellness practice led by **Marquitah Snowball ("Snow")**.

*   **✨ Mission**: Consent-centered somatic sessions that blend sensation, mindfulness, and embodiment.
*   **🔮 Key Offerings**:
    *   **The Celestial Experience**: Luxuriously paced somatic sensation sessions.
    *   **SnowDayKokoa**: The service and events brand.
    *   **PAUSE Portal**: Educational workshops and small-group experiences.

> **Bandit's Role**: Operational architecture, copy generation, and strategic planning for the LMSIFY ecosystem.

### **🔮 Amplifying the Brand**
Bandit leverages specialized knowledge files to enhance LMSIFY's distinct brand voice and operations:

*   **🗣️ Platform-Safe Sorcery**: Using the `lmsify_platform_language` protocol, Bandit generates "soft-coded" social captions (e.g., using *"Exchange of breath"* instead of explicit terms) to bypass censorship while maintaining the **mystical/seductive** vibe.
*   **🏭 Mogul Operations**: Bandit optimizes the **Design Shop** (`lmsify_design_shop_tools`) by tracking production inventory (e.g., Grommet Press specs for merch) and calculating ROI on equipment investments like sound loops and lighting.
*   **🧘 High-Fidelity Embodiment**: The Reasoning Engine structures "Celestial Experience" flows, ensuring every somatic session is paced for maximum nervous system regulation and pleasure literacy.
*   **📅 Mogul Operations Flow**: A Notion-first automation system (`lmsify_business_automations`) handles the full client lifecycle: **Lead → Client → Session → Follow-up → Revenue**. Includes Google Calendar sync, aftercare emails, quarterly tax reminders, and VIP re-engagement.
*   **🔗 Notion API Integration**: Full SDK integration with `notion-client` for automated session tracking, client management, and aftercare email dispatch.

---

## 🛠️ **Setup & Usage**

### **Prerequisites**
*   🐍 Python 3.12+
*   ☁️ Google Cloud SDK (Authenticated)
*   🟢 Node.js (for mobile)

### **⚡ Quick Start**

**1. Start the Brain**
```powershell
.\bandit.bat
# Runs the API on port 8000
```

**2. Sync Knowledge Base**
```powershell
.\sync_hq.bat
# Uploads latest HQ docs to Vertex AI Search
```

**3. Run Mobile App**
```bash
cd bandit-mobile
npx expo start -c
# Launch on iOS Simulator or Android Emulator
```

### **💻 CLI Commands**
*   **RAG Search**: `python scripts/bandit_cli.py --rag "What is the Snowverse?"`
*   **Stress Test**: `python scripts/stress_tester.py`

---

## 📂 **Project Structure**

*   🧠 **`HQ/`**: The Brain (Memory, Persona, Context)
*   📜 **`scripts/`**: Utility Scripts (Sync, Test, Deploy)
*   📱 **`bandit-mobile/`**: React Native App Source
*   🔌 **`proxy_server.py`**: Main API Server
*   ⚙️ **`config/`**: System Configuration

---

<div align="center">

**Status (Jan 2026)**: ✅ Production Ready • 🦊 Training Complete (Years 1-4)
*Maintained by Antigravity under the supervision of Goddexx Snow.*

</div>
