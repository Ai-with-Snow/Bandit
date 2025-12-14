// Local storage helpers for conversations

import AsyncStorage from '@react-native-async-storage/async-storage';
import { Conversation, Message, Project } from './api';

const CONVERSATIONS_KEY = '@bandit_conversations';
const CURRENT_CONVERSATION_KEY = '@bandit_current';
const PROJECTS_KEY = '@bandit_projects';

/**
 * Save all projects to storage
 */
export async function saveProjects(projects: Project[]): Promise<void> {
    try {
        await AsyncStorage.setItem(PROJECTS_KEY, JSON.stringify(projects));
    } catch (error) {
        console.error('Failed to save projects:', error);
    }
}

/**
 * Load all projects from storage
 */
export async function loadProjects(): Promise<Project[]> {
    try {
        const data = await AsyncStorage.getItem(PROJECTS_KEY);
        if (!data) return [];

        const parsed = JSON.parse(data);
        return parsed.map((proj: any) => ({
            ...proj,
            createdAt: new Date(proj.createdAt),
        }));
    } catch (error) {
        console.error('Failed to load projects:', error);
        return [];
    }
}

/**
 * Save all conversations to storage
 */
export async function saveConversations(conversations: Conversation[]): Promise<void> {
    try {
        await AsyncStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations));
    } catch (error) {
        console.error('Failed to save conversations:', error);
    }
}

/**
 * Load all conversations from storage
 */
export async function loadConversations(): Promise<Conversation[]> {
    try {
        const data = await AsyncStorage.getItem(CONVERSATIONS_KEY);
        if (!data) return [];

        const parsed = JSON.parse(data);
        // Convert date strings back to Date objects
        return parsed.map((conv: any) => ({
            ...conv,
            createdAt: new Date(conv.createdAt),
            updatedAt: new Date(conv.updatedAt),
            messages: conv.messages.map((msg: any) => ({
                ...msg,
                timestamp: new Date(msg.timestamp),
            })),
        }));
    } catch (error) {
        console.error('Failed to load conversations:', error);
        return [];
    }
}

/**
 * Save current conversation ID
 */
export async function saveCurrentConversationId(id: string | null): Promise<void> {
    try {
        if (id) {
            await AsyncStorage.setItem(CURRENT_CONVERSATION_KEY, id);
        } else {
            await AsyncStorage.removeItem(CURRENT_CONVERSATION_KEY);
        }
    } catch (error) {
        console.error('Failed to save current conversation:', error);
    }
}

/**
 * Load current conversation ID
 */
export async function loadCurrentConversationId(): Promise<string | null> {
    try {
        return await AsyncStorage.getItem(CURRENT_CONVERSATION_KEY);
    } catch (error) {
        console.error('Failed to load current conversation:', error);
        return null;
    }
}

/**
 * Clear all data
 */
export async function clearAllData(): Promise<void> {
    try {
        await AsyncStorage.multiRemove([CONVERSATIONS_KEY, CURRENT_CONVERSATION_KEY]);
    } catch (error) {
        console.error('Failed to clear data:', error);
    }
}
