try {
    const { getDefaultConfig } = require("expo/metro-config");
    const { withNativeWind } = require("nativewind/metro");

    console.log("Imports successful");

    const config = getDefaultConfig(__dirname);
    console.log("got default config");

    const finalConfig = withNativeWind(config, { input: "./global.css" });
    console.log("withNativeWind success");

} catch (e) {
    console.error("Config Error:", e);
}
