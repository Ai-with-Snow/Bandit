// Sidebar component - conversation history like ChatGPT

import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../constants/theme';
import { Conversation } from '../lib/api';

interface SidebarProps {
    conversations: Conversation[];
    currentId: string | null;
    onSelect: (id: string) => void;
    onNewChat: () => void;
    onClose: () => void;
}

export function Sidebar({ conversations, currentId, onSelect, onNewChat, onClose }: SidebarProps) {
    // Group by date
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const grouped = {
        today: conversations.filter(c => isSameDay(c.updatedAt, today)),
        yesterday: conversations.filter(c => isSameDay(c.updatedAt, yesterday)),
        older: conversations.filter(c => !isSameDay(c.updatedAt, today) && !isSameDay(c.updatedAt, yesterday)),
    };

    return (
        <View style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <TouchableOpacity style={styles.newChatButton} onPress={onNewChat}>
                    <Ionicons name="add" size={20} color={theme.colors.text} />
                    <Text style={styles.newChatText}>New chat</Text>
                </TouchableOpacity>

                <TouchableOpacity onPress={onClose} style={styles.closeButton}>
                    <Ionicons name="close" size={24} color={theme.colors.text} />
                </TouchableOpacity>
            </View>

            {/* Conversation list */}
            <ScrollView style={styles.list}>
                {grouped.today.length > 0 && (
                    <View style={styles.group}>
                        <Text style={styles.groupTitle}>Today</Text>
                        {grouped.today.map(conv => (
                            <ConversationItem
                                key={conv.id}
                                conversation={conv}
                                isActive={conv.id === currentId}
                                onPress={() => onSelect(conv.id)}
                            />
                        ))}
                    </View>
                )}

                {grouped.yesterday.length > 0 && (
                    <View style={styles.group}>
                        <Text style={styles.groupTitle}>Yesterday</Text>
                        {grouped.yesterday.map(conv => (
                            <ConversationItem
                                key={conv.id}
                                conversation={conv}
                                isActive={conv.id === currentId}
                                onPress={() => onSelect(conv.id)}
                            />
                        ))}
                    </View>
                )}

                {grouped.older.length > 0 && (
                    <View style={styles.group}>
                        <Text style={styles.groupTitle}>Previous</Text>
                        {grouped.older.map(conv => (
                            <ConversationItem
                                key={conv.id}
                                conversation={conv}
                                isActive={conv.id === currentId}
                                onPress={() => onSelect(conv.id)}
                            />
                        ))}
                    </View>
                )}

                {conversations.length === 0 && (
                    <View style={styles.empty}>
                        <Text style={styles.emptyText}>No conversations yet</Text>
                    </View>
                )}
            </ScrollView>

            {/* Footer */}
            <View style={styles.footer}>
                <View style={styles.brand}>
                    <Text style={styles.brandText}>Bandit HQ</Text>
                    <Text style={styles.versionText}>v1.0.0</Text>
                </View>
            </View>
        </View>
    );
}

function ConversationItem({ conversation, isActive, onPress }: {
    conversation: Conversation;
    isActive: boolean;
    onPress: () => void;
}) {
    return (
        <TouchableOpacity
            style={[styles.item, isActive && styles.itemActive]}
            onPress={onPress}
        >
            <Ionicons name="chatbubble-outline" size={16} color={theme.colors.textMuted} />
            <Text style={styles.itemText} numberOfLines={1}>
                {conversation.title}
            </Text>
        </TouchableOpacity>
    );
}

function isSameDay(d1: Date, d2: Date): boolean {
    return d1.toDateString() === d2.toDateString();
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: theme.colors.surface,
        borderRightWidth: 1,
        borderRightColor: theme.colors.border,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: theme.spacing.md,
        borderBottomWidth: 1,
        borderBottomColor: theme.colors.border,
    },
    newChatButton: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: theme.colors.surfaceLight,
        paddingHorizontal: theme.spacing.md,
        paddingVertical: theme.spacing.sm,
        borderRadius: theme.borderRadius.md,
        flex: 1,
        marginRight: theme.spacing.sm,
    },
    newChatText: {
        color: theme.colors.text,
        marginLeft: theme.spacing.sm,
        fontSize: theme.fontSize.sm,
    },
    closeButton: {
        padding: theme.spacing.xs,
    },
    list: {
        flex: 1,
    },
    group: {
        paddingVertical: theme.spacing.sm,
    },
    groupTitle: {
        color: theme.colors.textDim,
        fontSize: theme.fontSize.xs,
        fontWeight: '600',
        paddingHorizontal: theme.spacing.md,
        paddingVertical: theme.spacing.xs,
        textTransform: 'uppercase',
    },
    item: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: theme.spacing.md,
        paddingVertical: theme.spacing.sm,
        marginHorizontal: theme.spacing.sm,
        borderRadius: theme.borderRadius.sm,
    },
    itemActive: {
        backgroundColor: theme.colors.surfaceLight,
    },
    itemText: {
        color: theme.colors.text,
        fontSize: theme.fontSize.sm,
        marginLeft: theme.spacing.sm,
        flex: 1,
    },
    empty: {
        padding: theme.spacing.lg,
        alignItems: 'center',
    },
    emptyText: {
        color: theme.colors.textDim,
        fontSize: theme.fontSize.sm,
    },
    footer: {
        padding: theme.spacing.md,
        borderTopWidth: 1,
        borderTopColor: theme.colors.border,
    },
    brand: {
        alignItems: 'center',
    },
    brandText: {
        color: theme.colors.primary,
        fontSize: theme.fontSize.sm,
        fontWeight: '600',
    },
    versionText: {
        color: theme.colors.textDim,
        fontSize: theme.fontSize.xs,
    },
});
