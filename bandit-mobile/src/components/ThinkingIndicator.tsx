// ThinkingIndicator - animated dots like ChatGPT/Claude

import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { theme } from '../constants/theme';

export function ThinkingIndicator() {
    const dots = [useRef(new Animated.Value(0)).current, useRef(new Animated.Value(0)).current, useRef(new Animated.Value(0)).current];

    useEffect(() => {
        const animations = dots.map((dot, index) => {
            return Animated.loop(
                Animated.sequence([
                    Animated.delay(index * 200),
                    Animated.timing(dot, {
                        toValue: 1,
                        duration: 400,
                        useNativeDriver: true,
                    }),
                    Animated.timing(dot, {
                        toValue: 0,
                        duration: 400,
                        useNativeDriver: true,
                    }),
                ])
            );
        });

        animations.forEach(anim => anim.start());

        return () => {
            animations.forEach(anim => anim.stop());
        };
    }, []);

    return (
        <View style={styles.container}>
            <View style={styles.avatarContainer}>
                <View style={styles.avatar}>
                    <Text style={styles.avatarText}>B</Text>
                </View>
            </View>

            <View style={styles.contentContainer}>
                <Text style={styles.roleText}>Bandit</Text>
                <View style={styles.dotsContainer}>
                    {dots.map((dot, index) => (
                        <Animated.View
                            key={index}
                            style={[
                                styles.dot,
                                {
                                    opacity: dot.interpolate({
                                        inputRange: [0, 1],
                                        outputRange: [0.3, 1],
                                    }),
                                    transform: [
                                        {
                                            scale: dot.interpolate({
                                                inputRange: [0, 1],
                                                outputRange: [0.8, 1.2],
                                            }),
                                        },
                                    ],
                                },
                            ]}
                        />
                    ))}
                </View>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        paddingHorizontal: theme.spacing.md,
        paddingVertical: theme.spacing.sm,
        marginVertical: theme.spacing.xs,
    },
    avatarContainer: {
        marginRight: theme.spacing.md,
    },
    avatar: {
        width: 32,
        height: 32,
        borderRadius: theme.borderRadius.sm,
        backgroundColor: theme.colors.primary,
        alignItems: 'center',
        justifyContent: 'center',
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
    dotsContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        height: 24,
    },
    dot: {
        width: 8,
        height: 8,
        borderRadius: 4,
        backgroundColor: theme.colors.primary,
        marginRight: 6,
    },
});
