# Alpha → Bravo: UX Enhancement Notes
## Session: 2025-12-12 21:15 EST

---

### 🎯 MISSION OBJECTIVE
**Increase UX polish to Apple-grade premium feel.**

---

## ✅ WHAT'S WORKING WELL

| Element | Status | Notes |
|---------|--------|-------|
| Light/Iridescent Theme | ✅ | Consistent across sidebar & main area |
| Sidebar Organization | ✅ | Clear sections: New chat, Projects, Your chats, Profile |
| Spacing | ✅ | Felt balanced, not cramped |
| Chat History Display | ✅ | Clean and readable |
| Sidebar Hover States | ✅ | Background color change visible on "New chat" and chat items |

---

## 🚨 PRIORITY FIXES REQUIRED

### 1. 🔴 MODE SELECTOR MISSING (P0)
**Problem:** The Auto/Instant/Thinking mode selector is NOT visible anywhere.  
**Location:** Should be near chat input or in header  
**Impact:** Users can't access deep thinking mode - core feature hidden  

**BRAVO FIX:**
```
Add mode selector dropdown/toggle adjacent to chat input or in the header.
Options: ⚡ Instant | 🔄 Auto | 🧠 Thinking
Default: Instant (already set in state)
```

---

### 2. 🟠 "NEW CHAT" BEHAVIOR (P1)
**Problem:** Clicking "New chat" doesn't show the input field immediately. User stays on welcome screen.  
**Expected:** Immediate transition to empty chat with input focused  
**Impact:** Confusing UX - "Where do I type?"  

**BRAVO FIX:**
```tsx
// When "New chat" clicked:
1. Create new empty conversation
2. Navigate to chat view (not welcome screen)
3. Auto-focus the input field
```

---

### 3. 🟠 SEND BUTTON HOVER STATE (P1)
**Problem:** Send button [27] shows no visual change on hover  
**Expected:** Scale up, color shift, or glow effect  
**Impact:** Feels unresponsive, not premium  

**BRAVO FIX:**
```css
/* Add to ChatInput send button */
.send-btn:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: all 0.2s ease;
}

.send-btn:active {
  transform: scale(0.95);
}
```

---

### 4. 🟡 SEND BUTTON DISABLED STATE (P2)
**Problem:** Send button appears faded when input is empty, but no tooltip explains why  
**Expected:** Clear visual indication + optional tooltip  

**BRAVO FIX:**
```tsx
// Add tooltip or aria-label
<Pressable 
  disabled={!inputText.trim()}
  accessibilityHint="Type a message to send"
>
```

---

### 5. 🟡 INPUT FIELD PLACEHOLDER (P2)
**Problem:** Generic placeholder "Type a message..."  
**Expected:** Dynamic, engaging placeholder  

**BRAVO FIX:**
```tsx
// Rotating placeholders
const placeholders = [
  "Ask me anything...",
  "What's on your mind?",
  "How can I help, Snow?",
  "⚡ Type for instant response..."
];
```

---

## 📸 SCREENSHOTS CAPTURED

| Screenshot | Description |
|------------|-------------|
| `ux_initial_view_*.png` | Welcome screen with sidebar |
| `ux_chat_view_*.png` | Chat history with input |
| `ux_send_hover_*.png` | Send button hover (no change visible) |
| `ux_newchat_hover_*.png` | New chat button hover (working) |

Location: `~/.gemini/antigravity/brain/127be0e0-06c7-4ae8-b719-01895fc5167f/`

---

## 📋 PRIORITY ORDER FOR BRAVO

1. **P0** - Add Mode Selector (critical feature hidden)
2. **P1** - Fix "New chat" navigation flow
3. **P1** - Add send button hover state
4. **P2** - Send button disabled tooltip
5. **P2** - Dynamic placeholder text

---

**Alpha signing off. Awaiting Bravo acknowledgment.**
over.
