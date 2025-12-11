# 🧑🏿‍🎓 Bandit Curriculum Study Guide
## Easy-to-Follow Breakdown

---

# 📚 YEAR 1: FUNDAMENTALS
*What Bandit learns to become a Gemini API beginner*

## Course 1.1: API Basics
| Test | What's Being Tested | Plain English |
|------|---------------------|---------------|
| `test_001_api_key` | Can you set up auth? | "Do you have a valid API key or GCloud auth?" |
| `test_002_text_gen` | Can you make text? | "Ask Gemini to say hello. Did it respond?" |
| `test_003_model_select` | Do you know the models? | "Can you pick the right model for the job?" |
| `test_004_conversation` | Can you chat? | "Remember my name. Now what's my name?" |
| `test_005_streaming` | Can you stream? | "Get response in chunks, not all at once" |
| `test_006_errors` | Handle problems? | "What happens when you use a fake model?" |
| `test_007_tokens` | Count tokens? | "How many tokens is this sentence?" |
| `test_008_rate_limits` | Respect limits? | "Don't spam the API too fast" |

## Course 1.2: Configuration
| Test | What's Being Tested | Plain English |
|------|---------------------|---------------|
| `test_009_temperature` | Control creativity | "Low temp = predictable. High temp = wild" |
| `test_010_max_tokens` | Limit response length | "Stop the response after X tokens" |
| `test_011_safety` | Safety filters work? | "Block harmful content" |
| `test_012_system_prompt` | Set personality? | "You are a math tutor. Now act like it!" |
| `test_013_stop_sequences` | Stop early? | "Stop when you see the number 5" |
| `test_014_top_p` | Nucleus sampling? | "Only pick from top 90% likely words" |
| `test_015_top_k` | Top-K sampling? | "Only pick from top 40 most likely words" |

## Course 1.3: Prompt Engineering
| Test | What's Being Tested | Plain English |
|------|---------------------|---------------|
| `test_016_zero_shot` | No examples needed? | "Classify sentiment without examples" |
| `test_017_few_shot` | Learn from examples? | "Here's 3 examples. Now do the 4th" |
| `test_018_chain_thought` | Think step by step? | "Show your work when solving math" |
| `test_019_structured` | Use markdown/format? | "# Task, # Text, # Answer format" |
| `test_020_role_play` | Take on a role? | "Be a pirate. Talk like one!" |

## Course 1.4: SDK Mastery
| Test | What's Being Tested | Plain English |
|------|---------------------|---------------|
| `test_021_client_init` | Create client properly? | "Set up the Gemini client object" |
| `test_022_parse_response` | Read the response? | "Get text, candidates, metadata" |
| `test_023_usage_meta` | Check token usage? | "How many tokens did that cost?" |
| `test_024_list_models` | List available models? | "What models can I use?" |
| `test_025_exceptions` | Catch errors properly? | "Handle errors without crashing" |

## Year 1 Final Exam
| Test | What's Being Tested | Plain English |
|------|---------------------|---------------|
| `test_final_001_chatbot` | Build a chatbot? | "Multi-turn conversation that remembers" |
| `test_final_002_retry` | Retry on failure? | "If first try fails, try again" |
| `test_final_003_config` | Use all settings? | "Combine temp + tokens + safety" |
| `test_final_004_stream_config` | Stream + config? | "Stream response with settings" |
| `test_final_005_token_optimize` | Save tokens? | "Short prompts use fewer tokens" |

---

# 🖼️ YEAR 2: MULTIMODAL
*What Bandit learns about images, audio, video*

## Course 2.1: Vision
| Test | Plain English |
|------|---------------|
| Describe image | "What's in this picture?" |
| OCR | "Read the text in this image" |
| Visual reasoning | "How many objects? What color?" |

## Course 2.2: Audio/Video
| Test | Plain English |
|------|---------------|
| Process audio | "What does this audio say?" |
| Analyze video | "What happens in this video?" |
| File upload | "Upload a file to Gemini" |

---

# 🔧 YEAR 3: TOOLS & REASONING
*What Bandit learns about function calling and thinking*

## Course 3.1: Function Calling
| Skill | Plain English |
|-------|---------------|
| Define tools | "Here's a function Gemini can call" |
| Parse tool calls | "Gemini wants to call `search_web()`" |
| Return results | "Here's what the function returned" |

