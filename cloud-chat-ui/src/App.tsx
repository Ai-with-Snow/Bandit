/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useRef, useEffect } from "react";
import { GoogleGenAI } from "@google/genai";
import { Send, Bot, User, Loader2, Sparkles, Trash2, Plus, X, Image as ImageIcon, FileText, Search, Microscope, Volume2, Video, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import ReactMarkdown from "react-markdown";

const BANDIT_API_BASE = "https://bandit-849984150802.us-central1.run.app";

interface Attachment {
  id: string;
  name: string;
  type: string;
  data?: string;
}

interface Message {
  id: string;
  role: "user" | "model";
  text: string;
  timestamp: Date;
  attachments?: Attachment[];
  isResearch?: boolean;
  isSearch?: boolean;
  isVideo?: boolean;
  videoUrl?: string;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [searchMode, setSearchMode] = useState(false);
  const [researchMode, setResearchMode] = useState(false);
  const [videoMode, setVideoMode] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [showKeyWarning, setShowKeyWarning] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach(file => {
      const reader = new FileReader();
      reader.onload = (event) => {
        const newAttachment: Attachment = {
          id: Math.random().toString(36).substr(2, 9),
          name: file.name,
          type: file.type,
          data: event.target?.result as string
        };
        setAttachments(prev => [...prev, newAttachment]);
      };
      reader.readAsDataURL(file);
    });
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removeAttachment = (id: string) => {
    setAttachments(prev => prev.filter(a => a.id !== id));
  };

  const pollResearch = async (interactionId: string, messageId: string) => {
    const poll = async () => {
      try {
        const res = await fetch(`${BANDIT_API_BASE}/research/${interactionId}`);
        const data = await res.json();
        
        if (data.status === "completed" || data.report) {
          setMessages(prev => prev.map(m => 
            m.id === messageId 
              ? { ...m, text: data.report || data.response || "Research complete." } 
              : m
          ));
          setIsLoading(false);
          return true;
        }
        return false;
      } catch (e) {
        console.error("Polling error", e);
        return true; // Stop on error
      }
    };

    const interval = setInterval(async () => {
      const done = await poll();
      if (done) clearInterval(interval);
    }, 5000);
  };

  const handleVideoGeneration = async (prompt: string, messageId: string) => {
    try {
      const hasKey = await (window as any).aistudio.hasSelectedApiKey();
      if (!hasKey) {
        await (window as any).aistudio.openSelectKey();
      }

      const apiKey = (process.env as any).API_KEY || process.env.GEMINI_API_KEY;
      const ai = new GoogleGenAI({ apiKey });
      
      let operation = await ai.models.generateVideos({
        model: 'veo-3.1-fast-generate-preview',
        prompt: prompt,
        config: {
          numberOfVideos: 1,
          resolution: '720p',
          aspectRatio: '16:9'
        }
      });

      while (!operation.done) {
        await new Promise(resolve => setTimeout(resolve, 10000));
        operation = await ai.operations.getVideosOperation({operation: operation});
      }

      const downloadLink = operation.response?.generatedVideos?.[0]?.video?.uri;
      if (downloadLink) {
        const response = await fetch(downloadLink, {
          method: 'GET',
          headers: {
            'x-goog-api-key': apiKey || "",
          },
        });
        const blob = await response.blob();
        const videoUrl = URL.createObjectURL(blob);
        
        setMessages(prev => prev.map(m => 
          m.id === messageId 
            ? { ...m, text: "Neural rendering complete. Previewing video link below.", videoUrl } 
            : m
        ));
      }
    } catch (error: any) {
      console.error("Video generation error:", error);
      if (error.message?.includes("Requested entity was not found")) {
        await (window as any).aistudio.openSelectKey();
      }
      setMessages(prev => prev.map(m => 
        m.id === messageId 
          ? { ...m, text: "System Error: Video rendering failed. Please ensure you have a valid paid API key selected." } 
          : m
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async () => {
    if ((!input.trim() && attachments.length === 0) || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      text: input.trim(),
      timestamp: new Date(),
      attachments: [...attachments],
      isSearch: searchMode,
      isResearch: researchMode,
      isVideo: videoMode
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setAttachments([]);
    setIsLoading(true);

    // Intent detection for video generation
    const isVideoGenerationIntent = /generate|make|create|render|build/i.test(userMessage.text) && /video|movie|clip|animation/i.test(userMessage.text);

    if (videoMode || isVideoGenerationIntent) {
      const aiMessageId = (Date.now() + 1).toString();
      const aiMessage: Message = {
        id: aiMessageId,
        role: "model",
        text: "Bandit has detected a video generation request. Initializing the Veo neural engine now...",
        timestamp: new Date(),
        isVideo: true
      };
      setMessages((prev) => [...prev, aiMessage]);
      handleVideoGeneration(userMessage.text, aiMessageId);
      return;
    }

    try {
      let endpoint = "/chat";
      let body: any = { message: userMessage.text };

      if (researchMode) {
        endpoint = "/research";
        body = { topic: userMessage.text };
      } else if (searchMode || /video|link|url|watch/i.test(userMessage.text)) {
        // Auto-switch to search if asking for links/videos
        endpoint = "/search";
        body = { query: userMessage.text };
      } else if (attachments.length > 0) {
        body = { 
          message: userMessage.text || "Analyze these attachments",
          prompt: userMessage.attachments?.map(a => `[File: ${a.name}]`).join("\n")
        };
      }

      const response = await fetch(`${BANDIT_API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (researchMode && data.interaction_id) {
        const aiMessageId = (Date.now() + 1).toString();
        const aiMessage: Message = {
          id: aiMessageId,
          role: "model",
          text: "Bandit is conducting deep research. This may take a few minutes...",
          timestamp: new Date(),
          isResearch: true
        };
        setMessages((prev) => [...prev, aiMessage]);
        pollResearch(data.interaction_id, aiMessageId);
      } else {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "model",
          text: data.response || data.text || "Bandit has processed your request.",
          timestamp: new Date(),
          isSearch: searchMode || endpoint === "/search"
        };
        setMessages((prev) => [...prev, aiMessage]);
        setIsLoading(false);
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [...prev, {
        id: Date.now().toString(),
        role: "model",
        text: "System Error: Bandit's neural link was interrupted. The Proxy API might be down.",
        timestamp: new Date(),
      }]);
      setIsLoading(false);
    }
  };

  const speakMessage = async (text: string) => {
    if (isPlayingAudio) return;
    setIsPlayingAudio(true);
    try {
      const res = await fetch(`${BANDIT_API_BASE}/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, voice: "Charon" })
      });
      const data = await res.json();
      if (data.audio) {
        const audio = new Audio(`data:${data.format || 'audio/wav'};base64,${data.audio}`);
        audio.onended = () => setIsPlayingAudio(false);
        audio.play();
      } else {
        setIsPlayingAudio(false);
      }
    } catch (e) {
      console.error("TTS error", e);
      setIsPlayingAudio(false);
    }
  };

  return (
    <div className="relative flex flex-col h-screen overflow-hidden bg-[#050505] text-white font-sans selection:bg-purple-500/30">
      {/* Iridescent Background Blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] rounded-full bg-purple-600/20 blur-[120px] animate-pulse" />
        <div className="absolute top-[20%] -right-[10%] w-[35%] h-[35%] rounded-full bg-blue-600/20 blur-[120px] animate-pulse [animation-delay:2s]" />
        <div className="absolute -bottom-[10%] left-[20%] w-[45%] h-[45%] rounded-full bg-emerald-600/10 blur-[120px] animate-pulse [animation-delay:4s]" />
      </div>

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-8 py-6 backdrop-blur-xl bg-white/5 border-b border-white/10">
        <div className="flex items-center gap-4">
          <motion.div 
            whileHover={{ scale: 1.1, rotate: 5 }}
            className="p-3 bg-gradient-to-br from-purple-500 via-fuchsia-500 to-blue-500 rounded-2xl shadow-[0_0_20px_rgba(168,85,247,0.4)]"
          >
            <Bot size={24} className="text-white" />
          </motion.div>
          <div>
            <h1 className="text-2xl font-bold tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/50">
              BANDIT <span className="text-xs font-black bg-white/10 px-2 py-0.5 rounded ml-2 border border-white/10">PROXY v3</span>
            </h1>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              <p className="text-[10px] uppercase tracking-[0.2em] font-bold text-emerald-500/80">Neural Link Active</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => {
              setSearchMode(!searchMode);
              setResearchMode(false);
              setVideoMode(false);
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl border transition-all ${
              searchMode ? "bg-blue-500/20 border-blue-500 text-blue-400" : "bg-white/5 border-white/10 text-white/40 hover:text-white"
            }`}
          >
            <Search size={16} />
            <span className="text-xs font-bold uppercase tracking-wider">Search</span>
          </button>
          <button
            onClick={() => {
              setResearchMode(!researchMode);
              setSearchMode(false);
              setVideoMode(false);
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl border transition-all ${
              researchMode ? "bg-purple-500/20 border-purple-500 text-purple-400" : "bg-white/5 border-white/10 text-white/40 hover:text-white"
            }`}
          >
            <Microscope size={16} />
            <span className="text-xs font-bold uppercase tracking-wider">Research</span>
          </button>
          <button
            onClick={() => {
              setVideoMode(!videoMode);
              setSearchMode(false);
              setResearchMode(false);
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl border transition-all ${
              videoMode ? "bg-emerald-500/20 border-emerald-500 text-emerald-400" : "bg-white/5 border-white/10 text-white/40 hover:text-white"
            }`}
          >
            <Video size={16} />
            <span className="text-xs font-bold uppercase tracking-wider">Video</span>
          </button>
          <button
            onClick={() => setMessages([])}
            className="p-2.5 text-white/40 hover:text-white hover:bg-white/10 rounded-xl transition-all border border-transparent hover:border-white/10"
          >
            <Trash2 size={20} />
          </button>
        </div>
      </header>

      {/* Chat Area */}
      <main className="relative z-10 flex-1 overflow-y-auto px-4 py-12 custom-scrollbar">
        <div className="max-w-4xl mx-auto space-y-10">
          {messages.length === 0 ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-[50vh] text-center"
            >
              <div className="relative mb-8">
                <div className="absolute inset-0 bg-purple-500/30 blur-3xl rounded-full animate-pulse" />
                <Bot size={80} className="relative text-white/20" />
              </div>
              <h2 className="text-4xl font-light tracking-tight text-white mb-4">
                Wake up, <span className="font-bold italic text-purple-400">Bandit</span> is here.
              </h2>
              <p className="text-white/40 max-w-md leading-relaxed">
                Connected to the Proxy API. I can now perform deep research, web searches, and analyze your files. Toggle **Video** mode to generate cinematic previews.
              </p>
            </motion.div>
          ) : (
            <AnimatePresence mode="popLayout">
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  className={`flex gap-6 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
                >
                  <div className={`flex-shrink-0 w-12 h-12 rounded-2xl flex items-center justify-center shadow-lg transform transition-transform hover:scale-110 ${
                    msg.role === "user" 
                      ? "bg-white/10 border border-white/20 text-white" 
                      : "bg-gradient-to-br from-purple-600 to-blue-600 text-white"
                  }`}>
                    {msg.role === "user" ? <User size={24} /> : <Bot size={24} />}
                  </div>
                  
                  <div className="flex flex-col gap-2 max-w-[80%]">
                    <div className={`relative group perspective-1000`}>
                      <div className={`
                        px-6 py-4 rounded-[2rem] backdrop-blur-2xl border transition-all duration-500
                        hover:rotate-x-1 hover:rotate-y-1 hover:shadow-[0_20px_50px_rgba(0,0,0,0.3)]
                        ${msg.role === "user" 
                          ? "bg-white/10 border-white/20 rounded-tr-none text-white/90" 
                          : "bg-purple-500/10 border-purple-500/30 rounded-tl-none text-white"}
                      `}>
                        {/* Mode Indicators */}
                        {(msg.isSearch || msg.isResearch || msg.isVideo) && (
                          <div className="flex gap-2 mb-3">
                            {msg.isSearch && <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-[10px] font-bold rounded border border-blue-500/30 uppercase tracking-tighter">Search Grounded</span>}
                            {msg.isResearch && <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 text-[10px] font-bold rounded border border-purple-500/30 uppercase tracking-tighter">Deep Research</span>}
                            {msg.isVideo && <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-bold rounded border border-emerald-500/30 uppercase tracking-tighter">Veo Video Engine</span>}
                          </div>
                        )}

                        {/* Attachments in message */}
                        {msg.attachments && msg.attachments.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-4">
                            {msg.attachments.map(att => (
                              <div key={att.id} className="flex items-center gap-2 px-3 py-1.5 bg-black/40 rounded-full border border-white/10 text-[10px] font-medium">
                                {att.type.startsWith('image/') ? <ImageIcon size={12} /> : <FileText size={12} />}
                                <span className="truncate max-w-[100px]">{att.name}</span>
                              </div>
                            ))}
                          </div>
                        )}
                        
                        <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10">
                          <ReactMarkdown>{msg.text}</ReactMarkdown>
                        </div>

                        {msg.videoUrl && (
                          <div className="mt-4 rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
                            <video 
                              src={msg.videoUrl} 
                              controls 
                              autoPlay 
                              loop 
                              className="w-full aspect-video object-cover"
                            />
                            <div className="p-3 bg-black/40 backdrop-blur-md flex justify-between items-center">
                              <span className="text-[10px] font-bold uppercase tracking-widest text-white/40">Bandit Neural Render // 720p</span>
                              <a 
                                href={msg.videoUrl} 
                                download="bandit-render.mp4"
                                className="text-[10px] font-bold uppercase tracking-widest text-emerald-400 hover:text-emerald-300 transition-colors"
                              >
                                Download Link
                              </a>
                            </div>
                          </div>
                        )}

                        {msg.role === "model" && !msg.videoUrl && (
                          <button 
                            onClick={() => speakMessage(msg.text)}
                            className={`mt-4 p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors ${isPlayingAudio ? "text-purple-400 animate-pulse" : "text-white/40"}`}
                          >
                            <Volume2 size={16} />
                          </button>
                        )}
                      </div>
                      <div className={`text-[10px] mt-2 font-bold tracking-widest uppercase opacity-30 ${msg.role === "user" ? "text-right" : "text-left"}`}>
                        {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          )}
          
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-6">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center animate-pulse">
                <Bot size={24} />
              </div>
              <div className="px-6 py-4 bg-white/5 border border-white/10 rounded-[2rem] rounded-tl-none backdrop-blur-xl">
                <div className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" />
                  <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                  <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Area */}
      <footer className="relative z-20 p-8">
        <div className="max-w-4xl mx-auto">
          {/* Video Key Warning */}
          <AnimatePresence>
            {videoMode && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="mb-4 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl backdrop-blur-xl flex items-center gap-4"
              >
                <AlertCircle className="text-emerald-400 shrink-0" size={20} />
                <div className="flex-1">
                  <p className="text-xs text-emerald-400 font-bold uppercase tracking-wider">Video Mode Active</p>
                  <p className="text-[10px] text-white/60">Veo requires a paid API key. You will be prompted to select one if not already configured.</p>
                </div>
                <a 
                  href="https://ai.google.dev/gemini-api/docs/billing" 
                  target="_blank" 
                  className="text-[10px] font-bold underline text-white/40 hover:text-white"
                >
                  Billing Docs
                </a>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Attachment Preview Bar */}
          <AnimatePresence>
            {attachments.length > 0 && (
              <motion.div 
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="flex flex-wrap gap-3 mb-4 p-4 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-xl"
              >
                {attachments.map(att => (
                  <motion.div 
                    layout
                    key={att.id}
                    className="relative group flex items-center gap-3 px-4 py-2 bg-black/40 border border-white/10 rounded-xl"
                  >
                    {att.type.startsWith('image/') ? <ImageIcon size={16} className="text-purple-400" /> : <FileText size={16} className="text-blue-400" />}
                    <span className="text-xs font-medium truncate max-w-[150px]">{att.name}</span>
                    <button 
                      onClick={() => removeAttachment(att.id)}
                      className="p-1 hover:bg-white/10 rounded-md transition-colors"
                    >
                      <X size={14} />
                    </button>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          <div className="relative group">
            {/* Iridescent Border Glow */}
            <div className="absolute -inset-[1px] bg-gradient-to-r from-purple-500 via-blue-500 to-emerald-500 rounded-[2.5rem] opacity-20 group-focus-within:opacity-100 blur-sm transition-opacity" />
            
            <div className="relative flex items-end gap-2 p-2 bg-[#121212]/80 backdrop-blur-3xl border border-white/10 rounded-[2.5rem]">
              <input 
                type="file" 
                multiple 
                className="hidden" 
                ref={fileInputRef} 
                onChange={handleFileSelect}
              />
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="p-4 text-white/40 hover:text-white hover:bg-white/10 rounded-full transition-all"
              >
                <Plus size={24} />
              </button>
              
              <textarea
                rows={1}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder={videoMode ? "Describe the video you want to render..." : researchMode ? "Enter research topic..." : searchMode ? "Search the web..." : "Message Bandit..."}
                className="flex-1 bg-transparent border-none focus:ring-0 py-4 px-2 text-white placeholder:text-white/20 resize-none max-h-40"
              />
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSend}
                disabled={(!input.trim() && attachments.length === 0) || isLoading}
                className={`p-4 rounded-full transition-all ${
                  (input.trim() || attachments.length > 0) && !isLoading
                    ? "bg-white text-black shadow-[0_0_20px_rgba(255,255,255,0.3)]"
                    : "bg-white/5 text-white/20 cursor-not-allowed"
                }`}
              >
                {isLoading ? <Loader2 className="animate-spin" size={24} /> : <Send size={24} />}
              </motion.button>
            </div>
          </div>
          <p className="text-[10px] text-center text-white/20 mt-4 uppercase tracking-[0.3em] font-bold">
            Bandit Proxy Protocol v3.0 // Veo Neural Engine Enabled
          </p>
        </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
        .perspective-1000 { perspective: 1000px; }
        .rotate-x-1 { transform: rotateX(2deg); }
        .rotate-y-1 { transform: rotateY(2deg); }
      `}} />
    </div>
  );
}
