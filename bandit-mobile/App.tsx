// Bandit Mobile - Main App with Chat Screen

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Dimensions,
  Platform,
  KeyboardAvoidingView,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { theme } from './src/constants/theme';
import { ChatBubble } from './src/components/ChatBubble';
import { ChatInput } from './src/components/ChatInput';
import { ThinkingIndicator } from './src/components/ThinkingIndicator';
import { Sidebar } from './src/components/Sidebar';
import { Message, Conversation, queryBandit, generateId, generateTitle } from './src/lib/api';
import { saveConversations, loadConversations, saveCurrentConversationId, loadCurrentConversationId } from './src/lib/storage';

const { width } = Dimensions.get('window');
const isMobile = width < 768;

// Demo mode - no auth required
const DEMO_TOKEN = 'demo';

export default function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showSidebar, setShowSidebar] = useState(!isMobile);
  const flatListRef = useRef<FlatList>(null);

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

  // Save current conversation ID
  useEffect(() => {
    saveCurrentConversationId(currentConversation?.id || null);
  }, [currentConversation]);

  async function loadData() {
    const saved = await loadConversations();
    const currentId = await loadCurrentConversationId();

    if (saved.length > 0) {
      setConversations(saved);
      const current = currentId ? saved.find(c => c.id === currentId) : saved[0];
      setCurrentConversation(current || saved[0]);
    }
  }

  function startNewChat() {
    setCurrentConversation(null);
    if (isMobile) setShowSidebar(false);
  }

  function selectConversation(id: string) {
    const conv = conversations.find(c => c.id === id);
    if (conv) {
      setCurrentConversation(conv);
      if (isMobile) setShowSidebar(false);
    }
  }

  async function sendMessage(text: string) {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };

    // Create or update conversation
    let conv = currentConversation;
    if (!conv) {
      conv = {
        id: generateId(),
        title: generateTitle(text),
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
      // Use demo token for now, or fetch from storage if auth implemented
      const result = await queryBandit(text, 'demo');

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
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />

      {/* Sidebar */}
      {showSidebar && (
        <View style={[styles.sidebar, isMobile && styles.sidebarMobile]}>
          <Sidebar
            conversations={conversations}
            currentId={currentConversation?.id || null}
            onSelect={selectConversation}
            onNewChat={startNewChat}
            onClose={() => setShowSidebar(false)}
          />
        </View>
      )}

      {/* Main chat area */}
      <KeyboardAvoidingView
        style={styles.main}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.menuButton}
            onPress={() => setShowSidebar(!showSidebar)}
          >
            <Ionicons name="menu" size={24} color={theme.colors.text} />
          </TouchableOpacity>

          <View style={styles.headerTitle}>
            <Text style={styles.headerTitleText}>Bandit</Text>
            <Text style={styles.headerSubtitle}>HQ Operator</Text>
          </View>

          <TouchableOpacity
            style={styles.newButton}
            onPress={startNewChat}
          >
            <Ionicons name="create-outline" size={24} color={theme.colors.text} />
          </TouchableOpacity>
        </View>

        {/* Messages or welcome screen */}
        {messages.length === 0 && !isLoading ? (
          <View style={styles.welcome}>
            <View style={styles.welcomeLogo}>
              <Text style={styles.welcomeLogoText}>B</Text>
            </View>
            <Text style={styles.welcomeTitle}>How can I help you today?</Text>
            <Text style={styles.welcomeSubtitle}>
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
                  style={styles.suggestionChip}
                  onPress={() => sendMessage(suggestion)}
                >
                  <Text style={styles.suggestionText}>{suggestion}</Text>
                  <Ionicons name="arrow-forward" size={16} color={theme.colors.textMuted} />
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ) : (
          <FlatList
            ref={flatListRef}
            data={messages}
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
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}



const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: theme.colors.background,
  },
  sidebar: {
    width: 260,
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
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  menuButton: {
    padding: theme.spacing.sm,
  },
  headerTitle: {
    flex: 1,
    alignItems: 'center',
  },
  headerTitleText: {
    color: theme.colors.primary,
    fontSize: theme.fontSize.lg,
    fontWeight: '700',
  },
  headerSubtitle: {
    color: theme.colors.textMuted,
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
    backgroundColor: theme.colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: theme.spacing.lg,
  },
  welcomeLogoText: {
    color: theme.colors.text,
    fontSize: 32,
    fontWeight: '700',
  },
  welcomeTitle: {
    color: theme.colors.text,
    fontSize: theme.fontSize.xl,
    fontWeight: '600',
    marginBottom: theme.spacing.sm,
  },
  welcomeSubtitle: {
    color: theme.colors.textMuted,
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
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.sm,
  },
  suggestionText: {
    color: theme.colors.text,
    fontSize: theme.fontSize.sm,
    flex: 1,
  },
  messageList: {
    paddingVertical: theme.spacing.sm,
  },
});
