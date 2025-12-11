// Bandit Mobile - Theme (ChatGPT/Claude inspired dark theme)

export const theme = {
    colors: {
        // Background layers
        background: '#0D0D0D',      // Main background (ChatGPT-like)
        surface: '#171717',          // Card/sidebar background
        surfaceLight: '#212121',     // Input fields, hover states

        // Accents
        primary: '#E040FB',          // Magenta (Bandit brand)
        primaryMuted: '#B030C8',     // Muted magenta
        accent: '#00D4AA',           // Teal accent

        // Text
        text: '#ECECEC',             // Primary text
        textMuted: '#8E8E8E',        // Secondary text
        textDim: '#6E6E6E',          // Tertiary text

        // Messages
        userBubble: '#2A2A2A',       // User message background
        banditBubble: '#0D0D0D',     // Bandit message (same as bg)

        // UI elements
        border: '#2A2A2A',
        borderLight: '#3A3A3A',
        error: '#FF5252',
        success: '#4CAF50',
        warning: '#FFB300',

        // Special
        thinking: '#E040FB',         // Thinking indicator
        code: '#1E1E2E',             // Code block background
    },

    spacing: {
        xs: 4,
        sm: 8,
        md: 16,
        lg: 24,
        xl: 32,
    },

    borderRadius: {
        sm: 8,
        md: 12,
        lg: 16,
        xl: 24,
        full: 9999,
    },

    fontSize: {
        xs: 12,
        sm: 14,
        md: 16,
        lg: 18,
        xl: 24,
        xxl: 32,
    },
};

export type Theme = typeof theme;
