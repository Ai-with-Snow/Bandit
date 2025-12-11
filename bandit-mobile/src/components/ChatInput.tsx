// ChatInput component - message input bar like ChatGPT/Claude

import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../constants/theme';

interface ChatInputProps {
    onSend: (message: string) => void;
    isLoading: boolean;
    placeholder?: string;
}

export function ChatInput({ onSend, isLoading, placeholder = 'Message Bandit...' }: ChatInputProps) {
    const [text, setText] = useState('');

    const handleSend = () => {
        const trimmed = text.trim();
        if (trimmed && !isLoading) {
            onSend(trimmed);
            setText('');
        }
    };

    return (
        <View style={styles.container}>
            <View style={styles.inputContainer}>
                <TextInput
                    style={styles.input}
                    value={text}
                    onChangeText={setText}
                    placeholder={placeholder}
                    placeholderTextColor={theme.colors.textDim}
                    multiline
                    maxLength={4000}
                    editable={!isLoading}
                    onSubmitEditing={handleSend}
                    returnKeyType="send"
                />

                <TouchableOpacity
                    style={[styles.sendButton, (!text.trim() || isLoading) && styles.sendButtonDisabled]}
                    onPress={handleSend}
                    disabled={!text.trim() || isLoading}
                >
                    {isLoading ? (
                        <ActivityIndicator size="small" color={theme.colors.text} />
                    ) : (
                        <Ionicons
                            name="arrow-up"
                            size={20}
                            color={text.trim() ? theme.colors.background : theme.colors.textDim}
                        />
                    )}
                </TouchableOpacity>
            </View>

            <View style={styles.disclaimer}>
                {/* Optional disclaimer text like ChatGPT */}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        paddingHorizontal: theme.spacing.md,
        paddingVertical: theme.spacing.sm,
        paddingBottom: theme.spacing.lg,
        backgroundColor: theme.colors.background,
        borderTopWidth: 1,
        borderTopColor: theme.colors.border,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        backgroundColor: theme.colors.surfaceLight,
        borderRadius: theme.borderRadius.lg,
        borderWidth: 1,
        borderColor: theme.colors.border,
        paddingHorizontal: theme.spacing.md,
        paddingVertical: theme.spacing.sm,
    },
    input: {
        flex: 1,
        color: theme.colors.text,
        fontSize: theme.fontSize.md,
        maxHeight: 120,
        paddingVertical: theme.spacing.xs,
    },
    sendButton: {
        width: 32,
        height: 32,
        borderRadius: theme.borderRadius.full,
        backgroundColor: theme.colors.primary,
        alignItems: 'center',
        justifyContent: 'center',
        marginLeft: theme.spacing.sm,
    },
    sendButtonDisabled: {
        backgroundColor: theme.colors.border,
    },
    disclaimer: {
        marginTop: theme.spacing.xs,
        alignItems: 'center',
    },
});
