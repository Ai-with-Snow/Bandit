// ThinkingIndicator - animated dots like ChatGPT/Claude

import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { theme } from '../constants/theme';

export function ThinkingIndicator() {
    const [step, setStep] = React.useState(0);
    const steps = [
        "Analyzing query parameters...",
        "Routing to Neural Link...",
        "Consulting Model [Gemini 2.5 Pro]...",
        "Simulating reasoning paths...",
        "Synthesizing response...",
        "Finalizing output..."
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setStep((prev) => (prev + 1) % steps.length);
        }, 800); // Fast updates like a terminal
        return () => clearInterval(interval);
    }, []);

    return (
        <View style={styles.container}>
            <View style={styles.contentContainer}>
                <Text style={styles.roleText}>BANDIT // SYSTEMS</Text>
                <Text style={styles.thinkingText}>
                    {steps[step]} <Text style={styles.cursor}>_</Text>
                </Text>
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
        borderLeftWidth: 2,
        borderLeftColor: theme.colors.primary,
        marginLeft: theme.spacing.lg,
        backgroundColor: 'rgba(0, 0, 0, 0.02)',
    },
    avatarContainer: {
        marginRight: theme.spacing.md,
        display: 'none', // Hide avatar for thinking block
    },
    contentContainer: {
        flex: 1,
    },
    roleText: {
        color: theme.colors.primary,
        fontSize: theme.fontSize.xs,
        fontWeight: '700',
        marginBottom: 4,
        textTransform: 'uppercase',
        letterSpacing: 0.5,
    },
    thinkingText: {
        color: theme.colors.textDim,
        fontSize: theme.fontSize.sm,
        fontFamily: 'monospace', // Monospace for terminal feel
    },
    cursor: {
        color: theme.colors.primary,
        fontWeight: 'bold',
    }
});
