// ChatBubble component - displays messages like ChatGPT/Claude

import React from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';
import { theme } from '../constants/theme';
import { Message } from '../lib/api';

interface ChatBubbleProps {
    message: Message;
}

export function ChatBubble({ message }: ChatBubbleProps) {
    const isUser = message.role === 'user';

    return (
        <View className={`px-8 py-4 ${isUser ? 'items-end' : 'items-start'}`}>
            <View className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
                {/* Label */}
                {!isUser && (
                    <Text className="text-sm font-semibold text-brand-text mb-2">
                        Somatic Healer
                    </Text>
                )}

                {/* Bubble */}
                <View className={`rounded-3xl px-6 py-4 shadow-lg ${isUser
                    ? 'bg-white/70'
                    : 'bg-[#D4C5F9]/60'
                    }`} style={{
                        shadowColor: '#000',
                        shadowOffset: { width: 0, height: 2 },
                        shadowOpacity: 0.1,
                        shadowRadius: 8,
                    }}>
                    {message.attachments && message.attachments.length > 0 && (
                        <View className="flex-row flex-wrap gap-2 mb-3">
                            {message.attachments.map((att, index) => (
                                att.type === 'image' ? (
                                    <Image
                                        key={index}
                                        source={{ uri: att.uri }}
                                        className="w-48 h-48 rounded-2xl"
                                        resizeMode="cover"
                                    />
                                ) : (
                                    <View key={index} className="p-3 bg-white/30 rounded-2xl">
                                        <Text className="text-brand-text text-sm">{att.name || 'File'}</Text>
                                    </View>
                                )
                            ))}
                        </View>
                    )}
                    <Text className="text-brand-text text-base leading-7">
                        {message.content}
                    </Text>
                </View>

                {/* Timestamp */}
                <Text className="text-xs text-brand-text-timestamp mt-2 mx-2">
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
