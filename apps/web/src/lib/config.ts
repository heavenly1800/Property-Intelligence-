export type PublicConfig = {
  apiUrl: string;
  supabaseUrl: string;
  supabaseAnonKey: string;
};

export function readPublicConfig(): { config: PublicConfig | null; errors: string[] } {
  const values = {
    apiUrl: import.meta.env.VITE_API_URL as string | undefined,
    supabaseUrl: import.meta.env.VITE_SUPABASE_URL as string | undefined,
    supabaseAnonKey: import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined,
  };
  const errors = Object.entries(values)
    .filter(([, value]) => !value?.trim())
    .map(([name]) => `${name} is not configured.`);
  return { config: errors.length ? null : values as PublicConfig, errors };
}

export const publicConfig = readPublicConfig().config;
