import { Platform } from 'react-native';

const PROXY_URL = Platform.select({
    android: 'http://192.168.1.122:8000/v1/chat/completions', // Physical device - use local network IP
    ios: 'http://localhost:8000/v1/chat/completions',
    web: 'http://localhost:8000/v1/chat/completions',
    default: 'http://localhost:8000/v1/chat/completions',
});

export interface BanditResponse {
    success: boolean;
    response?: string;
    error?: string;
    duration?: number;
}

export interface Message {
    id: string;
    role: 'user' | 'bandit';
    content: string;
    attachments?: { type: 'image' | 'file', uri: string, name?: string, base64?: string }[];
    timestamp: Date;
}

export interface Project {
    id: string;
    name: string;
    description?: string;
    color?: string;
    icon?: string;
    createdAt: Date;
}

export interface Conversation {
    id: string;
    title: string;
    messages: Message[];
    projectId?: string; // Link to a project
    createdAt: Date;
    updatedAt: Date;
}

export type ThinkingMode = 'auto' | 'instant' | 'thinking';

export async function queryBandit(
    prompt: string,
    accessToken: string,
    thinkingMode: ThinkingMode = 'instant',
    attachments: { type: 'image' | 'file', base64: string }[] = [],
    webSearch: boolean = false
): Promise<BanditResponse> {
    const startTime = Date.now();

    try {
        const response = await fetch(PROXY_URL as string, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                model: 'bandit-v1.0',
                messages: [
                    { role: 'user', content: prompt } // Proxy will handle multimodal if content is complex, or we add attachments here
                ],
                thinking_mode: thinkingMode,
                attachments: attachments, // Pass to proxy
                web_search: webSearch     // Pass to proxy
            }),
        });

        const duration = (Date.now() - startTime) / 1000;

        if (!response.ok) {
            const errorText = await response.text();
            return {
                success: false,
                error: `HTTP ${response.status}: ${errorText.slice(0, 200)}`,
                duration,
            };
        }

        const result = await response.json();
        const content = result.choices?.[0]?.message?.content || "No response content";

        return {
            success: true,
            response: content,
            duration,
        };
    } catch (error) {
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error',
            duration: (Date.now() - startTime) / 1000,
        };
    }
}

export function generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export function generateTitle(firstMessage: string): string {
    const cleaned = firstMessage.trim();
    if (cleaned.length <= 40) return cleaned;
    return cleaned.slice(0, 40) + '...';
}
