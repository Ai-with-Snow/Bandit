// Bandit Mobile - Main App with Chat Screen

import './global.css'; // Import NativeWind/Tailwind styles
import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  useWindowDimensions,
  Platform,
  KeyboardAvoidingView,
  ScrollView,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { theme } from './src/constants/theme';
import { ChatBubble } from './src/components/ChatBubble';
import { ChatInput } from './src/components/ChatInput';
import { ThinkingIndicator } from './src/components/ThinkingIndicator';
import { Sidebar } from './src/components/Sidebar';
import { Message, Conversation, Project, ThinkingMode, queryBandit, generateId, generateTitle } from './src/lib/api';
import { saveConversations, loadConversations, saveCurrentConversationId, loadCurrentConversationId, saveProjects, loadProjects } from './src/lib/storage';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

// Demo mode - no auth required
const DEMO_TOKEN = 'demo';

export default function App() {
  const { width } = useWindowDimensions();
  const isMobile = width < 768;
  const isTablet = width >= 768 && width < 1024;

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarState, setSidebarState] = useState<'hidden' | 'collapsed' | 'expanded'>(isMobile ? 'hidden' : 'expanded');
  const [thinkingMode, setThinkingMode] = useState<ThinkingMode>('instant');
  const [projectsExpanded, setProjectsExpanded] = useState(true);
  const [chatsExpanded, setChatsExpanded] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  // Update sidebar visibility on resize
  useEffect(() => {
    if (!isMobile && sidebarState === 'hidden') {
      setSidebarState('expanded');
    } else if (isMobile && sidebarState !== 'hidden') {
      setSidebarState('hidden');
    }
  }, [isMobile]);

  // Load saved conversations on mount
  useEffect(() => {
    loadData();
  }, []);

  // Save conversations when they change
  useEffect(() => {
    if (conversations.length > 0) {
      saveConversations(conversations);
    }
  }, [conversations]);

  // Save projects when they change
  useEffect(() => {
    if (projects.length > 0) {
      saveProjects(projects);
    }
  }, [projects]);

  // Save current conversation ID
  useEffect(() => {
    saveCurrentConversationId(currentConversation?.id || null);
  }, [currentConversation]);

  async function loadData() {
    const savedConvs = await loadConversations();
    const savedProjects = await loadProjects();
    const currentId = await loadCurrentConversationId();

    if (savedProjects.length > 0) setProjects(savedProjects);

    if (savedConvs.length > 0) {
      setConversations(savedConvs);
      // Removed auto-loading of last conversation
      // setCurrentConversation(null); // Explicitly ensure it's null on load
    }
  }

  function createProject(name: string, options?: { description?: string, color?: string, icon?: string }) {
    const newProject: Project = {
      id: Date.now().toString(),
      name,
      description: options?.description,
      color: options?.color,
      icon: options?.icon,
      createdAt: new Date(),
    };
    setProjects(prev => [...prev, newProject]);
  }

  function assignToProject(conversationId: string, projectId: string | undefined) {
    setConversations(prev => prev.map(c => {
      if (c.id === conversationId) {
        return { ...c, projectId, updatedAt: new Date() };
      }
      return c;
    }));

    // Update current if needed
    if (currentConversation?.id === conversationId) {
      setCurrentConversation(prev => prev ? { ...prev, projectId, updatedAt: new Date() } : null);
    }
  }

  function renameProject(projectId: string, newName: string) {
    setProjects(prev => prev.map(p => {
      if (p.id === projectId) {
        return { ...p, name: newName };
      }
      return p;
    }));
  }

  function moveConversation(conversationId: string, projectId: string | null) {
    setConversations(prev => prev.map(c => {
      if (c.id === conversationId) {
        return { ...c, projectId: projectId || undefined, updatedAt: new Date() };
      }
      return c;
    }));
    // Update current if needed
    if (currentConversation?.id === conversationId) {
      setCurrentConversation(prev => prev ? { ...prev, projectId: projectId || undefined, updatedAt: new Date() } : null);
    }
  }

  function renameConversation(id: string, newTitle: string) {
    setConversations(prev => prev.map(c => {
      if (c.id === id) {
        return { ...c, title: newTitle, updatedAt: new Date() };
      }
      return c;
    }));
    // Update current if needed
    if (currentConversation?.id === id) {
      setCurrentConversation(prev => prev ? { ...prev, title: newTitle, updatedAt: new Date() } : null);
    }
  }

  function deleteConversation(id: string) {
    setConversations(prev => prev.filter(c => c.id !== id));
    if (currentConversation?.id === id) {
      setCurrentConversation(null);
    }
  }

  function deleteProject(projectId: string) {
    setProjects(prev => prev.filter(p => p.id !== projectId));
    // Unassign chats in this project
    setConversations(prev => prev.map(c => {
      if (c.projectId === projectId) {
        return { ...c, projectId: undefined };
      }
      return c;
    }));
    // Update current if needed
    if (currentConversation?.projectId === projectId) {
      setCurrentConversation(prev => prev ? { ...prev, projectId: undefined } : null);
    }
  }

  function updateProject(projectId: string, updates: Partial<Project>) {
    setProjects(prev => prev.map(p => {
      if (p.id === projectId) {
        return { ...p, ...updates };
      }
      return p;
    }));
  }

  function startNewChat() {
    setCurrentConversation(null);
    if (isMobile) setSidebarState('hidden');
  }

  function selectConversation(id: string) {
    const conv = conversations.find(c => c.id === id);
    if (conv) {
      setCurrentConversation(conv);
      if (isMobile) setSidebarState('hidden');
    }
  }

  async function sendMessage(text: string, options?: { webSearch: boolean, attachments: any[] }) {
    if ((!text.trim() && (!options?.attachments || options.attachments.length === 0)) || isLoading) return;

    // Use text or a placeholder for the user message content if only attachments
    const content = text.trim() || (options?.attachments?.length ? "Sent an attachment" : "");

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: content,
      timestamp: new Date(),
      // Store attachments in message for display (images only for now in ui)
      attachments: options?.attachments,
    };

    // Create or update conversation
    let conv = currentConversation;
    if (!conv) {
      conv = {
        id: generateId(),
        title: generateTitle(content),
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };
    }

    // Add user message
    const updatedConv = {
      ...conv,
      messages: [...conv.messages, userMessage],
      updatedAt: new Date(),
    };

    setCurrentConversation(updatedConv);
    updateConversations(updatedConv);
    setIsLoading(true);

    // Scroll to bottom
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);

    // Query Bandit (Real API)
    try {
      // Helper to format attachments for API
      const apiAttachments = options?.attachments?.map(a => ({
        type: a.type,
        base64: a.base64 || "" // Ideally ensure base64 is present
      })).filter(a => a.base64) || [];

      // Use demo token for now, or fetch from storage if auth implemented
      const result = await queryBandit(
        text,
        'demo',
        thinkingMode,
        apiAttachments,
        options?.webSearch || false
      );

      if (result.success && result.response) {
        const banditMessage: Message = {
          id: generateId(),
          role: 'bandit',
          content: result.response,
          timestamp: new Date(),
        };

        const finalConv = {
          ...updatedConv,
          messages: [...updatedConv.messages, banditMessage],
          updatedAt: new Date(),
        };

        setCurrentConversation(finalConv);
        updateConversations(finalConv);
      } else {
        throw new Error(result.error || 'Failed to get response');
      }
    } catch (error) {
      const errorMessage: Message = {
        id: generateId(),
        role: 'bandit',
        content: `**Error**\n\nCould not connect to Bandit Reasoning Engine via Proxy.\n\nDetails: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };

      const errorConv = {
        ...updatedConv,
        messages: [...updatedConv.messages, errorMessage],
        updatedAt: new Date(),
      };

      setCurrentConversation(errorConv);
      updateConversations(errorConv);
    } finally {
      setIsLoading(false);
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }

  function updateConversations(conv: Conversation) {
    setConversations(prev => {
      const existing = prev.findIndex(c => c.id === conv.id);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = conv;
        return updated;
      }
      return [conv, ...prev];
    });
  }

  const messages = currentConversation?.messages || [];

  return (
    <LinearGradient
      // Ethereal gradient background
      colors={['#fce4ec', '#e0f7fa', '#e8eaf6', '#f3e5f5']}
      locations={[0, 0.3, 0.6, 1]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.container}
    >
      <SafeAreaView style={{ flex: 1, flexDirection: 'row' }}>
        <StatusBar style="dark" />

        {/* Collapsed Sidebar - Icon only */}
        {sidebarState === 'collapsed' && (
          <TouchableOpacity
            className="h-full w-14 p-3 pr-0"
            onPress={() => setSidebarState('expanded')}
          >
            <BlurView
              intensity={20}
              tint="light"
              className="h-full w-full flex-col items-center py-4 rounded-2xl border border-white/30 overflow-hidden"
              style={{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }}
            >
              <Ionicons name="menu" size={22} color="#3D3D3D" />
              <View className="mt-6">
                <Ionicons name="chatbubbles-outline" size={20} color="#5E5E5E" />
              </View>
              <View className="mt-4">
                <Ionicons name="folder-outline" size={20} color="#5E5E5E" />
              </View>
              {/* Spacer to push user icon to bottom */}
              <View className="flex-1" />
              {/* User icon at bottom - opens settings */}
              <TouchableOpacity
                className="w-8 h-8 rounded-full bg-[#E0D7FE] items-center justify-center mb-2"
                onPress={(e) => { e.stopPropagation(); setShowSettings(true); }}
              >
                <Ionicons name="person-outline" size={18} color="#3D3D3D" />
              </TouchableOpacity>
            </BlurView>
          </TouchableOpacity>
        )}

        {/* Expanded Sidebar */}
        {sidebarState === 'expanded' && (
          <View className="h-full w-1/3 max-w-[320px] min-w-[240px] p-3 pr-0">
            <BlurView
              intensity={20}
              tint="light"
              className="h-full w-full flex-col rounded-l-3xl rounded-r-lg border border-white/30 overflow-hidden"
              style={{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }}
            >
              <Sidebar
                conversations={conversations}
                projects={projects}
                currentId={currentConversation?.id || null}
                onSelect={selectConversation}
                onNewChat={startNewChat}
                onCreateProject={createProject}
                onRenameProject={renameProject}
                onAssignProject={assignToProject}
                onRenameConversation={renameConversation}
                onDeleteConversation={deleteConversation}
                onDeleteProject={deleteProject}
                onUpdateProject={updateProject}
                onClose={() => setSidebarState('collapsed')}
                onOpenSettings={() => setShowSettings(true)}
                projectsExpanded={projectsExpanded}
                setProjectsExpanded={setProjectsExpanded}
                chatsExpanded={chatsExpanded}
                setChatsExpanded={setChatsExpanded}
              />
            </BlurView>
          </View>
        )}

        {/* Main chat area */}
        <KeyboardAvoidingView
          style={styles.main}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
        >
          {/* Main Layout Container */}
          <View className="flex-1 p-4">
            <BlurView
              intensity={20}
              tint="light"
              className="flex-1 rounded-[24px] border border-white/20 overflow-hidden"
              style={{ backgroundColor: 'rgba(255, 255, 255, 0.15)' }}
            >
              {/* Settings View */}
              {showSettings ? (
                <>
                  {/* Settings Header */}
                  <View style={styles.header}>
                    <TouchableOpacity
                      style={styles.headerTitle}
                      onPress={() => setShowSettings(false)}
                    >
                      <Ionicons name="chevron-back" size={24} color="#3D3D3D" />
                      <Text style={[styles.headerTitleText, { color: '#3D3D3D', marginLeft: 8 }]}>Settings</Text>
                    </TouchableOpacity>
                  </View>

                  {/* Settings Content */}
                  <ScrollView style={{ flex: 1, padding: 20 }}>
                    {/* User Profile Section */}
                    <View style={{ alignItems: 'center', marginBottom: 32 }}>
                      <View style={{ width: 80, height: 80, borderRadius: 40, backgroundColor: '#E0D7FE', alignItems: 'center', justifyContent: 'center', marginBottom: 12 }}>
                        <Text style={{ fontSize: 32, color: '#3D3D3D', fontWeight: '600' }}>G</Text>
                      </View>
                      <Text style={{ fontSize: 20, fontWeight: '600', color: '#3D3D3D' }}>Goddexx Snow</Text>
                      <Text style={{ fontSize: 14, color: '#5E5E5E', marginTop: 4 }}>Pro Plan</Text>
                    </View>

                    {/* Settings Options */}
                    <View style={{ gap: 12 }}>
                      <TouchableOpacity style={{ flexDirection: 'row', alignItems: 'center', padding: 16, backgroundColor: 'rgba(255,255,255,0.5)', borderRadius: 12 }}>
                        <Ionicons name="person-outline" size={22} color="#3D3D3D" />
                        <Text style={{ marginLeft: 16, fontSize: 16, color: '#3D3D3D', flex: 1 }}>Account</Text>
                        <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
                      </TouchableOpacity>

                      <TouchableOpacity style={{ flexDirection: 'row', alignItems: 'center', padding: 16, backgroundColor: 'rgba(255,255,255,0.5)', borderRadius: 12 }}>
                        <Ionicons name="color-palette-outline" size={22} color="#3D3D3D" />
                        <Text style={{ marginLeft: 16, fontSize: 16, color: '#3D3D3D', flex: 1 }}>Appearance</Text>
                        <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
                      </TouchableOpacity>

                      <TouchableOpacity style={{ flexDirection: 'row', alignItems: 'center', padding: 16, backgroundColor: 'rgba(255,255,255,0.5)', borderRadius: 12 }}>
                        <Ionicons name="notifications-outline" size={22} color="#3D3D3D" />
                        <Text style={{ marginLeft: 16, fontSize: 16, color: '#3D3D3D', flex: 1 }}>Notifications</Text>
                        <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
                      </TouchableOpacity>

                      <TouchableOpacity style={{ flexDirection: 'row', alignItems: 'center', padding: 16, backgroundColor: 'rgba(255,255,255,0.5)', borderRadius: 12 }}>
                        <Ionicons name="shield-checkmark-outline" size={22} color="#3D3D3D" />
                        <Text style={{ marginLeft: 16, fontSize: 16, color: '#3D3D3D', flex: 1 }}>Privacy & Security</Text>
                        <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
                      </TouchableOpacity>

                      <TouchableOpacity style={{ flexDirection: 'row', alignItems: 'center', padding: 16, backgroundColor: 'rgba(255,255,255,0.5)', borderRadius: 12 }}>
                        <Ionicons name="help-circle-outline" size={22} color="#3D3D3D" />
                        <Text style={{ marginLeft: 16, fontSize: 16, color: '#3D3D3D', flex: 1 }}>Help & Support</Text>
                        <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
                      </TouchableOpacity>

                      <TouchableOpacity style={{ flexDirection: 'row', alignItems: 'center', padding: 16, backgroundColor: 'rgba(255,255,255,0.5)', borderRadius: 12, marginTop: 12 }}>
                        <Ionicons name="log-out-outline" size={22} color="#EF4444" />
                        <Text style={{ marginLeft: 16, fontSize: 16, color: '#EF4444', flex: 1 }}>Sign Out</Text>
                      </TouchableOpacity>
                    </View>

                    {/* App Version */}
                    <Text style={{ textAlign: 'center', color: '#9CA3AF', marginTop: 32, fontSize: 12 }}>Bandit v1.0.0</Text>
                  </ScrollView>
                </>
              ) : (
                <>
                  {/* Header */}
                  <View style={styles.header}>
                    <TouchableOpacity
                      style={styles.headerTitle}
                      onPress={() => setCurrentConversation(null)}
                    >
                      <Text style={[styles.headerTitleText, { color: '#3D3D3D' }]}>Bandit</Text>
                      <Text style={[styles.headerSubtitle, { color: '#5E5E5E' }]}>HQ Operator</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.newButton}
                      onPress={startNewChat}
                    >
                      <Ionicons name="create-outline" size={24} color={theme.colors.textMuted} />
                    </TouchableOpacity>
                  </View>

                  {/* Messages or welcome screen */}
                  <View style={styles.contentWrapper}>
                    {messages.length === 0 && !isLoading ? (
                      <View style={styles.welcome}>
                        <View style={[styles.welcomeLogo, { backgroundColor: '#E0D7FE' }]}>
                          <Text style={[styles.welcomeLogoText, { color: '#FFF' }]}>B</Text>
                        </View>
                        <Text style={[styles.welcomeTitle, { color: '#3D3D3D' }]}>How can I help you today?</Text>
                        <Text style={[styles.welcomeSubtitle, { color: '#5E5E5E' }]}>
                          I'm Bandit, your HQ Operator. Ask me anything.
                        </Text>

                        {/* Suggestion chips */}
                        <View style={styles.suggestions}>
                          {[
                            'What can you do?',
                            'Write a Python function',
                            'Explain distributed systems',
                          ].map((suggestion, index) => (
                            <TouchableOpacity
                              key={index}
                              style={[styles.suggestionChip, { backgroundColor: 'rgba(255,255,255,0.4)', borderColor: 'rgba(255,255,255,0.5)' }]}
                              onPress={() => sendMessage(suggestion)}
                            >
                              <Text style={[styles.suggestionText, { color: '#3D3D3D' }]}>{suggestion}</Text>
                              <Ionicons name="arrow-forward" size={16} color="#5E5E5E" />
                            </TouchableOpacity>
                          ))}
                        </View>

                        {/* Recent Chats Section */}
                        {conversations.length > 0 && (
                          <View style={styles.recentChats}>
                            <Text style={[styles.recentChatsTitle, { color: '#3D3D3D' }]}>Recent Chats</Text>
                            {conversations.slice(0, 3).map((conv) => (
                              <TouchableOpacity
                                key={conv.id}
                                style={[styles.recentChatChip, { borderColor: 'rgba(255,255,255,0.5)' }]}
                                onPress={() => selectConversation(conv.id)}
                              >
                                <View style={{ flex: 1 }}>
                                  <Text style={[styles.recentChatTitle, { color: '#3D3D3D' }]} numberOfLines={1}>{conv.title}</Text>
                                  <Text style={[styles.recentChatTime, { color: '#5E5E5E' }]}>
                                    {new Date(conv.updatedAt).toLocaleDateString()}
                                  </Text>
                                </View>
                                <Ionicons name="chatbubble-outline" size={16} color="#E0D7FE" />
                              </TouchableOpacity>
                            ))}
                          </View>
                        )}
                      </View>
                    ) : (
                      <FlatList
                        ref={flatListRef}
                        data={messages}
                        style={{ flex: 1 }}
                        keyExtractor={(item) => item.id}
                        renderItem={({ item }) => <ChatBubble message={item} />}
                        contentContainerStyle={styles.messageList}
                        ListFooterComponent={isLoading ? <ThinkingIndicator /> : null}
                        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
                        onLayout={() => flatListRef.current?.scrollToEnd({ animated: false })}
                        keyboardShouldPersistTaps="handled"
                        keyboardDismissMode="interactive"
                      />
                    )}

                    {/* Input */}
                    <View style={styles.inputWrapper}>
                      <ChatInput
                        onSend={sendMessage}
                        isLoading={isLoading}
                        thinkingMode={thinkingMode}
                        onSetThinkingMode={setThinkingMode}
                      />
                      {/* <View style={{ padding: 20 }}><Text>ChatInput Disabled</Text></View> */}
                    </View>
                  </View>
                </>
              )}
            </BlurView>
          </View>

          {/* Mobile Backdrop */}
          {isMobile && sidebarState === 'expanded' && (
            <TouchableOpacity
              style={styles.backdrop}
              activeOpacity={1}
              onPress={() => setSidebarState('hidden')}
            />
          )}
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

// Keeping some styles for now until full component refactor
const styles = StyleSheet.create({
  container: {
    flex: 1,
    width: '100%',
  },
  sidebar: {
    // Handled by tailwind
  },
  sidebarMobile: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    zIndex: 100,
    width: '80%',
    maxWidth: 300,
  },
  main: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    // borderBottomWidth: 1,
    // borderBottomColor: 'rgba(255,255,255,0.2)', // handled in view
  },
  menuButton: {
    padding: theme.spacing.sm,
    marginRight: 8,
  },
  headerTitle: {
    flex: 1,
    // alignItems: 'center', // Align left for new design
  },
  headerTitleText: {
    fontSize: theme.fontSize.lg,
    fontWeight: '700',
  },
  headerSubtitle: {
    fontSize: theme.fontSize.xs,
  },
  newButton: {
    padding: theme.spacing.sm,
  },
  welcome: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.lg,
  },
  welcomeLogo: {
    width: 64,
    height: 64,
    borderRadius: theme.borderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: theme.spacing.lg,
  },
  welcomeLogoText: {
    fontSize: 32,
    fontWeight: '700',
  },
  welcomeTitle: {
    fontSize: theme.fontSize.xl,
    fontWeight: '600',
    marginBottom: theme.spacing.sm,
  },
  welcomeSubtitle: {
    fontSize: theme.fontSize.md,
    textAlign: 'center',
    marginBottom: theme.spacing.xl,
  },
  suggestions: {
    width: '100%',
    maxWidth: 400,
  },
  suggestionChip: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 1,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.sm,
  },
  suggestionText: {
    fontSize: theme.fontSize.sm,
    flex: 1,
  },
  messageList: {
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: 20, // Added padding
    paddingBottom: 20,
  },
  contentWrapper: {
    flex: 1,
    width: '100%',
  },
  inputWrapper: {
    marginBottom: 0,
    padding: 20, // Added padding around input
  },
  backdrop: {
    position: 'absolute',
    left: 0,
    top: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.4)',
    zIndex: 90,
  },
  recentChats: {
    width: '100%',
    maxWidth: 400,
    marginTop: theme.spacing.xl,
  },
  recentChatsTitle: {
    fontSize: theme.fontSize.sm,
    fontWeight: '600',
    marginBottom: theme.spacing.sm,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  recentChatChip: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.sm,
  },
  recentChatTitle: {
    fontSize: theme.fontSize.md,
    fontWeight: '500',
    marginBottom: 2,
  },
  recentChatTime: {
    fontSize: theme.fontSize.xs,
  },
});
