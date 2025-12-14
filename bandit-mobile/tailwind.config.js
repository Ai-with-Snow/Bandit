/** @type {import('tailwindcss').Config} */
module.exports = {
    presets: [require("nativewind/preset")],
    content: [
        "./App.{js,jsx,ts,tsx}",
        "./src/**/*.{js,jsx,ts,tsx}"
    ],
    theme: {
        extend: {
            colors: {
                'brand-purple': '#E0D7FE',
                'brand-text': '#3D3D3D',
                'brand-text-light': '#5E5E5E',
                'brand-text-timestamp': '#A0A0A0',
                'glass-border': 'rgba(255, 255, 255, 0.3)',
                'healer-bubble': 'rgba(224, 215, 254, 0.5)',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'], // In RN, this needs custom font loading or system font
            },
        },
    },
    plugins: [],
}
