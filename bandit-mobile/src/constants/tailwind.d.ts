declare module 'tailwindcss/resolveConfig' {
    import { Config } from 'tailwindcss';
    function resolveConfig(config: Config): Config;
    export = resolveConfig;
}
