import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Clipboard, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error, errorInfo: null };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        this.setState({
            error: error,
            errorInfo: errorInfo
        });
        console.error("ErrorBoundary caught an error", error, errorInfo);
    }

    resetError = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    }

    copyToClipboard = () => {
        if (this.state.error) {
            const text = `Error: ${this.state.error.toString()}\n\nStack: ${this.state.errorInfo?.componentStack}`;
            Clipboard.setString(text);
            alert('Error details copied to clipboard');
        }
    }

    render() {
        if (this.state.hasError) {
            return (
                <SafeAreaView style={styles.container}>
                    <View style={styles.content}>
                        <Ionicons name="warning-outline" size={64} color="#FF6B6B" style={styles.icon} />
                        <Text style={styles.title}>Something went wrong</Text>
                        <Text style={styles.subtitle}>
                            An error occurred in the application.
                        </Text>

                        <ScrollView style={styles.errorContainer}>
                            <Text style={styles.errorTitle}>Error:</Text>
                            <Text style={styles.errorText}>{this.state.error?.toString()}</Text>

                            <Text style={styles.stackTitle}>Stack Trace:</Text>
                            <Text style={styles.stackText}>
                                {this.state.errorInfo?.componentStack || "No stack trace available"}
                            </Text>
                        </ScrollView>

                        <View style={styles.buttonContainer}>
                            <TouchableOpacity style={styles.buttonSecondary} onPress={this.copyToClipboard}>
                                <Text style={styles.buttonTextSecondary}>Copy Details</Text>
                            </TouchableOpacity>
                            <TouchableOpacity style={styles.buttonPrimary} onPress={this.resetError}>
                                <Text style={styles.buttonTextPrimary}>Try Again</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </SafeAreaView>
            );
        }

        return this.props.children;
    }
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#1A1A1A',
    },
    content: {
        flex: 1,
        padding: 20,
        alignItems: 'center',
        justifyContent: 'center',
    },
    icon: {
        marginBottom: 20,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#FFF',
        marginBottom: 10,
    },
    subtitle: {
        fontSize: 16,
        color: '#AAA',
        marginBottom: 30,
        textAlign: 'center',
    },
    errorContainer: {
        width: '100%',
        maxHeight: 400,
        backgroundColor: '#333',
        padding: 15,
        borderRadius: 8,
        marginBottom: 20,
    },
    errorTitle: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#FF8888',
        marginBottom: 5,
    },
    errorText: {
        fontSize: 14,
        color: '#FFF',
        fontFamily: 'monospace',
        marginBottom: 15,
    },
    stackTitle: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#88AAFF',
        marginBottom: 5,
    },
    stackText: {
        fontSize: 12,
        color: '#DDD',
        fontFamily: 'monospace',
    },
    buttonContainer: {
        flexDirection: 'row',
        gap: 15,
        marginTop: 10
    },
    buttonPrimary: {
        backgroundColor: '#E0D7FE',
        paddingVertical: 12,
        paddingHorizontal: 24,
        borderRadius: 8,
    },
    buttonSecondary: {
        backgroundColor: '#444',
        paddingVertical: 12,
        paddingHorizontal: 24,
        borderRadius: 8,
    },
    buttonTextPrimary: {
        color: '#1A1A1A',
        fontWeight: '600',
        fontSize: 16,
    },
    buttonTextSecondary: {
        color: '#FFF',
        fontWeight: '600',
        fontSize: 16,
    }
});
