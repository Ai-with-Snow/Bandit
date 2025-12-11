import { Platform } from 'react-native';

const PROXY_URL = Platform.select({
    android: 'https://bandit-849984150802.us-central1.run.app/v1/chat/completions',
    ios: 'https://bandit-849984150802.us-central1.run.app/v1/chat/completions',
    web: 'https://bandit-849984150802.us-central1.run.app/v1/chat/completions',
    default: 'https://bandit-849984150802.us-central1.run.app/v1/chat/completions',
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
    timestamp: Date;
}

export interface Conversation {
    id: string;
    title: string;
    messages: Message[];
    createdAt: Date;
    updatedAt: Date;
}

export async function queryBandit(
    prompt: string,
    accessToken: string
): Promise<BanditResponse> {
    const startTime = Date.now();

    try {
        const response = await fetch(PROXY_URL as string, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: 'bandit-v1.0',
                messages: [
                    { role: 'user', content: prompt }
                ]
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