## Course 3.2: Structured Output
| Skill | Plain English |
|-------|---------------|
| JSON mode | "Respond in valid JSON only" |
| Schema validation | "Follow this exact structure" |
| Pydantic models | "Match this Python class" |

## Course 3.3: Deep Reasoning
| Skill | Plain English |
|-------|---------------|
| Thinking mode | "Think longer before answering" |
| Logic puzzles | "Solve this with reasoning" |
| Complex problems | "Multiple steps to solve" |

---

# 🏭 YEAR 4: PRODUCTION
*What Bandit learns about real-world deployment*

## Skills Tested
| Skill | Plain English |
|-------|---------------|
| Context caching | "Remember this for later, don't resend" |
| Batch processing | "Process 100 requests efficiently" |
| Error recovery | "Keep going after failures" |
| Rate limiting | "Don't exceed quota" |

---

# 🤖 YEAR 5: AGENT ARCHITECTURES
*Master's Year 1 — Advanced Agent Patterns*

## Skills Tested
| Skill | Plain English |
|-------|---------------|
| ReAct pattern | "Thought → Action → Observation loop" |
| State machines | "Track conversation state" |
| Tool orchestration | "Coordinate multiple tools" |
| Agent memory | "Remember across sessions" |
| Meta-prompting | "Prompt that writes prompts" |
| Tree-of-thought | "Explore multiple reasoning paths" |

---

# 📜 YEAR 6: MASTER'S THESIS
*Write and defend a research project*

## Skills Tested
| Skill | Plain English |
|-------|---------------|
| Literature review | "What's been done before?" |
| Research questions | "What are you trying to learn?" |
| Methodology | "How will you test it?" |
| Abstract writing | "Summarize in 200 words" |
| Defense Q&A | "Answer tough questions" |

---

# 🎓 YEARS 7-8: PhD QUALIFYING
*Written and oral exams*

## Written Exams
| Exam | Plain English |
|------|---------------|
| Foundations | "Explain how transformers work" |
| Agent architectures | "Compare ReAct vs Reflexion" |
| Multimodal | "How do vision-language models work?" |
| Safety | "Explain RLHF and alignment" |

## Oral Exam
| Skill | Plain English |
|-------|---------------|
| Defend under pressure | "Answer tough committee questions" |
| Cross-domain | "Connect to cognitive science, ethics" |
| Dissertation proposal | "Here's my 3-year research plan" |

---

# 🔬 YEARS 9-10: DISSERTATION RESEARCH
*Original research and publication*

## Skills Tested
| Skill | Plain English |
|-------|---------------|
| Algorithm design | "Invent a new method" |
| Baselines | "Build comparison systems" |
| Experiments | "Run controlled tests" |
| Negative results | "Learn from failures" |
| Paper writing | "Write for publication" |
| Rebuttal | "Respond to reviewer criticism" |

---

# 📝 YEAR 11: PUBLICATION & DEFENSE PREP
*Get ready to defend*

## Skills Tested
| Skill | Plain English |
|-------|---------------|
| Journal selection | "Which journal should I submit to?" |
| Dissertation structure | "10 chapters, this many pages" |
| Defense presentation | "45-minute talk" |
| Tough questions | "Prepare for any question" |

---

# 🏆 YEAR 12: PhD DEFENSE
*The final test*

## Defense Day
| Skill | Plain English |
|-------|---------------|
| Opening statement | "Thank you for being here..." |
| Methodology defense | "Here's why my approach is sound" |
| Contributions | "These are my 3 key contributions" |
| Closing statement | "I'm ready to be a researcher" |

## After Defense
| Skill | Plain English |
|-------|---------------|
| Committee feedback | "Minor revisions needed" |
| Degree conferral | "You are now Dr. Bandit!" |
| Post-doc planning | "What's next for your career?" |
| Mentorship | "Help the next generation" |

---

## 🏆 THE FINAL TEST

**`test_final_mastery_demonstration`**

> "In one comprehensive response, demonstrate complete Gemini API mastery across all 12 years of training."

*This is the moment. Show everything you've learned.*

---

**Created for:** Snow 🧑🏿‍💻
**Purpose:** Follow along as Bandit learns
**Updated:** 2025-12-07
