// ChatBubble component - displays messages like ChatGPT/Claude

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../constants/theme';
import { Message } from '../lib/api';

interface ChatBubbleProps {
    message: Message;
}

export function ChatBubble({ message }: ChatBubbleProps) {
    const isUser = message.role === 'user';

    return (
        <View style={[styles.container, isUser && styles.userContainer]}>
            <View style={styles.avatarContainer}>
                <View style={[styles.avatar, isUser ? styles.userAvatar : styles.banditAvatar]}>
                    <Text style={styles.avatarText}>
                        {isUser ? 'U' : 'B'}
                    </Text>
                </View>
            </View>

            <View style={styles.contentContainer}>
                <Text style={[styles.roleText, isUser && styles.userRoleText]}>
                    {isUser ? 'You' : 'Bandit'}
                </Text>
                <View style={[styles.bubble, isUser ? styles.userBubble : styles.banditBubble]}>
                    <Text style={styles.messageText}>{message.content}</Text>
                </View>
                <Text style={styles.timestamp}>
                    {formatTimestamp(message.timestamp)}
                </Text>
            </View>
        </View>
    );
}

function formatTimestamp(date: Date): string {
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;

    return date.toLocaleDateString();
}

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        paddingHorizontal: theme.spacing.md,
        paddingVertical: theme.spacing.sm,
        marginVertical: theme.spacing.xs,
    },
    userContainer: {
        backgroundColor: theme.colors.surfaceLight,
    },
    avatarContainer: {
        marginRight: theme.spacing.md,
    },
    avatar: {
        width: 32,
        height: 32,
        borderRadius: theme.borderRadius.sm,
        alignItems: 'center',
        justifyContent: 'center',
    },
    userAvatar: {
        backgroundColor: theme.colors.accent,
    },
    banditAvatar: {
        backgroundColor: theme.colors.primary,
    },
    avatarText: {
        color: theme.colors.text,
        fontSize: theme.fontSize.sm,
        fontWeight: '600',
    },
    contentContainer: {
        flex: 1,
    },
    roleText: {
        color: theme.colors.text,
        fontSize: theme.fontSize.sm,
        fontWeight: '600',
        marginBottom: theme.spacing.xs,
    },
    userRoleText: {
        color: theme.colors.accent,
    },
    bubble: {
        borderRadius: theme.borderRadius.md,
        paddingHorizontal: theme.spacing.md,
        paddingVertical: theme.spacing.sm,
    },
    userBubble: {
        backgroundColor: 'transparent',
    },
    banditBubble: {
        backgroundColor: 'transparent',
    },
    messageText: {
        color: theme.colors.text,
        fontSize: theme.fontSize.md,
        lineHeight: 24,
    },
    timestamp: {
        color: theme.colors.textDim,
        fontSize: theme.fontSize.xs,
        marginTop: theme.spacing.xs,
    },
});
