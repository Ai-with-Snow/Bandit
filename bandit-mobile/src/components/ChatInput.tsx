// ChatInput component - message input bar like ChatGPT/Claude

import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Text, Image, Alert, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../constants/theme';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';

interface Attachment {
    type: 'image' | 'file';
    uri: string;
    name: string;
    base64?: string;
    mimeType?: string;
}

interface ChatInputProps {
    onSend: (message: string, options: { webSearch: boolean, attachments: Attachment[] }) => void;
    isLoading: boolean;
    placeholder?: string;
    thinkingMode: 'auto' | 'instant' | 'thinking';
    onSetThinkingMode: (mode: 'auto' | 'instant' | 'thinking') => void;
}

export function ChatInput({ onSend, isLoading, placeholder = 'Message Bandit...', thinkingMode, onSetThinkingMode }: ChatInputProps) {
    const [message, setMessage] = useState('');
    const [showModeSelector, setShowModeSelector] = useState(false);
    const [showAttachMenu, setShowAttachMenu] = useState(false);
    const [webSearch, setWebSearch] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [attachments, setAttachments] = useState<Attachment[]>([]);

    const handleSend = () => {
        if ((!message.trim() && attachments.length === 0) || isLoading) return;
        onSend(message, { webSearch, attachments });
        setMessage('');
        setAttachments([]);
    };

    const MAX_ATTACHMENTS = 10;

    const pickImage = async () => {
        setShowAttachMenu(false);

        if (attachments.length >= MAX_ATTACHMENTS) {
            Alert.alert('Limit reached', `You can attach up to ${MAX_ATTACHMENTS} files.`);
            return;
        }

        // For web, use a file input with multiple selection
        if (Platform.OS === 'web') {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.multiple = true;
            input.onchange = async (e: any) => {
                const files = Array.from(e.target.files || []) as File[];
                const remaining = MAX_ATTACHMENTS - attachments.length;
                const toProcess = files.slice(0, remaining);

                for (const file of toProcess) {
                    const uri = URL.createObjectURL(file);
                    const reader = new FileReader();
                    reader.onload = () => {
                        const base64 = (reader.result as string).split(',')[1];
                        setAttachments(prev => {
                            if (prev.length >= MAX_ATTACHMENTS) return prev;
                            return [...prev, {
                                type: 'image',
                                uri,
                                name: file.name,
                                base64,
                                mimeType: file.type,
                            }];
                        });
                    };
                    reader.readAsDataURL(file);
                }
            };
            input.click();
            return;
        }

        // For native, use ImagePicker
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (status !== 'granted') {
            Alert.alert('Permission needed', 'Please allow access to your photo library to attach images.');
            return;
        }

        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: false,
            quality: 0.8,
            base64: true,
        });

        if (!result.canceled && result.assets[0]) {
            const asset = result.assets[0];
            const fileName = asset.uri.split('/').pop() || 'image.jpg';
            setAttachments(prev => [...prev, {
                type: 'image',
                uri: asset.uri,
                name: fileName,
                base64: asset.base64 ?? undefined,
                mimeType: asset.mimeType || 'image/jpeg',
            }]);
        }
    };

    const pickDocument = async () => {
        setShowAttachMenu(false);

        if (attachments.length >= MAX_ATTACHMENTS) {
            Alert.alert('Limit reached', `You can attach up to ${MAX_ATTACHMENTS} files.`);
            return;
        }

        // For web, use a file input with multiple selection
        if (Platform.OS === 'web') {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '*/*';
            input.multiple = true;
            input.onchange = async (e: any) => {
                const files = Array.from(e.target.files || []) as File[];
                const remaining = MAX_ATTACHMENTS - attachments.length;
                const toProcess = files.slice(0, remaining);

                for (const file of toProcess) {
                    const uri = URL.createObjectURL(file);
                    setAttachments(prev => {
                        if (prev.length >= MAX_ATTACHMENTS) return prev;
                        return [...prev, {
                            type: 'file',
                            uri,
                            name: file.name,
                            mimeType: file.type,
                        }];
                    });
                }
            };
            input.click();
            return;
        }

        // For native, use DocumentPicker
        try {
            const result = await DocumentPicker.getDocumentAsync({
                type: '*/*',
                copyToCacheDirectory: true,
            });

            if (!result.canceled && result.assets[0]) {
                const asset = result.assets[0];
                setAttachments(prev => [...prev, {
                    type: 'file',
                    uri: asset.uri,
                    name: asset.name,
                    mimeType: asset.mimeType,
                }]);
            }
        } catch (err) {
            console.error('Document picker error:', err);
        }
    };

    const removeAttachment = (index: number) => {
        setAttachments(prev => prev.filter((_, i) => i !== index));
    };

    const canSend = message.trim() || attachments.length > 0;

    return (
        <View className="px-8 py-6 bg-transparent">
            {/* Attachment Previews */}
            {attachments.length > 0 && (
                <View className="flex-row flex-wrap mb-3 gap-2">
                    {attachments.map((att, index) => (
                        <View key={index} className="relative">
                            {att.type === 'image' ? (
                                <Image
                                    source={{ uri: att.uri }}
                                    style={{ width: 60, height: 60, borderRadius: 8 }}
                                />
                            ) : (
                                <View className="w-16 h-16 bg-white/60 rounded-lg items-center justify-center border border-white/80">
                                    <Ionicons name="document-outline" size={24} color="#5E5E5E" />
                                    <Text className="text-xs text-gray-500 mt-1" numberOfLines={1}>
                                        {att.name.slice(0, 8)}
                                    </Text>
                                </View>
                            )}
                            <TouchableOpacity
                                className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 rounded-full items-center justify-center"
                                onPress={() => removeAttachment(index)}
                            >
                                <Ionicons name="close" size={12} color="#fff" />
                            </TouchableOpacity>
                        </View>
                    ))}
                </View>
            )}

            <View className="flex-row items-center bg-white/60 rounded-full border border-white/80 px-6 py-4 shadow-md" style={{
                shadowColor: '#000',
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: 0.08,
                shadowRadius: 12,
            }}>
                <TextInput
                    className="text-brand-text text-base flex-1 py-0"
                    placeholder={placeholder}
                    placeholderTextColor="#9CA3AF"
                    value={message}
                    onChangeText={setMessage}
                />

                <View className="flex-row items-center gap-2 ml-2">
                    <TouchableOpacity
                        className="p-2"
                        onPress={() => setShowAttachMenu(!showAttachMenu)}
                    >
                        <Ionicons name="attach-outline" size={22} color={attachments.length > 0 ? "#D4C5F9" : "#9CA3AF"} />
                    </TouchableOpacity>
                    <TouchableOpacity
                        className="p-2"
                        onPress={() => {/* TODO: Implement emoji picker */ }}
                    >
                        <Ionicons name="happy-outline" size={22} color="#9CA3AF" />
                    </TouchableOpacity>
                    <TouchableOpacity
                        className={`w-10 h-10 rounded-full items-center justify-center ml-1 ${canSend ? 'bg-[#D4C5F9]' : 'bg-gray-300'}`}
                        onPress={handleSend}
                        disabled={!canSend || isLoading}
                    >
                        {isLoading ? (
                            <ActivityIndicator size="small" color="#fff" />
                        ) : (
                            <Ionicons name="send" size={18} color="#fff" />
                        )}
                    </TouchableOpacity>
                </View>
            </View>

            {/* Attach Menu */}
            {showAttachMenu && (
                <View className="absolute bottom-24 left-8 bg-white/95 p-2 rounded-2xl shadow-lg" style={{
                    shadowColor: '#000',
                    shadowOffset: { width: 0, height: 4 },
                    shadowOpacity: 0.15,
                    shadowRadius: 12,
                    zIndex: 100,
                }}>
                    <TouchableOpacity
                        className="flex-row items-center p-3 rounded-xl"
                        onPress={pickImage}
                    >
                        <Ionicons name="image-outline" size={22} color="#3D3D3D" />
                        <Text className="ml-3 text-sm text-gray-700">Photo</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        className="flex-row items-center p-3 rounded-xl"
                        onPress={pickDocument}
                    >
                        <Ionicons name="document-outline" size={22} color="#3D3D3D" />
                        <Text className="ml-3 text-sm text-gray-700">File</Text>
                    </TouchableOpacity>
                </View>
            )}

            {showModeSelector && (
                <View className="absolute bottom-20 right-6 bg-white/90 p-2 rounded-2xl shadow-lg w-40" style={{
                    shadowColor: '#000',
                    shadowOffset: { width: 0, height: 4 },
                    shadowOpacity: 0.15,
                    shadowRadius: 12,
                }}>
                    {['auto', 'instant', 'thinking'].map((mode) => (
                        <TouchableOpacity
                            key={mode}
                            className={`p-3 rounded-xl ${thinkingMode === mode ? 'bg-[#D4C5F9]/40' : ''}`}
                            onPress={() => {
                                onSetThinkingMode(mode as any);
                                setShowModeSelector(false);
                            }}
                        >
                            <Text className={`text-sm capitalize ${thinkingMode === mode ? 'text-brand-text font-semibold' : 'text-brand-text-light'}`}>
                                {mode}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </View>
            )}

            <View className="items-center mt-3">
                <Text className="text-xs text-brand-text-light/60">Bandit can make mistakes. Check important info.</Text>
            </View>
        </View>
    );
}
